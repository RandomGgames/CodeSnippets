import logging
import pathlib
import typing

logger = logging.getLogger(__name__)


def read_text_file_lines(file_path: typing.Union[str, pathlib.Path]) -> typing.List[str]:
    """
    Reads a text file and returns a list of strings with the \n characters at the end of each line removed.
    Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the text file to read.

    Returns:
    typing.List[str]: A list of strings with the \n characters at the end of each line removed.
    """
    try:
        file_path = pathlib.Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: '{file_path.parent}'")
        with open(file_path, 'r') as f:
            lines = [line.rstrip("\n\r") for line in f]
        logger.info(f"Successfully read {file_path}")
        return lines
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return []


def write_text_file_lines(file_path: typing.Union[str, pathlib.Path], lines: typing.List[str]) -> None:
    """
    Writes a list of strings to a text file, with each string on a new line.
    Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the text file to write.
    lines (typing.List[str]): A list of strings to write to the text file.

    Returns:
    None
    """
    try:
        file_path = pathlib.Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: '{file_path.parent}'")
        with open(file_path, 'r') as f:
            for line in lines:
                f.write(line + '\n')
        logger.info(f"Successfully wrote {file_path}")
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")


def read_text_file(file_path: typing.Union[str, pathlib.Path]) -> str:
    """
    Reads a text file and returns its entire contents as a single string.
    Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the text file to read.

    Returns:
    str: The entire contents of the text file as a single string.
    """
    try:
        file_path = pathlib.Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: '{file_path.parent}'")
        with open(file_path, 'r') as f:
            text = f.read()
        logger.info(f"Successfully read {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""


def write_text_file(file_path: typing.Union[str, pathlib.Path], text: str) -> None:
    """
    Writes a string to a text file. Includes error checking and logging.

    Args:
    file_path (typing.Union[str, pathlib.Path]): The file path of the text file to write.
    text (str): A string to write to the text file.
    """
    try:
        file_path = pathlib.Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created folder: '{file_path.parent}'")
        with open(file_path, 'w') as f:
            f.write(text)
        logger.info(f"Successfully wrote {file_path}")
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")
