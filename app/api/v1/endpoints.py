from fastapi import APIRouter, HTTPException
from app.services.crypto import CryptoService
from app.api.v1.models import (
    CryptoPriceResponse,
    PinCryptoRequest,
    PinnedCryptoResponse,
    CoinMarketData
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
crypto_service = CryptoService()

@router.get("/coins", response_model=list[CoinMarketData])
async def get_all_coins(vs_currency: str = "usd", limit: int = 100):
    try:
        logger.info(f"Fetching all coins: vs_currency={vs_currency}, limit={limit}")
        coins = crypto_service.get_all_coins(vs_currency, limit)
        logger.info(f"Successfully fetched {len(coins)} coins")
        return coins
    except Exception as e:
        logger.error(f"Error fetching coins: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/price/{crypto_id}", response_model=CryptoPriceResponse)
async def get_crypto_price(crypto_id: str):
    try:
        logger.info(f"Fetching price for {crypto_id}")
        price = crypto_service.get_price(crypto_id.lower())
        return {"crypto_id": crypto_id, "price": price}
    except Exception as e:
        logger.error(f"Error fetching price for {crypto_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pin")
async def pin_crypto(request: PinCryptoRequest):
    try:
        crypto_id = request.crypto_id.lower()
        logger.info(f"Pinning crypto: {crypto_id}")
        crypto_service.pin_crypto(crypto_id)
        return {"message": f"{crypto_id} pinned successfully"}
    except Exception as e:
        logger.error(f"Error pinning {request.crypto_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/unpin/{crypto_id}")
async def unpin_crypto(crypto_id: str):
    try:
        logger.info(f"Unpinning crypto: {crypto_id}")
        crypto_service.unpin_crypto(crypto_id.lower())
        return {"message": f"{crypto_id} unpinned successfully"}
    except Exception as e:
        logger.error(f"Error unpinning {crypto_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pinned", response_model=list[CoinMarketData])
async def get_pinned_cryptos():
    try:
        logger.info("Fetching pinned cryptos")
        pinned = crypto_service.get_pinned_cryptos()
        logger.info(f"Successfully fetched {len(pinned)} pinned cryptos")
        return pinned
    except Exception as e:
        logger.error(f"Error fetching pinned cryptos: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))