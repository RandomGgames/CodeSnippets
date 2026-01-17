"""
Create a zip archive from a list of files. Any files that don't exist are skipped.
"""
import json
import logging
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)


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
