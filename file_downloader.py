import os
import threading
import requests
from tqdm import tqdm
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Event
import time

class FileDownloader:
    #Supports multithreading, retry logic, and download progress tracking.
    
    def __init__(self, db_manager, output_folder, max_threads, retry_limit):
        self.db_manager = db_manager
        self.output_folder = output_folder
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        self.retry_limit = retry_limit
        self.lock = threading.Lock() #ensure thread-safe operations when accessing shared resources
        self.tasks = Queue() # Queue to store download tasks
        self.download_states = {}  
        os.makedirs(output_folder, exist_ok=True) # Creates the output folder if it doesn't exist.
        
    def download_file(self, download_id, url, retry_count):
        """
        Downloads a file from the given URL with progress tracking and retry logic.
        """
        start_time = time.time()
        local_filename = os.path.join(self.output_folder, os.path.basename(url))
        self.download_states[download_id] = "running"

        try:
            # Perform an HTTP GET request with streaming enabled.
            with requests.get(url, stream=True, timeout=10) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                with open(local_filename, 'wb') as file, tqdm(
                        desc=os.path.basename(url), # Display the file name in the progress bar.
                        total=total_size,
                        unit='B', # Unit for progress (bytes).
                        unit_scale=True,
                        unit_divisor=1024
                ) as progress:
                    # Write data in chunks and update the progress bar.
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                        progress.update(len(chunk))
                    end_time = time.time()
                    total_time = end_time - start_time
                    total_mins = int(total_time // 60)
                    total_secs = int(total_time % 60)
                    total_millisecs = int((total_time - total_secs) * 1000)
                    print(f"Download {download_id} for {url} completed in\n {total_mins} minutes and {total_secs} seconds and {total_millisecs} milliseconds.")
            
            # Update the database with the download completion status.
            with self.lock:
                self.db_manager.update_download(download_id, 'Completed', local_filename)
        except Exception as e:
            with self.lock:
                if retry_count < self.retry_limit:
                    self.db_manager.update_download(download_id, 'Pending', retry_count=retry_count + 1)
                    self.tasks.put((download_id, url, retry_count + 1))
                else:
                    self.db_manager.update_download(download_id, 'Failed')
                print(f"Failed to download {url}: {e}")

    def start_downloading(self):
        """
        Starts the download process by consuming tasks from the queue.
        Uses a thread pool executor to run downloads concurrently.
        """
        while not self.tasks.empty(): 
            download_id, url, retry_count = self.tasks.get()
            self.executor.submit(self.download_file, download_id, url, retry_count)   # Submit the task to the thread pool.
   