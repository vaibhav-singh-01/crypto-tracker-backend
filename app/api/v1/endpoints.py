from fastapi import APIRouter, HTTPException
from app.services.crypto import CryptoService
from app.api.v1.models import (
    CryptoPriceResponse,
    PinCryptoRequest,
    PinnedCryptoResponse,
    CoinMarketData
)
from app.core.providers import CryptoNotFoundError, CurrencyNotSupportedError, RateLimitError, APIServiceError
from app.core.logging import log as logger
router = APIRouter()
crypto_service = CryptoService()

@router.get("/coins", response_model=list[CoinMarketData])
async def get_all_coins(vs_currency: str = "usd", limit: int = 100):
    try:
        logger.info(f"Fetching all coins: vs_currency={vs_currency}, limit={limit}")
        coins = crypto_service.get_all_coins(vs_currency, limit)
        logger.info(f"Successfully fetched {len(coins)} coins")
        return coins
    except RateLimitError as e:
        logger.warning(f"Rate limit hit for get_all_coins: {str(e)}")
        raise HTTPException(status_code=429, detail=str(e))
    except APIServiceError as e:
        logger.error(f"API service error for get_all_coins: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fetching coins: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cryptocurrency data")

@router.get("/price/{crypto_id}", response_model=CryptoPriceResponse)
async def get_crypto_price(crypto_id: str, vs_currency: str = "usd"):
    try:
        logger.info(f"Fetching price for {crypto_id} in {vs_currency}")
        price = crypto_service.get_price(crypto_id.lower(), vs_currency.lower())
        return {"crypto_id": crypto_id, "price": price, "currency": vs_currency.lower()}
    except CryptoNotFoundError as e:
        logger.info(f"Crypto not found: {crypto_id} - {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except CurrencyNotSupportedError as e:
        logger.info(f"Currency not supported: {vs_currency} - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        logger.warning(f"Rate limit hit for {crypto_id}: {str(e)}")
        raise HTTPException(status_code=429, detail=str(e))
    except APIServiceError as e:
        logger.error(f"API service error for {crypto_id}: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fetching price for {crypto_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cryptocurrency price")

@router.post("/pin")
async def pin_crypto(request: PinCryptoRequest):
    try:
        crypto_id = request.crypto_id.lower()
        logger.info(f"Pinning crypto: {crypto_id}")
        crypto_service.pin_crypto(crypto_id)
        return {"message": f"{crypto_id} pinned successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pinning {request.crypto_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to pin cryptocurrency")

@router.delete("/unpin/{crypto_id}")
async def unpin_crypto(crypto_id: str):
    try:
        logger.info(f"Unpinning crypto: {crypto_id}")
        crypto_service.unpin_crypto(crypto_id.lower())
        return {"message": f"{crypto_id} unpinned successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unpinning {crypto_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unpin cryptocurrency")

@router.get("/pinned", response_model=list[CoinMarketData])
async def get_pinned_cryptos(vs_currency: str = "usd"):
    try:
        logger.info(f"Fetching pinned cryptos in {vs_currency}")
        pinned = crypto_service.get_pinned_cryptos(vs_currency.lower())
        logger.info(f"Successfully fetched {len(pinned)} pinned cryptos")
        return pinned
    except RateLimitError as e:
        logger.warning(f"Rate limit hit for get_pinned_cryptos: {str(e)}")
        raise HTTPException(status_code=429, detail=str(e))
    except APIServiceError as e:
        logger.error(f"API service error for get_pinned_cryptos: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fetching pinned cryptos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch pinned cryptocurrencies")

@router.get("/health")
async def health_check():
    return {"status": "healthy"}