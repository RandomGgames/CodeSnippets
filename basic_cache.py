"""
Cache module for saving and loading data to and from a file.
"""

import json
import logging
from pathlib import Path

from dir_and_file_functions import ensure_dir

logger = logging.getLogger(__name__)


def load_cache(path: Path = Path("cache.json")) -> dict:
    """
    Loads a cache from the given path.

    Args:
    path (typing.Union[pathlib.Path, str], optional): The path of the cache file to load. Defaults to "cache.json".

    Returns:
    dict: The loaded cache.
    """
    path = Path(path)
    logger.debug(f"Loading cache file {json.dumps(str(path))}...")

    data = {}
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.debug("Loaded cache.")
        except json.JSONDecodeError:
            logger.exception("Failed to decode cache file. Using empty cache.")
        except OSError:
            logger.exception("Failed to read cache file. Using empty cache.")
    else:
        logger.info("Cache file does not exist. Using empty cache.")

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


def save_cache(data: dict, path: Path = Path("cache.json")) -> None:
    """
    Saves the given cache data to the specified path.

    Args:
        data (dict): The cache data to save.
        path (str | Path, optional): The path of the cache file to save. Defaults to "cache.json".
    """
    path = Path(path)
    logger.debug(f"Saving cache to {json.dumps(str(path))}...")

    try:
        ensure_dir(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        logger.debug(f"Saved cache with {len(data)} entries.")
    except Exception:
        logger.exception("Failed to save cache.")
        raise


# Example usage
cache = load_cache()
cache["a"] = "a"
cache["b"] = 2
cache["c"] = ["c"]
save_cache(cache)
