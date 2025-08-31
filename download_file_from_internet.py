import logging
import pathlib
import requests
import typing

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://opensource.org/licenses/MIT"  # safe, text, stable
DEFAULT_FILE = "default.txt"
DEFAULT_ETAG_FILE = "default_etag.txt"


def download_if_updated(
    url: str,
    file_path: typing.Union[str, pathlib.Path],
    etag_file_path: typing.Union[str, pathlib.Path],
):
    """
    Download a file only if it has changed on the server.
    Uses ETag headers for conditional requests.
    """
    file_path = pathlib.Path(file_path)
    etag_file_path = pathlib.Path(etag_file_path)

    headers = {}
    if etag_file_path.exists():
        etag = etag_file_path.read_text().strip()
        if etag:
            headers["If-None-Match"] = etag

    logger.debug(f"Checking for updates to {file_path} from {url}...")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 304:
            logger.debug(f"{file_path} has not been modified. Using cached version.")
            return file_path

        response.raise_for_status()  # will raise for 4xx/5xx

        # fresh download
        logger.debug(f"Updating {file_path}...")
        file_path.write_bytes(response.content)

        new_etag = response.headers.get("ETag", "")
        if new_etag:
            etag_file_path.write_text(new_etag)

        logger.debug(f"{file_path} updated.")
        return file_path

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while downloading {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise
