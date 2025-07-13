from app.core.providers import PROVIDERS
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import log as logger

class CryptoService:
    def __init__(self, provider_name: str = "coingecko"):
        self.provider = PROVIDERS[provider_name]()

    def get_price(self, crypto_id: str, vs_currency: str = "usd") -> float:
        return self.provider.get_price(crypto_id, vs_currency)

    def get_all_coins(self, vs_currency: str = "usd", limit: int = 100):
        coins = self.provider.get_all_coins(vs_currency, limit)
        
        # upd currency of each coin
        for coin in coins:
            coin['currency'] = vs_currency.lower()
            
        return coins
    
    def get_coins_by_ids(self, coin_ids: list, vs_currency: str = "usd"):
        coins = self.provider.get_coins_by_ids(coin_ids, vs_currency)
        
        # upd currency of each coin
        for coin in coins:
            coin['currency'] = vs_currency.lower()
            
        return coins

    def _is_coin_supported_for_pinning(self, crypto_id: str) -> bool:
        """Check if a coin is supported by the markets endpoint for pinning"""
        try:
            result = self.get_coins_by_ids([crypto_id])
            return len(result) > 0
        except Exception:
            return False

    def pin_crypto(self, crypto_id: str):
        if not crypto_id or not crypto_id.strip():
            raise HTTPException(status_code=400, detail="Crypto ID cannot be empty")
        
        # Validate same endpoint as pinned cryptos
        if not self._is_coin_supported_for_pinning(crypto_id):
            logger.warning(f"Pinning failed for {crypto_id} as it's unsupported")
            raise HTTPException(status_code=400, detail=f"Coin '{crypto_id}' is not supported for pinning")
        
        if crypto_id not in settings.PINNED_CRYPTOS:
            settings.PINNED_CRYPTOS.append(crypto_id)
            settings.save_pinned_cryptos()
            logger.info(f"Successfully pinned {crypto_id}")
        else:
            raise HTTPException(status_code=400, detail="Crypto already pinned")

    def unpin_crypto(self, crypto_id: str):
        if not crypto_id or not crypto_id.strip():
            raise HTTPException(status_code=400, detail="Crypto ID cannot be empty")
        
        if crypto_id in settings.PINNED_CRYPTOS:
            settings.PINNED_CRYPTOS.remove(crypto_id)
            settings.save_pinned_cryptos()
            logger.info(f"Successfully unpinned {crypto_id}")
        else:
            raise HTTPException(status_code=404, detail=f"Cannot unpin '{crypto_id}' because it is not currently pinned")

    def get_pinned_cryptos(self, vs_currency: str = "usd"):
        if not settings.PINNED_CRYPTOS:
            logger.info("No pinned cryptos found")
            return []
        
        logger.info(f"Getting data for {len(settings.PINNED_CRYPTOS)} pinned cryptos: {settings.PINNED_CRYPTOS}")
        
        # Fetch only the pinned coins directly using their IDs
        pinned_coins = self.get_coins_by_ids(settings.PINNED_CRYPTOS, vs_currency)
        
        logger.info(f"Successfully fetched {len(pinned_coins)} pinned coins")
        return pinned_coins