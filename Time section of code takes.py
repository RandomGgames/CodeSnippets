import time

# Run this at the start of the function
start_time = time.perf_counter()

print(f'Start')
time.sleep(1)
print(f'End')

# Run this at the end of function
end_time = time.perf_counter()
duration = end_time - start_time
print(f'Took {duration:.10f}s to complete.')
