"""
Function for checking if a measured value falls within the target range.
"""

import logging
import multiprocessing as mp
import platform
import sys
import time

logger = logging.getLogger()


def test_measurement(
    name: str,
    measured: float,
    min_val: float | None = None,
    max_val: float | None = None,
    tolerance: float | None = None,
    target: float | None = None,
    units: str = "",
) -> bool:
    """
    Log a standardized test result and automatically determine PASS/FAIL.

    The function evaluates the measured value against one of the following
    conditions (in priority order):

    1. Range check (min_val / max_val)
    2. Target with tolerance
    3. Exact target match

    Returns
    -------
    bool
        True if the test passed, False if it failed.
    """

    status: bool | None = None
    deviation: float | None = None

    if min_val is not None or max_val is not None:
        lower = min_val if min_val is not None else float("-inf")
        upper = max_val if max_val is not None else float("inf")
        status = lower <= measured <= upper

    elif target is not None and tolerance is not None:
        lower = target - tolerance
        upper = target + tolerance
        status = lower <= measured <= upper
        deviation = abs(measured - target)

    elif target is not None:
        status = measured == target
        deviation = abs(measured - target)

    else:
        logger.warning("Test '%s' has no comparison criteria.", name)
        return False

    status_str = "PASS" if status else "FAIL"

    parts: list[str] = [name, status_str]
    parts.append(f"Measured: {measured}{units}")

    if target is not None and tolerance is not None:
        parts.append(f"Target: {target}±{tolerance}{units}")
        if deviation is not None:
            parts.append(f"Dev: {round(deviation, 6)}{units}")

    elif target is not None:
        parts.append(f"Target: {target}{units}")
        if deviation is not None:
            parts.append(f"Dev: {round(deviation, 6)}{units}")

    elif min_val is not None or max_val is not None:
        lower_str = f"{min_val}{units}" if min_val is not None else f"-inf{units}"
        upper_str = f"{max_val}{units}" if max_val is not None else f"inf{units}"
        parts.append(f"Range: {lower_str} to {upper_str}")

    message = " | ".join(parts)
    logger.info("%s", message)

    return status


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
