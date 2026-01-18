"""
A function to get the name of the current function.
"""

import logging
import inspect

logger = logging.getLogger(__name__)


def get_function_name():
    """
    Get the name of the current function.

    Returns:
        str: The name of the current function.
    """
    frame = inspect.currentframe()
    if frame is not None:
        frame = frame.f_back
        if frame is not None:
            return frame.f_code.co_name
    logger.warning("Could not get function name. Returning empty string.")
    return ""
