from app.core.providers import PROVIDERS
from fastapi import HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CryptoService:
    def __init__(self, provider_name: str = "coingecko"):
        self.provider = PROVIDERS[provider_name]()

    def get_price(self, crypto_id: str) -> float:
        return self.provider.get_price(crypto_id)

    def get_all_coins(self, vs_currency: str = "usd", limit: int = 100):
        return self.provider.get_all_coins(vs_currency, limit)

    def pin_crypto(self, crypto_id: str):
        if crypto_id not in settings.PINNED_CRYPTOS:
            settings.PINNED_CRYPTOS.append(crypto_id)
            settings.save_pinned_cryptos()
            logger.info(f"Successfully pinned {crypto_id}")
        else:
            raise HTTPException(status_code=400, detail="Crypto already pinned")

    def unpin_crypto(self, crypto_id: str):
        if crypto_id in settings.PINNED_CRYPTOS:
            settings.PINNED_CRYPTOS.remove(crypto_id)
            settings.save_pinned_cryptos()
            logger.info(f"Successfully unpinned {crypto_id}")
        else:
            raise HTTPException(status_code=404, detail="Crypto not pinned")

    def get_pinned_cryptos(self):
        if not settings.PINNED_CRYPTOS:
            logger.info("No pinned cryptos found")
            return []
        
        logger.info(f"Getting data for {len(settings.PINNED_CRYPTOS)} pinned cryptos: {settings.PINNED_CRYPTOS}")
        
        # Get all coins data (this will use cache if available)
        all_coins = self.get_all_coins(limit=250)  # Get more coins to ensure we find all pinned ones
        
        # Filter to only include pinned coins
        pinned_coins = [coin for coin in all_coins if coin['id'] in settings.PINNED_CRYPTOS]
        
        logger.info(f"Found {len(pinned_coins)} pinned coins in the market data")
        return pinned_coins