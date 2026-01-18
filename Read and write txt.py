"""
Functions for reading and writing text files
"""

from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


def read_text_file(file_path: Path | str) -> str:
    """
    Reads a text file and returns its entire contents as a single string.
    Includes error checking and logging.

    Args:
    file_path (Path | str): The file path of the text file to read.

    Returns:
    str: The entire contents of the text file as a single string.
    """
    try:
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: {json.dumps(str(file_path.parent))}")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        logger.info(f"Successfully read {json.dumps(str(file_path))}")
        return text
    except FileNotFoundError:
        logger.error(f"File not found: {json.dumps(str(file_path))}")
        return ""
    except PermissionError:
        logger.error(f"Permission denied: {json.dumps(str(file_path))}")
        return ""
    except OSError as e:
        logger.error(f"Error reading {json.dumps(str(file_path))}", e)
        return ""


def read_text_file_lines(file_path: Path | str) -> list[str]:
    """
    Reads a text file and returns a list of strings with the \n characters at the end of each line removed.
    Includes error checking and logging.

    Args:
    file_path (Path | str): The file path of the text file to read.

    Returns:
    list[str]: A list of strings with the \n characters at the end of each line removed.
    """
    try:
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: {json.dumps(str(file_path.parent))}")
        with open(file_path, "r", encoding="utf-8") as f:
            text_lines = [line.rstrip("\n\r") for line in f]
        logger.info(f"Successfully read {json.dumps(str(file_path))}")
        return text_lines
    except FileNotFoundError:
        logger.error(f"File not found: {json.dumps(str(file_path))}")
        return []
    except PermissionError:
        logger.error(f"Permission denied: {json.dumps(str(file_path))}")
        return []
    except OSError as e:
        logger.error(f"Error reading {json.dumps(str(file_path))}", e)
        return []


def write_text_file(file_path: Path | str, text: str) -> None:
    """
    Writes a string to a text file. Includes error checking and logging.

    Args:
    file_path (Path | str): The file path of the text file to write.
    text (str): A string to write to the text file.
    """
    try:
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: {json.dumps(str(file_path.parent))}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"Successfully wrote {json.dumps(str(file_path))}")
    except FileNotFoundError:
        logger.error(f"File not found: {json.dumps(str(file_path))}")
    except PermissionError:
        logger.error(f"Permission denied: {json.dumps(str(file_path))}")
    except OSError as e:
        logger.error(f"Error writing {json.dumps(str(file_path))}", e)


def write_text_file_lines(file_path: Path | str, lines: list[str]) -> None:
    """
    Writes a list of strings to a text file, with each string on a new line.
    Includes error checking and logging.

    Args:
    file_path (Path | str): The file path of the text file to write.
    lines (list[str]): A list of strings to write to the text file.

    Returns:
    None
    """
    try:
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: {json.dumps(str(file_path.parent))}")
        with open(file_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        logger.info(f"Successfully wrote {json.dumps(str(file_path))}")
    except FileNotFoundError:
        logger.error(f"File not found: {json.dumps(str(file_path))}")
    except PermissionError:
        logger.error(f"Permission denied: {json.dumps(str(file_path))}")
    except OSError as e:
        logger.error(f"Error writing {json.dumps(str(file_path))}", e)
