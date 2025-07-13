import os
import json
from app.core.logging import log as logger
from dotenv import load_dotenv

load_dotenv()

class AppConfig:
    PROJECT_NAME: str = "Crypto Tracker API"
    API_V1_STR: str = "/api/v1"
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    COINGECKO_CACHE_DURATION: int = int(os.getenv("COINGECKO_CACHE_DURATION", "60"))
    PINNED_CRYPTOS_FILE: str = "pinned_cryptos.json"
    
    def __init__(self):
        self.PINNED_CRYPTOS = self.load_pinned_cryptos()
        self.check_api_key_status()
    
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
    
    def check_api_key_status(self):
        """Check API key status and provide guidance"""
        if not self.COINGECKO_API_KEY:
            logger.warning("COINGECKO_API_KEY not set - using public API with limited rate limits")
            logger.info("For better performance, get a free API key at https://www.coingecko.com/en/api")

settings = AppConfig()