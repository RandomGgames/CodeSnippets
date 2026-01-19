"""
Functions for downloading files from the internet
"""

import logging
import typing
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


def download_if_updated(url: str, file_path: typing.Union[str, Path], etag_file_path: typing.Union[str, Path]):
    """
    Download a file only if it has changed on the server.
    Uses ETag headers for conditional requests.
    """
    file_path = Path(file_path)
    etag_file_path = Path(etag_file_path)

    headers = {}
    if etag_file_path.exists():
        with open(etag_file_path, "r", encoding="utf-8") as f:
            etag = f.read().strip()
        if etag:
            headers["If-None-Match"] = etag

    logger.debug(f"Checking for updates to {file_path} from {url}...")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 304:
            logger.debug(f"{file_path} has not been modified. Using cached version.")
            return file_path

        response.raise_for_status()  # will raise for 4xx/5xx

        # fresh download
        logger.debug(f"Updating {file_path}...")
        file_path.write_bytes(response.content)

        new_etag = response.headers.get("ETag", "")
        if new_etag:
            with open(etag_file_path, "w", encoding="utf-8") as f:
                f.write(new_etag)

        logger.debug(f"{file_path} updated.")
        return file_path

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while downloading {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise


# Example usage:
# download_if_updated("https://raw.githubusercontent.com/spdx/license-list-data/refs/heads/main/text/MIT.txt", "MIT.txt", "MIT_etag.txt")
