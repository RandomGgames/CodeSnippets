import logging
import pathlib
import typing
logger = logging.getLogger(__name__)


def get_file_data(file_path: typing.Union[str, pathlib.Path]) -> tuple[int, int, int]:
    logger.debug(f"Getting file data...")
    file_path = pathlib.Path(file_path)
    modified_time = file_path.stat().st_mtime_ns
    created_time = file_path.stat().st_birthtime_ns
    size = file_path.stat().st_size
    logger.debug(f"Got file data: {modified_time=}, {created_time=}, {size=}")
    return modified_time, created_time, size
