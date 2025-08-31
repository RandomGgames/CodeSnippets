import hashlib
import logging
import pathlib
import typing
logger = logging.getLogger(__name__)


def generate_hash(file_path: typing.Union[str, pathlib.Path], algorithm="sha256") -> str:
    logger.debug(f"Generating hash for {file_path}...")
    with open(file_path, "rb") as f:
        digest = hashlib.file_digest(f, algorithm)
    hash = digest.hexdigest()
    logger.debug(f"Generated hash '{hash}'.")
    return hash
