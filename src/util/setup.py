import logging


def setup_logging() -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.getLogger("asyncio").setLevel(logging.WARNING)  # hide annoying asyncio info
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)  # hide annoying gateway info
    return logging.getLogger("main")
