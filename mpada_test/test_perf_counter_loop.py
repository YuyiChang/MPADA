# %%
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def task():
    # print("Performing the task...")
    # time.sleep(0)
    a = np.random.rand(100, 100)
    # For demonstration, let's just return an array containing the current time
    # return [time.strftime("%H:%M:%S")]
    return time.perf_counter()

def perform_task_every_n_seconds(n, results, iterations_event, max_iterations):
    for i in tqdm(range(max_iterations)):
        start_time = time.perf_counter()
        result = task()
        # results.append(result)
        results[i] = result
        elapsed_time = time.perf_counter() - start_time
        sleep_time = max(0, n - elapsed_time)
        time.sleep(sleep_time)
        
        # # Wait until the desired interval has passed
        # while time.perf_counter() - start_time < interval_seconds:
        #     pass
    iterations_event.set()  # Signal that all iterations are completed

# Set the time interval (in seconds) for performing the task
interval_seconds = 0.05

# Create a threading event to synchronize when all iterations are completed
iterations_event = threading.Event()

# Define the maximum number of iterations
max_iterations = 1000

# Create an empty list to store the results
all_results = [None] * max_iterations

print(max_iterations * interval_seconds)

# Create a thread to perform the task every interval_seconds
task_thread = threading.Thread(target=perform_task_every_n_seconds, args=(interval_seconds, all_results, iterations_event, max_iterations))
task_thread.daemon = True  # Set the thread as daemon so it will exit when the main program exits
task_thread.start()

# Wait for all iterations to complete
iterations_event.wait()

# Once all iterations are completed, save the data to a file or perform any other necessary action
print("All iterations completed. Saving data...")
# For demonstration, let's print the collected results
# print("Collected results:", all_results)


timestamps = np.array(all_results)
timeinterval = np.diff(timestamps)

# print(timeinterval)

fig = plt.figure()
# plt.plot(timeinterval)
plt.hist(timeinterval)
fig.savefig('out.jpg')

