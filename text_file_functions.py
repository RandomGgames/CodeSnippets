"""
Functions for reading and writing text files
"""

import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def read_text_file(file_path: Path, as_list: bool = False, *, encoding: str = "utf-8") -> str | list[str]:
    """
    Reads a text file as a single string or a list of lines.

    Args:
        file_path: Path to the file.
        as_list: If True, returns a list of strings (lines). If False, one string.
        encoding: Encoding used to read the file.
    """
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    data = file_path.read_text(encoding=encoding)
    # logger.info("Successfully read data from %s", file_path)
    return data.split('\n') if as_list else data


def write_text_file(file_path: Path, data: str | list[str], *, encoding: str = "utf-8") -> bool:
    """
    Writes a string or a list of strings to a text file atomically.
    """
    file_path = Path(file_path).absolute()
    temp_file_path: Path | None = None
    try:
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            # logger.debug("Created %s", file_path.parent)

        with tempfile.NamedTemporaryFile(mode='w', dir=str(file_path.parent), encoding=encoding, newline='\n', suffix=".tmp", delete=False) as tf:
            temp_file_path = Path(tf.name)
            # logger.info("Starting atomic write to %s", file_path)

            if isinstance(data, list):
                tf.write('\n'.join(data))
            else:
                tf.write(data)

            tf.flush()
            os.fsync(tf.fileno())

        temp_file_path.replace(file_path)
        # logger.info("Successfully saved to %s", file_path)
        return True

    except (KeyboardInterrupt, SystemExit) as e:
        # logger.error("Write interrupted for %s. Cleaning up.", file_path)
        raise e

    except Exception:
        # logger.exception("Failed to write to %s", file_path)
        return False

    finally:
        if temp_file_path is not None:
            try:
                temp_file_path.unlink(missing_ok=True)
            except OSError:
                # logger.exception("Failed to clean up temporary file %s", temp_file_path)
                pass
