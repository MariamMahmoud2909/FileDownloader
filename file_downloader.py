import os
import threading
import requests
from tqdm import tqdm
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Event
import time
class FileDownloader:
    def __init__(self, db_manager, output_folder, max_threads, retry_limit):
        self.db_manager = db_manager
        self.output_folder = output_folder
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        self.retry_limit = retry_limit
        self.lock = threading.Lock()
        self.tasks = Queue()
        self.download_states = {}  
        self.pause_events = {}
        os.makedirs(output_folder, exist_ok=True)
        
    def download_file(self, download_id, url, retry_count):
        start_time = time.time()
        local_filename = os.path.join(self.output_folder, os.path.basename(url))
        self.download_states[download_id] = "running"
        self.pause_events[download_id] = Event()
        self.pause_events[download_id].set()

        try:
            with requests.get(url, stream=True, timeout=10) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                with open(local_filename, 'wb') as file, tqdm(
                        desc=os.path.basename(url),
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024
                ) as progress:
                    for chunk in response.iter_content(chunk_size=8192):
                        self.pause_events[download_id].wait()  # Wait if paused
                        if self.download_states[download_id] == "stopped":
                            raise Exception("Download stopped by user.")
                        file.write(chunk)
                        progress.update(len(chunk))
                    end_time = time.time()
                    total_time = end_time - start_time
                    total_mins = int(total_time // 60)
                    total_secs = int(total_time % 60)
                    total_millisecs = int((total_time - total_secs) * 1000)
                    print(f"Download {download_id} for {url} completed in\n {total_mins} minutes and {total_secs} seconds and {total_millisecs} milliseconds.")
            with self.lock:
                self.db_manager.update_download(download_id, 'Completed', local_filename)
        except Exception as e:
            with self.lock:
                if retry_count < self.retry_limit and self.download_states[download_id] != "stopped":
                    self.db_manager.update_download(download_id, 'Pending', retry_count=retry_count + 1)
                    self.tasks.put((download_id, url, retry_count + 1))
                else:
                    self.db_manager.update_download(download_id, 'Failed')
                print(f"Failed to download {url}: {e}")
        finally:
            del self.download_states[download_id]
            del self.pause_events[download_id]
    
    def remove_download(self, download_id):
        with self.lock:
            remaining_tasks = []
            while not self.tasks.empty():
                task = self.tasks.get()
                if task[0] != download_id:
                    remaining_tasks.append(task)
            for task in remaining_tasks:
                self.tasks.put(task)

        self.db_manager.update_download(download_id, 'Removed')
    
    def pause_download(self, download_id):
        if download_id in self.download_states and self.download_states[download_id] == "running":
            self.download_states[download_id] = "paused"
            self.pause_events[download_id].clear()

    def resume_download(self, download_id):
        if download_id in self.download_states and self.download_states[download_id] == "paused":
            self.download_states[download_id] = "running"
            self.pause_events[download_id].set()

    def start_downloading(self):
        while not self.tasks.empty():
            download_id, url, retry_count = self.tasks.get()
            self.executor.submit(self.download_file, download_id, url, retry_count)
   