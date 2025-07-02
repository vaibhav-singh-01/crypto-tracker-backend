import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    PROJECT_NAME: str = "Crypto Tracker API"
    API_V1_STR: str = "/api/v1"
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    PINNED_CRYPTOS_FILE: str = "pinned_cryptos.json"
    
    def __init__(self):
        self.PINNED_CRYPTOS = self.load_pinned_cryptos()
    
    def load_pinned_cryptos(self) -> list:
        """Load pinned cryptos from file"""
        if os.path.exists(self.PINNED_CRYPTOS_FILE):
            try:
                with open(self.PINNED_CRYPTOS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading pinned cryptos: {e}")
                return []
        return []
    
    def save_pinned_cryptos(self):
        """Save pinned cryptos to file"""
        try:
            with open(self.PINNED_CRYPTOS_FILE, 'w') as f:
                json.dump(self.PINNED_CRYPTOS, f)
        except Exception as e:
            logger.error(f"Error saving pinned cryptos: {e}")

settings = Settings()