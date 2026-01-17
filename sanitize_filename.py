"""
Sanitize a string to be safe for use as a filename.
"""

import json
import logging
import re

logger = logging.getLogger(__name__)


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
