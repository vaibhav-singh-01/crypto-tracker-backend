from abc import ABC, abstractmethod
from app.core.config import settings
import requests
import time
from app.core.logging import log as logger
from typing import Dict, Any, Optional

# Custom exceptions 
class CryptoNotFoundError(Exception):
    pass

class CurrencyNotSupportedError(Exception):
    pass

class RateLimitError(Exception):
    pass

class APIServiceError(Exception):
    pass

class CryptoProvider(ABC):
    @abstractmethod
    def get_price(self, crypto_id: str, vs_currency: str = "usd") -> float:
        pass
    
    @abstractmethod
    def get_all_coins(self, vs_currency: str, limit: int) -> list:
        pass
    
    @abstractmethod
    def get_coins_by_ids(self, coin_ids: list, vs_currency: str = "usd") -> list:
        pass

class CoinGeckoProvider(CryptoProvider):
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_duration = settings.COINGECKO_CACHE_DURATION
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        
        cache_time = self._cache[cache_key].get('timestamp', 0)
        return time.time() - cache_time < self._cache_duration
    
    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get cached data if valid"""
        if self._is_cache_valid(cache_key):
            logger.info(f"Cache HIT for {cache_key}")
            return self._cache[cache_key]['data']
        logger.info(f"Cache MISS for {cache_key}")
        return None
    
    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Set data in cache with timestamp"""
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.info(f"Cached data for {cache_key}")

    def get_price(self, crypto_id: str, vs_currency: str = "usd") -> float:
        cache_key = f"price_{crypto_id}_{vs_currency}"
        
        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
        
        logger.info(f"Making CoinGecko API call for price: {crypto_id} in {vs_currency}")
        url = f"{settings.COINGECKO_API_URL}/simple/price"
        params = {
            "ids": crypto_id,
            "vs_currencies": vs_currency
        }
        
        if settings.COINGECKO_API_KEY:
            params["x_cg_demo_api_key"] = settings.COINGECKO_API_KEY

        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                logger.warning(f"Rate limit exceeded for CoinGecko API - crypto: {crypto_id}, currency: {vs_currency}")
                raise RateLimitError("API rate limit exceeded. Please try again later")
            elif response.status_code == 503:
                logger.warning(f"CoinGecko API service unavailable - crypto: {crypto_id}, currency: {vs_currency}")
                raise APIServiceError("Cryptocurrency data service is temporarily unavailable")
            
            response.raise_for_status()
            data = response.json()
            
            if crypto_id not in data:
                raise CryptoNotFoundError(f"Cryptocurrency '{crypto_id}' not found")
            
            if vs_currency not in data[crypto_id]:
                raise CurrencyNotSupportedError(f"Currency '{vs_currency}' is not supported")
            
            price = data[crypto_id][vs_currency]
            
            self._set_cache(cache_key, price)
            return price
        except (CryptoNotFoundError, CurrencyNotSupportedError, RateLimitError, APIServiceError):
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching price for {crypto_id} in {vs_currency}: {str(e)}")
            raise APIServiceError("Network error while fetching cryptocurrency data")
        except Exception as e:
            logger.error(f"Unexpected error fetching price for {crypto_id} in {vs_currency}: {str(e)}")
            raise APIServiceError("Unable to fetch cryptocurrency price")
    
    def get_all_coins(self, vs_currency: str = "usd", limit: int = 100) -> list:
        cache_key = f"all_coins_{vs_currency}_{limit}"
        
        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
        
        logger.info(f"Making CoinGecko API call for all coins: vs_currency={vs_currency}, limit={limit}")
        url = f"{settings.COINGECKO_API_URL}/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False
        }
        
        if settings.COINGECKO_API_KEY:
            params["x_cg_demo_api_key"] = settings.COINGECKO_API_KEY
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                logger.warning(f"Rate limit exceeded for CoinGecko API - fetching coins in {vs_currency}")
                raise RateLimitError("API rate limit exceeded. Please try again later")
            elif response.status_code == 503:
                logger.warning(f"CoinGecko API service unavailable - fetching coins in {vs_currency}")
                raise APIServiceError("Cryptocurrency data service is temporarily unavailable")
            
            response.raise_for_status()
            data = response.json()
            
            self._set_cache(cache_key, data)
            return data
        except (RateLimitError, APIServiceError):
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching coins for {vs_currency} with limit {limit}: {str(e)}")
            raise APIServiceError("Network error while fetching cryptocurrency data")
        except Exception as e:
            logger.error(f"Unexpected error fetching coins for {vs_currency} with limit {limit}: {str(e)}")
            raise APIServiceError("Unable to fetch cryptocurrency market data")
    
    def get_coins_by_ids(self, coin_ids: list, vs_currency: str = "usd") -> list:
        if not coin_ids:
            return []
        
        # cache key based on sorted coin_ids
        sorted_ids = sorted(coin_ids)
        cache_key = f"coins_by_ids_{','.join(sorted_ids)}_{vs_currency}"
        
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
        
        logger.info(f"Making CoinGecko API call for specific coins: {coin_ids} in {vs_currency}")
        url = f"{settings.COINGECKO_API_URL}/coins/markets"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "sparkline": False
        }
        
        if settings.COINGECKO_API_KEY:
            params["x_cg_demo_api_key"] = settings.COINGECKO_API_KEY
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                logger.warning(f"Rate limit exceeded for CoinGecko API - fetching specific coins: {coin_ids}")
                raise RateLimitError("API rate limit exceeded. Please try again later")
            elif response.status_code == 503:
                logger.warning(f"CoinGecko API service unavailable - fetching specific coins: {coin_ids}")
                raise APIServiceError("Cryptocurrency data service is temporarily unavailable")
            
            response.raise_for_status()
            data = response.json()
            
            self._set_cache(cache_key, data)
            return data
        except (RateLimitError, APIServiceError):
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching specific coins {coin_ids} for {vs_currency}: {str(e)}")
            raise APIServiceError("Network error while fetching cryptocurrency data")
        except Exception as e:
            logger.error(f"Unexpected error fetching specific coins {coin_ids} for {vs_currency}: {str(e)}")
            raise APIServiceError("Unable to fetch cryptocurrency market data")

PROVIDERS = {
    "coingecko": CoinGeckoProvider
}