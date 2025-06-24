from loguru import logger

def setup_logging():
    logger.add(
        "app.log",
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    return logger

log = setup_logging()