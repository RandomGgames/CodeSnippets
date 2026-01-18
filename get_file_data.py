"""
Function and class for reading file data
"""

import logging
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)


class FileMetadata(NamedTuple):
    """Container for file statistics."""
    modified: int
    created: int
    size: int


def get_file_data(file_path: Path | str) -> FileMetadata:
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
    return FileMetadata(modified=mtime, created=ctime, size=size)
