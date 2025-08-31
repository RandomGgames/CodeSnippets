import logging
import os
logger = logging.getLogger(__name__)


def dir_is_empty(path) -> bool:
    if not os.path.isdir(path):
        logger.debug(f"Path is not a directory")
        return False
    for _, _, files in os.walk(path):
        if files:
            logger.debug(f"Dir is not empty")
            return False
    logger.debug(f"Dir is empty")
    return True
