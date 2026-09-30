"""
Functions for reading and writing json files
"""

import json
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def read_json_file(file_path: Path, *, encoding: str = "utf-8") -> dict | list | str | int | float | bool | None:
    """
    Safely reads and parses a JSON file.
    """
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    try:
        data = json.loads(file_path.read_text(encoding=encoding))
        # logger.info("Successfully read data from %s", file_path)
        return data

    except json.JSONDecodeError as e:
        # logger.error("Invalid JSON format in %s", file_path)
        raise e

    except Exception as e:
        # logger.error("Unable to read %s", file_path)
        raise e


def write_json_file(file_path: Path, data: dict | list | str | int | float | bool | None, *, encoding: str = "utf-8", indent: int | str | None = 4, ensure_ascii: bool = True) -> bool:
    """
    Writes data to a JSON file atomically.
    """
    file_path = Path(file_path).absolute()

    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Created %s", json.dumps(str(file_path.parent.as_posix())))

    temp_file_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=str(file_path.parent), encoding=encoding, suffix=".tmp", delete=False) as tf:
            # Get file path from tempfile instance
            temp_file_path = Path(tf.name)
            # logger.info("Starting atomic write to %s", file_path)
            json.dump(data, tf, indent=indent, ensure_ascii=ensure_ascii)
            tf.flush()
            os.fsync(tf.fileno())

        # Atomic swap
        temp_file_path.replace(file_path)
        # logger.info("Successfully saved to %s", file_path)
        return True

    except (KeyboardInterrupt, SystemExit):
        logger.error("Write interrupted for %s. Cleaning up.", file_path)
        raise

    except Exception as e:
        logger.error("Failed to write to %s: %s", file_path, e)
        return False

    finally:
        if temp_file_path is not None:
            try:
                temp_file_path.unlink(missing_ok=True)
            except OSError:
                logger.exception("Failed to clean up temporary file %s", temp_file_path)


def load_config(file_path: Path, *, encoding: str = "utf-8") -> dict | list | str | int | float | bool | None:
    """Alias for read_json_file, specifically for configuration files."""
    return read_json_file(file_path, encoding=encoding)


def save_config(file_path: Path, config_data: dict | list | str | int | float | bool | None, *, encoding: str = "utf-8", indent: int | str | None = 4, ensure_ascii: bool = True) -> bool:
    """Alias for write_json_file, specifically for configuration files."""
    return write_json_file(file_path, config_data, encoding=encoding, indent=indent, ensure_ascii=ensure_ascii)


def load_cache(file_path: Path, *, encoding: str = "utf-8") -> dict | list | str | int | float | bool | None:
    """Alias for read_json_file, specifically for cache files."""
    return read_json_file(file_path, encoding=encoding)


def save_cache(file_path: Path, cache_data: dict | list | str | int | float | bool | None, *, encoding: str = "utf-8", indent: int | str | None = 4, ensure_ascii: bool = True) -> bool:
    """Alias for write_json_file, specifically for cache files."""
    return write_json_file(file_path, cache_data, encoding=encoding, indent=indent, ensure_ascii=ensure_ascii)
