"""
Functions for reading and writing text files
"""

import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def read_text_file(file_path: Path, as_list: bool = False) -> str | list[str] | None:
    """
    Reads a text file as a single string or a list of lines.

    Args:
        file_path: Path to the file.
        as_list: If True, returns a list of strings (lines). If False, one string.
    """
    if not file_path.exists():
        logger.warning("File not found: %s", file_path)
        return None

    try:
        if as_list:
            # .read_text().splitlines() is cleaner than .readlines()
            # as it handles different OS line endings automatically
            data = file_path.read_text(encoding='utf-8').splitlines()
        else:
            data = file_path.read_text(encoding='utf-8')

        logger.info("Successfully read text from %s", file_path)
        return data

    except Exception as e:
        logger.error("Unexpected error reading %s: %s", file_path, e)
        return None


def write_text_file(file_path: Path, data: str | list[str]) -> bool:
    """
    Writes a string or a list of strings to a text file atomically.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temp_file_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=str(file_path.parent), encoding='utf-8', suffix=".tmp", delete=False) as tf:
            temp_file_path = Path(tf.name)
            logger.info("Starting atomic text write to %s", file_path)

            if isinstance(data, list):
                # Add newlines if they aren't already there to ensure
                # list items don't all end up on one line
                tf.writelines(line if line.endswith('\n') else f"{line}\n" for line in data)
            else:
                tf.write(data)

            tf.flush()
            os.fsync(tf.fileno())

        temp_file_path.replace(file_path)
        logger.info("Successfully saved text to %s", file_path)
        return True

    except (KeyboardInterrupt, SystemExit):
        logger.error("Write interrupted for %s. Cleaning up.", file_path)
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        raise

    except Exception as e:
        logger.error("Failed to write text to %s: %s", file_path, e)
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        return False
