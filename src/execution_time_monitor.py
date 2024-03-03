# execution_time_monitor.py
import time


def execution_time_monitor(func):
    """
    A decorator to monitor the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time  # Calculate the execution time
        print(f"[Execution time of {func.__name__}: {execution_time:.4f} seconds]")
        return result
    return wrapper
