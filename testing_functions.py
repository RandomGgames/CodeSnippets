"""
Function for checking if a measured value falls within the target range.
"""

import logging
import multiprocessing as mp
import platform
import sys
import time

logger = logging.getLogger()


def is_in_tolerance(experimental_value: float, target_value: float, target_tolerance: float, name: str = "measurement") -> bool:
    """
    Check whether a measured value falls within a specified target tolerance.

    This function compares an experimental value against a target value
    ± a specified tolerance. It logs a PASS/FAIL message including
    the deviation and symbolic comparison. Useful for engineering
    measurements, calibration checks, and automated validation.

    Parameters
    ----------
    experimental_value : float
        The value obtained from a measurement or test.
    target_value : float
        The expected reference value.
    target_tolerance : float
        The allowed deviation from the target value.
    name : str, optional
        Identifier used in log messages.

    Returns
    -------
    bool
        True if the value is within tolerance, False otherwise.
    """

    deviation = round(abs(experimental_value - target_value), 2)
    in_tolerance = (target_value - target_tolerance) <= experimental_value <= (target_value + target_tolerance)

    # Determine comparison symbol
    if deviation > target_tolerance:
        symbol = ">"
    elif deviation < target_tolerance:
        symbol = "<"
    else:
        symbol = "="

    status = "PASS" if in_tolerance else "FAIL"

    logger.info("%s | %s | Measured: %s | Target: %s±%s | Dev: %.2f %s", name, status, experimental_value, target_value, target_tolerance, deviation, symbol)

    return in_tolerance


def is_in_range(value: float, min_value: float, max_value: float, name: str = "value") -> bool:
    """
    Check whether a numeric value falls within a specified range.

    This function validates that a number is within the inclusive
    bounds [min_value, max_value]. It logs a PASS/FAIL message
    using the module logger and can be used for configuration
    validation, input checking, or general numeric tests.

    Parameters
    ----------
    value : float
        The number to check.
    min_value : float
        Lower bound of the allowed range.
    max_value : float
        Upper bound of the allowed range.
    name : str, optional
        Identifier used in log messages.

    Returns
    -------
    bool
        True if value is within the range, False otherwise.
    """

    in_range = min_value <= value <= max_value
    deviation = 0.0
    if value < min_value:
        deviation = min_value - value
    elif value > max_value:
        deviation = value - max_value

    status = "PASS" if in_range else "FAIL"
    symbol = "<" if value < min_value else ">" if value > max_value else "="

    logger.info("%s | %s | Value: %s | Range: [%s, %s] | Dev: %.2f %s", name, status, value, min_value, max_value, deviation, symbol)

    return in_range


def _timeout_worker(queue, func, args, kwargs):
    """Internal worker executed in a separate process."""
    try:
        result = func(*args, **kwargs)
        queue.put(("result", result))
    except Exception as e:
        queue.put(("error", e))


def run_with_timeout(func, timeout: float, *args, **kwargs):
    """
    Run a function with a time limit. If the function exceeds the
    timeout, the process is terminated.

    Parameters
    ----------
    func : callable
        Function to execute.
    timeout : float
        Maximum runtime in seconds.
    *args
        Positional arguments passed to the function.
    **kwargs
        Keyword arguments passed to the function.

    Returns
    -------
    Any
        Function return value.

    Raises
    ------
    TimeoutError
        If the function exceeds the allowed time.

    Examples
    --------
    >>> def slow():
    ...     import time
    ...     time.sleep(5)
    ...     return "done"

    >>> run_with_timeout(slow, 2)
    TimeoutError
    """

    queue = mp.Queue()

    process = mp.Process(
        target=_timeout_worker,
        args=(queue, func, args, kwargs)
    )

    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"Function '{func.__name__}' exceeded {timeout} seconds")

    if not queue.empty():
        status, value = queue.get()
        if status == "error":
            raise value
        return value

    return None


def _retry_timeout_worker(queue, func, args, kwargs):
    """Worker process that executes the target function."""
    try:
        result = func(*args, **kwargs)
        queue.put(("result", result))
    except Exception as e:
        queue.put(("error", e))


def retry_with_timeout(
    func,
    *args,
    timeout: float,
    retries: int = 3,
    delay: float = 0,
    timeout_return=None,
    exceptions=(Exception,),
    **kwargs,
):
    """
    Execute a function with retry and timeout protection.

    The function runs in a separate process so it can be forcefully
    terminated if it exceeds the specified timeout.

    Parameters
    ----------
    func : callable
        Function to execute.

    *args
        Positional arguments passed to the function.

    timeout : float
        Maximum execution time per attempt (seconds).

    retries : int, default=3
        Number of attempts before giving up.

    delay : float, default=0
        Delay between retries (seconds).

    timeout_return : Any, optional
        Value returned if all attempts time out. If None, a TimeoutError is raised.

    exceptions : tuple[type], default=(Exception,)
        Exceptions that should trigger a retry.

    **kwargs
        Keyword arguments passed to the function.

    Returns
    -------
    Any
        Result of the function.

    Raises
    ------
    TimeoutError
        If all attempts time out and timeout_return is None.

    Exception
        Re-raises the last exception if retries are exhausted.
    """

    last_exception = None

    for attempt in range(1, retries + 1):

        logger.info(
            "Executing %s (attempt %d/%d)",
            func.__name__,
            attempt,
            retries,
        )

        queue = mp.Queue()
        process = mp.Process(
            target=_retry_timeout_worker,
            args=(queue, func, args, kwargs),
        )

        start_time = time.perf_counter()
        process.start()
        process.join(timeout)
        runtime = time.perf_counter() - start_time

        if process.is_alive():
            process.terminate()
            process.join()

            logger.warning(
                "%s timed out after %.2f seconds (attempt %d/%d)",
                func.__name__,
                timeout,
                attempt,
                retries,
            )

            if attempt == retries:
                if timeout_return is not None:
                    logger.error(
                        "%s exceeded timeout after %d attempts. Returning fallback value.",
                        func.__name__,
                        retries,
                    )
                    return timeout_return

                raise TimeoutError(
                    f"{func.__name__} exceeded {timeout}s after {retries} attempts"
                )

        else:
            if not queue.empty():
                status, value = queue.get()

                if status == "result":
                    logger.info(
                        "%s completed successfully in %.3f seconds",
                        func.__name__,
                        runtime,
                    )
                    return value

                if status == "error":

                    if isinstance(value, exceptions):
                        last_exception = value

                        logger.warning(
                            "%s raised %s: %s (attempt %d/%d)",
                            func.__name__,
                            type(value).__name__,
                            value,
                            attempt,
                            retries,
                        )
                    else:
                        logger.exception(
                            "%s raised unexpected exception",
                            func.__name__,
                        )
                        raise value

        if attempt < retries and delay > 0:
            logger.debug("Retrying %s in %.2f seconds", func.__name__, delay)
            time.sleep(delay)

    if last_exception:
        logger.error(
            "%s failed after %d attempts",
            func.__name__,
            retries,
        )
        raise last_exception

    return timeout_return
