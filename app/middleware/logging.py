from loguru import logger
from fastapi import Request
import time

async def log_middleware(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = (time.time() - start_time) * 1000
    formatted_time = f"{process_time:.2f}ms"

    # Log response
    logger.info(f"Response: {response.status_code} | Time: {formatted_time}")

    return response