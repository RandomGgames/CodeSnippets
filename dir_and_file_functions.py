"""
Functions for working with directories
"""

import hashlib
import json
import logging
import os
import re
import send2trash
import time
import zipfile
from pathlib import Path
from typing import Iterable, Pattern

import win32com.client

logger = logging.getLogger(__name__)


def ensure_dir(path: Path) -> None:
    """Ensures the parent directory for a given file path exists."""
    path = Path(path).resolve()

    # If the path doesn't exist, we assume it's a file if it has an extension.
    # Otherwise, if it's already a file, we want its parent.
    if path.suffix or path.is_file():
        path = path.parent

    try:
        # exist_ok=True replaces the manual 'if not path.exists()' check
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.debug("Created %s", json.dumps(str(path)))
    except OSError as e:
        logger.error("Error creating directory %s: %s", json.dumps(str(path)), e)
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
    logger.debug("Checking if %s is empty...", json.dumps(str(path)))
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


def get_file_data(file_path: Path | str) -> tuple[int, int, int]:
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
    return mtime, ctime, size


def sanitize_filename(name: str, default: str = "file", max_length: int = 255) -> str:
    """
    Remove characters that are illegal in filenames and handle reserved names.

    Args:
        name: Original string.
        default: Value to use if result is empty or reserved.
        max_length: Maximum filename length.

    Returns:
        Sanitized lowercase string.
    """
    illegal_chars_pattern = r'[<>:"/\\|?*]'
    reserved_names = {
        "con", "prn", "aux", "nul",
        *(f"com{i}" for i in range(1, 10)),
        *(f"lpt{i}" for i in range(1, 10)),
    }
    try:
        sanitized = re.sub(illegal_chars_pattern, "", name)
        sanitized = sanitized.strip().replace(" ", "_").lower()
        sanitized = sanitized[:max_length]
        if not sanitized or sanitized in reserved_names:
            return default
        return sanitized
    except re.error as e:
        logger.exception("Regex error while sanitizing filename %s: %s", json.dumps(name), e)
        return default


def create_zip(paths: list[Path], zip_path: Path, compresslevel: int = 6) -> None:
    """
    Create a zip archive from a list of files and folders.
    """
    try:
        missing_paths = [p for p in paths if not p.exists()]
        if missing_paths:
            raise FileNotFoundError(f"Missing paths: {[str(p) for p in missing_paths]}")

        if not zip_path.parent.exists():
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info("Created %s", json.dumps(str(zip_path.parent.as_posix())))

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compresslevel) as zipf:
            for path in paths:
                if path.is_file():
                    zipf.write(path, arcname=path.name)
                    continue

                for sub in path.rglob("*"):
                    if sub.is_file():
                        zipf.write(sub, arcname=str(sub.relative_to(path.parent)))

        logger.info("Created %s", json.dumps(str(zip_path.as_posix())))

    except Exception:
        logger.exception("Failed to create zip archive %s", json.dumps(str(zip_path.as_posix())))
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
        logger.exception("Failed to get files list for %s", json.dumps(str(root)))
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
        logger.exception("Failed to clean path string %s", json.dumps(str(path_str)))
        raise

    except Exception:
        logger.exception("Failed to clean path string %s", json.dumps(str(path_str)))
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

    logger.debug("Generating hash for %s using %s...", json.dumps(str(file_path)), algorithm)
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
        logger.exception("Failed to generate hash for %s: %s", file_path, e)
        raise

    logger.debug("Generated hash %s for %s", json.dumps(str(hexd)), file_path)
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


def send_to_recycle_bin(path: Path) -> bool:
    """
    Sends any duplicate files to the recycle bin

    Args:
        duplicates: A list of duplicate files
    """
    path = Path(path)

    try:
        send2trash.send2trash(str(path))
        logger.info("Sent %s to recycle bin.", json.dumps(str(path.as_posix())))
        return True
    except OSError as e:
        logger.error("Failed to send %s to recycle bin: %s", json.dumps(str(path.as_posix())), e)
        return False
