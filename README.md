# crypto-tracker-be-assignment-python-FastAPI

A simple, modular cryptocurrency price tracker API built with *Python* and the *FastAPI* framework. It allows users to:

- Fetch real-time prices from the CoinGecko API.  
- Pin favorite cryptocurrencies (in-memory).  
- Retrieve prices for pinned cryptocurrencies.  
- Unpin pinned cryptocurrencies.  
- Automatically logs all requests and responses via middleware using Loguru.  
- Supports `.env` configuration and enables CORS for frontend integration.
- In-memory caching to reduce redundant API calls.

## Getting started

### Prerequisites

- Python
- Internet access (to call the CoinGecko API)

### How to start the app

From the project root, run:

```bash
uvicorn app.main:app --reload

## APIs

### 1. GET /

Read root: Introductory message

Response: {"message": "Welcome to the Crypto Tracker API"}

### 2. GET /health

health check

Response: {"status": "healthy"}

### 3. GET /api/v1/coins

To get list of coins to show at homepage: takes parameters vs_currency and limit (deafult values are "usd" and 100)

Request url: http://127.0.0.1:8000/api/v1/coins?limit=3

Curl: 
   curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/coins?limit=3' \
  -H 'accept: application/json'

Success Response: 
[
  {
    "id": "bitcoin",
    "name": "Bitcoin",
    "symbol": "btc",
    "image": "https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png?1696501400",
    "current_price": 106573,
    "market_cap": 2119853324993,
    "market_cap_rank": 1,
    "price_change_percentage_24h": -1.1366
  },
  {
    "id": "ethereum",
    "name": "Ethereum",
    "symbol": "eth",
    "image": "https://coin-images.coingecko.com/coins/images/279/large/ethereum.png?1696501628",
    "current_price": 2447.3,
    "market_cap": 295577938238,
    "market_cap_rank": 2,
    "price_change_percentage_24h": -0.68686
  },
  {
    "id": "tether",
    "name": "Tether",
    "symbol": "usdt",
    "image": "https://coin-images.coingecko.com/coins/images/325/large/Tether.png?1696501661",
    "current_price": 1,
    "market_cap": 157739473773,
    "market_cap_rank": 3,
    "price_change_percentage_24h": 0.00527
  }
]

Error Response:
{
  "detail": "Error fetching coins: 400 Client Error: Bad Request for url: https://api.coingecko.com/api/v3/coins/markets?vs_currency=bad_value_to_get_error&order=market_cap_desc&per_page=2&page=1&sparkline=False"
}

### 4. GET /api/v1/price/{crypto_id}

To fetch price of a specific crypto_id

Request url: http://127.0.0.1:8000/api/v1/price/bitcoin

curl: 
   curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/price/bitcoin' \
  -H 'accept: application/json'

Success response:
{
  "crypto_id": "bitcoin",
  "price": 106558,
  "currency": "USD"
}

Error response:
{
  "detail": "Error fetching price: 'tibcoin'"
}

### 5. POST /api/v1/pin

To pin a specific crypto, crypto_id should be sent in the body.

request url: http://127.0.0.1:8000/api/v1/pin

curl:
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/pin' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "crypto_id": "bitcoin"
}'

response if crypto already pinned:
{
  "detail": "400: Crypto already pinned"
}

response if success:
{
  "message": "dogecoin pinned successfully"
}

### 6. DELETE /api/v1/unpin/{crypto_id}

To unpin crypto_id

request url: http://127.0.0.1:8000/api/v1/unpin/bitcoin

curl:
curl -X 'DELETE' \
  'http://127.0.0.1:8000/api/v1/unpin/bitcoin' \
  -H 'accept: application/json'

success response:
{
  "message": "bitcoin unpinned successfully"
}

error response:
{
  "detail": "404: Crypto not pinned"
}

### 7. GET /api/v1/pinned

To fetch all the pinned cryptos

request url: http://127.0.0.1:8000/api/v1/pinned

curl: 
   curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/pinned' \
  -H 'accept: application/json'

success response:

[
  {
    "id": "dogecoin",
    "name": "Dogecoin",
    "symbol": "doge",
    "image": "https://coin-images.coingecko.com/coins/images/5/large/dogecoin.png?1696501409",
    "current_price": 0.160285,
    "market_cap": 24025367207,
    "market_cap_rank": 9,
    "price_change_percentage_24h": -2.73871
  }
]






