"""
Functions for working with URLs
"""

import logging
import json
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def extract_url_domain(url):
    """
    Extracts the domain name from a given URL.
    For example: "https://www.google.com/" would return "google"

    Args:
        url (str): The URL to extract the domain name from.

    Returns:
        str: The domain name of the given URL.
    """

    logging.debug(f"Getting domain from {json.dumps(str(url))}")
    try:
        if not isinstance(url, str):
            logging.exception("Input is not a string.")
            raise TypeError("Input must be a string.")

        parsed_url = urlparse(url)
        domain = parsed_url.netloc.split(".")

        if domain[0] == "www":
            domain = domain[1]
        else:
            domain = domain[0]
        logging.debug(f"Got domain {json.dumps(str(domain))}")
        return domain

    except (ValueError, TypeError) as e:
        logging.exception(f"Error extracting domain from {json.dumps(str(url))}", exc_info=e)
        return None
