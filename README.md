# File Downloader App

## Overview
The File Downloader App is a Python-based GUI application for managing file downloads. It allows users to queue URLs, track download progress, and maintain a history of completed and failed downloads. 
It supports multithreading to enhance download speed and efficiency.

---

## Features
- Add URLs to a download queue.
- Support for multithreaded downloads.
- Retry mechanism for failed downloads.
- View and manage the download queue.
- Display download history with status and local file paths.
- Progress bars for ongoing downloads.

---

## Prerequisites
1. Python 3.8 or higher
2. Required Python libraries:
   - `tkinter`
   - `requests`
   - `tqdm`
   - `threading`
   - `concurrent.futures`

Install dependencies via pip:
```bash
pip install requests tqdm
```

## Configuration
Modify the CONNECTION_STRING in the config.py file to point to the appropriate database.

## Multithreading
When starting the app, you can enable multithreading for faster downloads. You will be prompted to specify the number of threads (1-8).

## Modules

1. FileDownloaderApp (GUI)
Handles the graphical user interface using Tkinter.
Allows users to add URLs, start downloads, and view history.
Connects to DatabaseManager and FileDownloader.

2. FileDownloader
Handles downloading files with multithreading and retries.

3. DatabaseManager
Handles database operations:
Add download URLs.
Retrieve pending downloads.
Update download status (completed, failed).

4. config.py
Stores configuration details: CONNECTION_STRING.

