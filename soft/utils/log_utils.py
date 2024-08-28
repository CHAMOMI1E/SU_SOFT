import logging
from config.settings import LOGGING_LEVEL


def setup_logging():
    logging.basicConfig(
        level=LOGGING_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s"
    )
