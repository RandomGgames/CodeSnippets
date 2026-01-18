"""
Functions for working with and manipulating values
"""

import logging

logger = logging.getLogger()


def clamp_value(value, min_value, max_value):
    if min_value > max_value:
        raise ValueError("min_value must be <= max_value")

    original_value = value
    # Inclusive clamp
    value = min(max(value, min_value), max_value)

    # Log only if clamped
    if value != original_value:
        logger.info(f"Clamped value from {original_value} to {value} (range: [{min_value}, {max_value}])")

    return value


def to_bool(value):
    """
    Convert a value to a boolean.

    Acceptable truthy strings: "true", "yes", "1"
    Acceptable falsy strings: "false", "no", "0"
    Accepts int, float, bool directly.

    Raises ValueError if the value cannot be interpreted as boolean.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        result = value != 0
        return result

    if isinstance(value, str):
        val = value.strip().lower()
        if val in {"true", "yes", "1"}:
            return True
        if val in {"false", "no", "0"}:
            return False

    # Could not interpret value
    raise ValueError(f"Cannot convert {value!r} to bool")
