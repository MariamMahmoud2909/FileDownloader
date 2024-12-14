import random
import time
import winsound
import tkinter as tk
import threading
import re
from tkinter import Tk, Label, Entry, Button, Listbox, StringVar, Toplevel, messagebox, END, simpledialog, ttk
from database_manager import DatabaseManager
from file_downloader import FileDownloader
from config import CONNECTION_STRING

class FileDownloaderApp:
   
    #Handles the GUI using Tkinter, and integrates database and downloading functionalities.
    def __init__(self, home):
        """Initializes the application, sets up the GUI, and integrates supporting modules."""
        
        self.db_manager = DatabaseManager(CONNECTION_STRING)
        output_folder = "C:/Downloads"  
        
        self.use_multithreading = False
        self.max_threads = 1  # number of threads for concurrency
        self.retry_limit = 3  
        
        self.file_downloader = FileDownloader(self.db_manager, output_folder, self.max_threads, self.retry_limit)
    
        self.setup_dialog()
        
        self.home = home        
        self.home.title("File Downloader App")
        self.home.geometry("700x600")
        self.home.configure(bg="#148483")
        
        self.url_var = StringVar() #Stores the URL input from the user.
        
        Label(home, font=("Arial", 12, "bold"), bg="#148483", fg="white", text="Insert File URL:     ").place(x=50, y=20)
        Entry(home, textvariable=self.url_var, width=55).place(x=200, y=21)
        
        Button(home, text="Add URL", command=self.add_url, fg="black").place(x=550, y=15)
        Button(home, text="Start Downloads", command=self.start_downloads, fg="black").place(x=200, y=70)
        Button(home, text="View Download History", command=self.view_history, fg="black").place(x=400, y=70)
        
        Label(home, font=("Arial", 12, "bold"), bg="#148483", fg="white", text="Download Queue:").place(x=50, y=120)
        self.queue_listbox = Listbox(home, width=100, height=15)
        self.queue_listbox.place(x=50, y=150)
        
        self.load_queue()# Load pending downloads into the queue  
      
    def setup_dialog(self):
        """Configures whether downloads will use multithreading or download using a single thread."""
        response = messagebox.askyesno("Multithreading", "Do you want to use multithreading for downloads?")
        if response:
            self.use_multithreading = True
            self.max_threads = simpledialog.askinteger("Threads", "Enter the number of threads to use (2-8):", minvalue=2, maxvalue=8)
            if self.max_threads is None:  # User cancels during thread selection
                self.home.destroy()       # If the user cancels, close the application
                return
        else:
            self.use_multithreading = False
            self.max_threads = 1
    
    def add_url(self):    
        """Handles adding URLs to the download queue. Uses a Regex to check for the URL validity"""         
        url = self.url_var.get().strip()
        url_regex = re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
        if url and re.fullmatch(url_regex,url):
            self.db_manager.add_download(url)
            self.url_var.set("")
            self.load_queue()
            messagebox.showinfo("Success", "URL added to the download queue.")
        else:
            messagebox.showerror("Error", "Please enter a valid URL.")

    def load_queue(self): 
        """Fetches pending downloads from the database and populates the queue listbox."""
        self.queue_listbox.delete(0, END)# Clear the current queue display
        pending_downloads = self.db_manager.get_pending_downloads()
        
        for download_id, url, retry_count in pending_downloads:
            item_text = f"ID {download_id}: {url} (Retry: {retry_count})"
            self.queue_listbox.insert(tk.END, item_text)
    
    def start_downloads(self): 
        """Starts the download process in a separate thread
        Target (_start_downloads): Specifies which method to execute in the new thread.
        (daemon=True): The thread will automatically terminate when the main program exits"""
        threading.Thread(target=self._start_downloads, daemon=True).start()

   
    def _start_downloads(self):
        """Starts the download process:
        - Opens a new progress bar window for each download (if it is a multithreaded download).
        - Distributes downloads based on threading settings."""
        pending_downloads = self.db_manager.get_pending_downloads()
        if not pending_downloads:
            messagebox.showinfo("No Downloads", "No pending downloads in the queue.")
            return
         # Add pending downloads to the FileDownloader tasks queue 
        for download_id, url, retry_count in pending_downloads:
            self.file_downloader.tasks.put((download_id, url, retry_count))

        progress_windows = []
        for download_id, url, retry_count in pending_downloads:
            progress_window = self.create_progress_window(download_id, url)
            progress_windows.append((progress_window, download_id, url, retry_count))
        for progress_window, download_id, url, retry_count in progress_windows:
            threading.Thread(target=self.download_file, args=(download_id, url, retry_count, progress_window), daemon=True).start()

        self.file_downloader.start_downloading()
        self.load_queue()
        #messagebox.showinfo("Downloads Completed", "All downloads have finished!")

    def create_progress_window(self, download_id, url):
        """Uses progress bars to display download status."""
        progress_window = Toplevel(self.home)
        progress_window.title(f"Download {download_id}")
        progress_window.geometry(f"300x100+{random.randint(100, 500)}+{random.randint(100, 500)}")
        Label(progress_window, text=f"Downloading: {url}", wraplength=250).pack(pady=10)
        progress_bar = ttk.Progressbar(progress_window, mode="determinate", length=250)
        progress_bar.pack(pady=10)
        progress_bar["value"] = 0
        progress_window.progress_bar = progress_bar
        return progress_window

    def download_file(self, download_id, url, retry_count, progress_window):
        """Simultaes the download Progress, marks downloads as completed or failed based on the outcome."""
        try:
           # Simulate downloading with a progress bar update
            for i in range(100): 
                time.sleep(random.uniform(0.05, 0.1))
                progress_window.progress_bar["value"] = i + 1
                progress_window.update_idletasks()
            #self.db_manager.mark_completed(download_id)
        except Exception as e:
            self.db_manager.mark_failed(download_id)
            winsound.Beep(1000, 500) 
        finally:
             # Close the progress window after the download finishes
            time.sleep(5)
            progress_window.destroy()

    def view_history(self):
        """Opens a window displaying the download history with success and failure details."""
        history = self.db_manager.get_download_history()
        history_window = Tk()
        
        history_window.title("Download History")
        history_window.geometry("600x400")
        
        canvas = tk.Canvas(history_window, bg="#f0f0f0")
        scroll_y = tk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        
        frame = tk.Frame(canvas, bg="#f0f0f0")
        frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        for idx, (url, status, file_path) in enumerate(history, start=1):
            bg_color = "#d4fdd4" if status.strip().casefold() == "completed" else "#ffd4d4" if status.strip().casefold() == "failed" else "red"
            
            tk.Label(frame, text=f"Record {idx}", font=("Arial", 10, "bold"), bg="#f0f0f0", anchor="w").pack(fill="x", pady=(10, 0))
            tk.Label(frame, text=f"URL: {url}", font=("Arial", 9), bg=bg_color, anchor="w").pack(fill="x", padx=10)
            tk.Label(frame, text=f"Status: {status}", font=("Arial", 9), bg=bg_color, anchor="w").pack(fill="x", padx=10)
            tk.Label(frame, text=f"Local File Path: {file_path}", font=("Arial", 9), bg=bg_color, anchor="w").pack(fill="x", padx=10)  