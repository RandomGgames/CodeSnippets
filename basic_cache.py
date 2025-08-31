import json
import logging
import pathlib
import typing
logger = logging.getLogger(__name__)


def load_cache(path: typing.Union[pathlib.Path, str] = "cache.json") -> dict:
    logger.debug("Loading cache...")
    path = pathlib.Path(path)
    if path.exists():
        try:
            logger.debug(f"Reading cache file...")
            with open(path) as f:
                cache = json.load(f)
                logger.debug(f"Read cache file.")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load cache from {path} due to {e}. Generating blank cache...")
            cache = {}
    else:
        logger.debug(f"Cache file '{path}' does not exist. Generating blank cache...")
        cache = {}
    # cache.setdefault("files", {})

    # logger.debug("Validating cache...")
    # for file_path in list(cache["files"].keys()):
    #     if not pathlib.Path(file_path).exists():
    #         logger.debug(f"Removing non-existent file {file_path} from cache.")
    #         del cache["files"][file_path]
    # logger.debug("Cache validated successfully.")

    logger.debug("Cache loaded.")
    return cache


def save_cache(cache: dict, path: typing.Union[pathlib.Path, str] = "cache.json") -> None:
    logger.debug("Saving cache...")
    path = pathlib.Path(path)
    try:
        cache_dir = path.parent
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)
            logger.debug(f"Created cache directory {cache_dir}.")
        with open(path, "w") as f:
            json.dump(cache, f, indent=4)
            logger.debug(f"Saved cache.")
    except Exception as e:
        logger.error(f"Failed to save cache to {path} due to {e}.")
        raise


cache = load_cache()
test = {
    "a": "a",
    "b": 2,
    "c": ["c"],

}
save_cache(test)
