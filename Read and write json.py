"""
Functions for reading and writing json files
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def read_json_file(file_path: Path | str) -> dict | list:
    """
    Reads a json file as a dictionary or list. Includes error checking and logging.

    Args:
    file_path (Path | str): The file path of the json file to read.

    Returns:
    dict | list: The contents of the json file as a dictionary or list.
    """
    try:
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: {json.dumps(str(file_path.parent))}")
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
            logger.debug(f"Successfully read json file: {json.dumps(str(file_path))}")
            return json_data
    except FileNotFoundError:
        logger.error(f"File not found: {json.dumps(str(file_path))}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding json file: {json.dumps(str(file_path))}")
        raise


def write_json_file(data: dict | list, file_path: Path | str) -> None:
    """
    Writes a dictionary or list to a json file. Includes error checking and logging.

    Args:
    data (dict | list): The data to write to the json file.
    file_path (Path | str): The file path of the json file to write.

    Returns:
    None
    """
    try:
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: {json.dumps(str(file_path.parent))}")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            logger.info(f"Successfully wrote json file: {json.dumps(str(file_path))}")
    except IOError:
        logger.error(f"Error writing json file: {json.dumps(str(file_path))}")
        raise
