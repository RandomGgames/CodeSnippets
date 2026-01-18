"""
An example of how to measure the time it takes to run a section of code
"""

import time
import logging

logger = logging.getLogger(__name__)


# Run this at the start of the function
start_ns = time.perf_counter_ns()

print("Start")
time.sleep(1)
print("End")

end_ns = time.perf_counter_ns()
duration_s = (end_ns - start_ns) / 1e9
print(f"Execution completed in {duration_s}s.")
