"""
Functions for working with directories
"""

import hashlib
import json
import logging
import os
import re
import time
import zipfile
from pathlib import Path

import win32com.client

logger = logging.getLogger(__name__)


def ensure_dir(path: str | Path) -> None:
    """Checks if a directory exists (using pathlib) and creates it if it doesn't."""
    # Ensure path is a directory in case it's a file
    if os.path.isfile(path):
        path = os.path.dirname(path)

    try:
        path = Path(path)
        if not path.exists():
            path.mkdir(parents=True)
            logger.debug(f"Created folder: {json.dumps(str(path))}")
    except OSError as e:
        logger.error(f"Error creating directory {json.dumps(str(path))}", e)
        raise


def open_working_dir() -> None:
    """Opens the current working directory in the file explorer."""
    try:
        os.startfile(os.getcwd())
    except OSError:
        logger.exception("Error opening working directory")
        raise


def dir_is_empty(path: str | Path) -> bool:
    """
    Checks if a directory is empty.
    """
    path = Path(path)
    logger.debug(f"Checking if {json.dumps(str(path))} is empty...")
    if not os.path.isdir(path):
        logger.debug("Path is not a directory")
        return False
    for _, _, files in os.walk(path):
        if files:
            logger.debug("Dir is not empty")
            return False
    logger.debug("Dir is empty")
    return True


def wait_for_file(path: str | Path, timeout=30):
    """
    Polls the folder until the file appears, then continues.
    """
    path = Path(path)
    start_time = time.time()
    while not os.path.exists(path):
        if time.time() - start_time > timeout:
            raise FileNotFoundError(f"File {path} not found after {timeout} seconds")
        time.sleep(1)


def get_file_data(file_path: Path | str) -> dict[str, int]:
    """
    Gets file stats safely across different Operating Systems.
    Returns times in nanoseconds.
    """
    path = Path(file_path)
    stat = path.stat()
    mtime = stat.st_mtime_ns
    try:
        # macOS/BSD
        ctime = getattr(stat, 'st_birthtime_ns', None)
        if ctime is None:
            # Windows (st_ctime is creation time on Windows)
            ctime = stat.st_ctime_ns
    except AttributeError:
        # Linux fallback (st_ctime is metadata change, not birth)
        ctime = mtime

    size = stat.st_size
    logger.debug(f"File stats for {path.name}: {mtime=}, {ctime=}, {size=}")
    return {"modified": mtime, "created": ctime, "size": size}


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    try:
        illegal_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(illegal_chars, "_", name).strip()
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.replace(" ", "_")
        if not sanitized:
            logger.warning(f"Sanitized filename is empty. Using default: {json.dumps('file')}")
            sanitized = "file"
        return sanitized
    except re.error:
        logger.exception("Error while sanitizing filename")
        return "file"


def zip_files(files: list[str | Path], zip_path: str | Path, compresslevel: int = 6, error_on_missing: bool = False) -> None:
    """
    Create a zip archive from a list of files. Any files that don't exist are skipped.

    Args:
    files (list[str | Path]): A list of files to add to the zip archive.
    zip_path (str | Path): The path of the zip archive to create.
    compresslevel (int): The compression level to use when creating the zip archive.
        Level 0 is no compression, and level 9 is maximum compression.
    error_on_missing (bool): If True, raise a FileNotFoundError if any of the files in the list do not exist.
    """
    try:
        paths = [Path(p) for p in files]
        zip_path = Path(zip_path)

        existing_paths = [path for path in paths if path.exists()]
        if error_on_missing and len(existing_paths) != len(paths):
            raise FileNotFoundError(f"The following files were not found: {[str(path) for path in paths if not path.exists()]}")

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compresslevel) as zipf:
            for path in existing_paths:
                zipf.write(path, arcname=path.name)

        logger.info("Created release archive: %s", zip_path)

    except Exception:
        logger.exception(f"Failed to create zip archive {json.dumps(str(zip_path))}")
        raise


def get_files_list(root: str | Path) -> list[str]:
    """
    Returns a list of all files in a directory and its subdirectories.
    """
    root = Path(root)
    if root.is_file():
        raise ValueError(f"{json.dumps(str(root))} is a file, not a directory")

    try:
        files = os.listdir(root)
        return files

    except Exception:
        logger.exception(f"Failed to get files list for {json.dumps(str(root))}")
        raise


def clean_path_string(path_str: str) -> str:
    """
    A function that strips extra quotes (common if you "Copy as Path" in Windows) and fixes backslashes vs. forward slashes so Python doesn't get confused.
    """
    try:
        new_str = path_str.strip('"').replace("\\", "/")
        return new_str
    except AttributeError:
        logger.exception(f"Failed to clean path string {json.dumps(str(path_str))}")
        raise

    except Exception:
        logger.exception(f"Failed to clean path string {json.dumps(str(path_str))}")
        raise


def generate_hash(file_path: str | Path, algorithm="sha256") -> str:
    """
    Generates a hash for a file

    Args:
    file_path (str | Path): The path of the file to generate a hash for.
    algorithm (str): The hash algorithm to use. Default is "sha256".
    """
    logger.debug(f"Generating hash for {json.dumps(str(file_path))}...")
    try:
        with open(file_path, "rb") as f:
            digest = hashlib.file_digest(f, algorithm)
        hex_digest = digest.hexdigest()
        logger.debug(f"Generated hash {json.dumps(str(hex_digest))}.")
        return hex_digest

    except Exception:
        logger.exception(f"Failed to generate hash for {json.dumps(str(file_path))}")
        raise


def get_windows_details(file_path: str | Path, max_columns: int = 512) -> dict[str, str]:
    """
    Return Windows 'Details' tab properties for a file using the Shell Property System.

    - Windows only.
    - Requires pywin32: pip install pywin32
    - Keys are localized to the OS display language, matching File Explorer.
    - Values are formatted like Explorer shows them.

    Args:
        file_path: Target file.
        max_columns: Maximum number of property columns to probe.

    Returns:
        Dict of {property_label: value} for all non-empty properties.
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(p)
    if os.name != "nt":
        raise OSError("get_windows_details is only supported on Windows")

    # Bind to Shell
    shell = win32com.client.Dispatch("Shell.Application")
    folder = shell.NameSpace(str(p.parent))
    if folder is None:
        raise RuntimeError(f"Shell.NameSpace failed for {p.parent}")
    item = folder.ParseName(p.name)
    if item is None:
        raise RuntimeError(f"Shell.ParseName failed for {p}")

    props: dict[str, str] = {}
    blanks = 0

    for i in range(max_columns):
        header = folder.GetDetailsOf(None, i)
        if not header:
            blanks += 1
            if blanks >= 25:
                break
            continue
        blanks = 0

        value = folder.GetDetailsOf(item, i)
        if isinstance(value, str):
            value = value.strip()
        if value:
            props[str(header).strip()] = str(value)

    return props


details = get_windows_details(r"img.jpg")
for k, v in details.items():
    print(f"{k}: {v}")
