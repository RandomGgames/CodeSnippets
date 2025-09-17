import logging
logger = logging.getLogger()


def is_in_tolerance(experimental_value: float | int, target_value: float | int, target_tolerance: float | int, name: str) -> bool:
    try:
        deviation = round(abs(experimental_value - target_value), 2)
        deviation_comparision = '>' if deviation > target_tolerance else '<' if deviation < target_tolerance else '='
        is_in_tolerance = True if experimental_value >= target_value - target_tolerance and experimental_value <= target_value + target_tolerance else False
        if is_in_tolerance == True:
            logger.info(f'"{name}": In tolerance: "{is_in_tolerance}". Expected: {target_value}±{target_tolerance} A. Measured: {experimental_value} A. Deviation: {deviation} {deviation_comparision} {target_tolerance}.')
            return True
        else:
            logger.warning(f'"{name}": In tolerance: "{is_in_tolerance}". Expected: {target_value}±{target_tolerance} A. Measured: {experimental_value} A. Deviation: {deviation} {deviation_comparision} {target_tolerance}.')
            return False
    except Exception as e:
        raise e
