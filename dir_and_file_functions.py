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
from typing import Iterable, Pattern

import win32com.client

logger = logging.getLogger(__name__)


def ensure_dir(path: Path) -> None:
    """Checks if a directory exists (using pathlib) and creates it if it doesn't."""
    # Ensure path is a directory in case it's a file
    path = Path(path)
    if path.is_file():
        path = path.parent

    try:
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
    r"""
    Remove characters that are illegal in filenames.

    Illegal characters: <>:"/\|?*

    Args:
        name: Original string.

    Returns:
        Sanitized lowercase string.
    """
    try:
        illegal_chars_pattern = r'[<>:"/\\|?*]'
        sanitized = re.sub(illegal_chars_pattern, "", name)
        return sanitized.lower()
    except re.error as e:
        logger.exception(f"Regex error while sanitizing filename {json.dumps(name)}: {e}")
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


def find_files(root: Path | str, *, recursive: bool = True, include: list[str | Pattern] | None = None, ignore: list[str | Pattern] | None = None) -> Iterable[Path]:
    """
    Yield files in a directory filtered by regex-based include and ignore patterns.

    Args:
        root: Directory path to search.
        recursive: If True, search all subdirectories.
        include: List of regex strings or compiled patterns. Only files matching
            at least one pattern are included. If None, all files are included.
        ignore: List of regex strings or compiled patterns. Files matching any
            pattern are skipped.

    Yields:
        pathlib.Path objects for files matching the include/ignore criteria.

    Raises:
        FileNotFoundError: If `root` does not exist.
        ValueError: If `root` is not a directory.
    """
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(f"Root path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Expected a directory, got: {root}")

    # Compile regexes if needed
    include_patterns: list[Pattern] = [
        re.compile(p) if isinstance(p, str) else p for p in (include or [])
    ]
    ignore_patterns: list[Pattern] = [
        re.compile(p) if isinstance(p, str) else p for p in (ignore or [])
    ]

    iterator = root.rglob("*") if recursive else root.glob("*")
    for path in iterator:
        if not path.is_file():
            continue

        path_str = str(path)

        # Skip files matching any ignore pattern
        if any(p.search(path_str) for p in ignore_patterns):
            continue

        # Include only if it matches at least one include pattern (or no include pattern)
        if include_patterns and not any(p.search(path_str) for p in include_patterns):
            continue

        yield path


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


def generate_hash(file_path: str | Path, algorithm: str = "sha256") -> str:
    """
    Generate a hexadecimal hash for a file.

    Works with Python >=3.6. If running on Python >=3.11, uses
    `hashlib.file_digest` for optimal performance. Otherwise,
    reads the file in chunks to avoid memory issues with large files.

    Args:
        file_path: Path to the file (str or Path).
        algorithm: Hash algorithm name (e.g., 'sha256', 'md5').

    Returns:
        Hexadecimal string of the file hash.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the algorithm is not supported.
        OSError: if reading the file fails.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    logger.debug(f"Generating hash for {json.dumps(str(file_path))} using {algorithm}...")
    try:
        with open(file_path, "rb") as f:
            # Python 3.11+ optimal path
            try:
                digest = hashlib.file_digest(f, algorithm)
                hexd = digest.hexdigest()
            except AttributeError:
                # Fallback for older Python: read in chunks
                h = hashlib.new(algorithm)
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
                hexd = h.hexdigest()
    except Exception as e:
        logger.exception(f"Failed to generate hash for {file_path}: {e}")
        raise

    logger.debug(f"Generated hash {json.dumps(str(hexd))} for {file_path}")
    return hexd


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
