"""
Functions for reading and writing json files
"""

import json
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def read_json_file(file_path: Path) -> dict | list | None:
    """
    Safely reads and parses a JSON file.
    """
    if not file_path.exists():
        logger.warning("File not found: %s", json.dumps(str(file_path)))
        return None

    try:
        data = json.loads(file_path.read_text(encoding='utf-8'))
        logger.info("Successfully read data from %s", json.dumps(str(file_path)))
        return data

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format in %s: %s", json.dumps(str(file_path)), e)
        return None

    except Exception as e:
        logger.error("Unexpected error reading %s: %s", json.dumps(str(file_path)), e)
        return None


def write_json_file(file_path: Path, data: dict | list) -> bool:
    """
    Writes data to a JSON file atomically.
    """
    file_path = Path(file_path).absolute()

    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Created %s", json.dumps(str(file_path.parent.as_posix())))

    temp_file_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=str(file_path.parent), encoding='utf-8', suffix=".tmp", delete=False) as tf:
            # Get file path from tempfile instance
            temp_file_path = Path(tf.name)
            logger.debug("Starting atomic write to %s", json.dumps(str(file_path)))
            json.dump(data, tf, indent=4)
            tf.flush()
            os.fsync(tf.fileno())

        # Atomic swap
        temp_file_path.replace(file_path)
        logger.info("Successfully saved to %s", json.dumps(str(file_path)))
        return True

    except (KeyboardInterrupt, SystemExit):
        logger.error("Write interrupted for %s. Cleaning up.", json.dumps(str(file_path)))
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        raise

    except Exception as e:
        logger.error("Failed to write to %s: %s", json.dumps(str(file_path)), e)
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        return False


def load_config(file_path: Path) -> dict | list | None:
    """Alias for read_json_file, specifically for configuration files."""
    return read_json_file(file_path)


def save_config(file_path: Path, config_data: dict | list) -> bool:
    """Alias for write_json_file, specifically for configuration files."""
    return write_json_file(file_path, config_data)


def load_cache(file_path: Path) -> dict | list | None:
    """Alias for read_json_file, specifically for cache files."""
    return read_json_file(file_path)


def save_cache(file_path: Path, cache_data: dict | list) -> bool:
    """Alias for write_json_file, specifically for cache files."""
    return write_json_file(file_path, cache_data)
