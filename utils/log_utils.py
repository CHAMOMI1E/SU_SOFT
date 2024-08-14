import logging
from SU_SOFT.config.settings import LOGGING_LEVEL


def setup_logging():
    logging.basicConfig(
        level=LOGGING_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s"
    )
