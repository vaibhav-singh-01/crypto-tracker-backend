from app.core.providers import PROVIDERS
from fastapi import HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CryptoService:
    def __init__(self, provider_name: str = "coingecko"):
        self.provider = PROVIDERS[provider_name]()

    def get_price(self, crypto_id: str, vs_currency: str = "usd") -> float:
        return self.provider.get_price(crypto_id, vs_currency)

    def get_all_coins(self, vs_currency: str = "usd", limit: int = 100):
        return self.provider.get_all_coins(vs_currency, limit)
    
    def get_coins_by_ids(self, coin_ids: list, vs_currency: str = "usd"):
        return self.provider.get_coins_by_ids(coin_ids, vs_currency)

    def pin_crypto(self, crypto_id: str):
        if not crypto_id or not crypto_id.strip():
            raise HTTPException(status_code=400, detail="Crypto ID cannot be empty")
        
        # Validate crypto_id 
        try:
            self.get_price(crypto_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Crypto '{crypto_id}' not found")
        
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

    def get_pinned_cryptos(self):
        if not settings.PINNED_CRYPTOS:
            logger.info("No pinned cryptos found")
            return []
        
        logger.info(f"Getting data for {len(settings.PINNED_CRYPTOS)} pinned cryptos: {settings.PINNED_CRYPTOS}")
        
        # Fetch only the pinned coins directly using their IDs
        pinned_coins = self.get_coins_by_ids(settings.PINNED_CRYPTOS)
        
        logger.info(f"Successfully fetched {len(pinned_coins)} pinned coins")
        return pinned_coins