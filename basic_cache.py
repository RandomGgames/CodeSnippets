"""
Cache module for saving and loading data to and from a file.
"""

import json
import logging
import typing
from pathlib import Path

logger = logging.getLogger(__name__)


def load_cache(path: typing.Union[Path, str] = "cache.json") -> dict:
    """
    Loads a cache from the given path.

    Args:
    path (typing.Union[pathlib.Path, str], optional): The path of the cache file to load. Defaults to "cache.json".

    Returns:
    dict: The loaded cache.
    """
    logger.debug("Loading cache...")
    path = Path(path)
    if path.exists():
        try:
            logger.debug("Reading cache file...")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.debug("Read cache file.")
        except json.JSONDecodeError as e:
            logger.error("Failed to load cache from %s due to %s. Generating blank cache...", json.dumps(str(path)), e)
            data = {}
    else:
        logger.debug("Cache file %s does not exist. Generating blank cache...", json.dumps(str(path)))
        data = {}

    logger.debug("Cache loaded.")
    return data


def validate_cache(data: dict) -> None:
    """
    Validates the given cache data.

    Args:
    cache (dict): The cache data to validate.
    """
    logger.debug("Validating cache...")
    for file_path in list(data["files"].keys()):
        if not Path(file_path).exists():
            logger.debug("Removing non-existent file %s from cache.", json.dumps(str(file_path)))
            del data["files"][file_path]
    logger.debug("Cache validated successfully.")


def save_cache(data: dict, path: typing.Union[Path, str] = "cache.json") -> None:
    """
    Saves the given cache data to the given path.

    Args:
    data (dict): The cache data to save.
    path (typing.Union[pathlib.Path, str], optional): The path of the cache file to save. Defaults to "cache.json".
    """
    logger.debug("Saving cache...")
    path = Path(path)
    try:
        cache_dir = path.parent
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)
            logger.debug("Created cache directory %s.", json.dumps(str(cache_dir)))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.debug("Saved cache.")
    except Exception as e:
        logger.error("Failed to save cache to %s due to %s.", json.dumps(str(path)), e)
        raise


# Example usage
cache = load_cache()
cache["a"] = "a"
cache["b"] = 2
cache["c"] = ["c"]
save_cache(cache)
