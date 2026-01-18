"""
Function for checking if a measured value falls within the target range.
"""

import logging

logger = logging.getLogger()


def is_in_tolerance(experimental_value: float, target_value: float, target_tolerance: float, name: str) -> bool:
    """Check if a measured value falls within the target range."""
    # Logic
    deviation = round(abs(experimental_value - target_value), 2)
    in_tolerance = (target_value - target_tolerance) <= experimental_value <= (target_value + target_tolerance)

    # Logging setup
    symbol = ">" if deviation > target_tolerance else "<" if deviation < target_tolerance else "="
    status = "PASS" if in_tolerance else "FAIL"

    log_msg = f"{name} | {status} | Measured: {experimental_value} | Target: {target_value}±{target_tolerance} | Dev: {deviation} {symbol} {target_tolerance}"

    logger.info(log_msg)
    return in_tolerance
