import json
import logging
import pathlib
import typing

logger = logging.getLogger(__name__)


def read_json_file(file_path: typing.Union[str, pathlib.Path]) -> typing.Union[dict, list]:
    """
    Reads a json file as a dictionary or list. Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the json file to read.

    Returns:
    typing.Union[dict, list]: The contents of the json file as a dictionary or list.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            logger.debug(f"Successfully read json file: '{file_path}'")
            return data
    except FileNotFoundError:
        logger.error(f"File not found: '{file_path}'")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding json file: '{file_path}'")
        raise


def write_json_file(data: typing.Union[dict, list], file_path: typing.Union[str, pathlib.Path]) -> None:
    """
    Writes a dictionary or list to a json file. Includes error checking and logging.

    Args:
    data (typing.Union[dict, list]): The data to write to the json file.
    file_path (typing.Union[str, pathlib.Path]): The file path of the json file to write.

    Returns:
    None
    """
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
            logger.info(f"Successfully wrote json file: '{file_path}'")
    except IOError:
        logger.error(f"Error writing json file: '{file_path}'")
        raise
