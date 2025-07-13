from pydantic import BaseModel

class CryptoPriceResponse(BaseModel):
    crypto_id: str
    price: float
    currency: str = "USD"

class PinCryptoRequest(BaseModel):
    crypto_id: str

class PinnedCryptoResponse(BaseModel):
    crypto_id: str
    price: float
    currency: str = "USD"

class CoinMarketData(BaseModel):
    id: str
    name: str
    symbol: str
    image: str
    current_price: float
    market_cap: float
    market_cap_rank: int
    price_change_percentage_24h: float
    currency: str = "usd"