from tkinter import Tk, Label, Entry, Button, Listbox, StringVar, messagebox, END
from database_manager import DatabaseManager
from file_downloader import FileDownloader
from config import CONNECTION_STRING
import tkinter as tk
import threading

class FileDownloaderApp:
    
    def __init__(self, home):
        self.home = home
        
        self.db_manager = DatabaseManager(CONNECTION_STRING)
        output_folder = "C:/Downloads"  
        max_threads = 8  # number of threads for concurrency
        retry_limit = 3  
        self.file_downloader = FileDownloader(self.db_manager, output_folder, max_threads, retry_limit)
        
        self.home.title("File Downloader App")
        self.home.geometry("700x600")
        self.home.configure(bg="#148483")
        
        self.url_var = StringVar()
        
        Label(home, font=("Arial", 12, "bold"), bg="#148483", fg="white", text="Insert File URL:     ").place(x=50, y=20)
        Entry(home, textvariable=self.url_var, width=55).place(x=200, y=21)
        Button(home, text="Add URL", command=self.add_url, fg="black").place(x=550, y=15)
        Button(home, text="Start Downloads", command=self.start_downloads, fg="black").place(x=200, y=70)
        Button(home, text="View Download History", command=self.view_history, fg="black").place(x=400, y=70)
        Label(home, font=("Arial", 12, "bold"), bg="#148483", fg="white", text="Download Queue:").place(x=50, y=120)
        self.queue_listbox = Listbox(home, width=100, height=15)
        self.queue_listbox.place(x=50, y=150)
        
        self.load_queue()
           
    def add_url(self):
        url = self.url_var.get().strip()
        if url:
            self.db_manager.add_download(url)
            self.url_var.set("")
            self.load_queue()
            messagebox.showinfo("Success", "URL added to the download queue.")
        else:
            messagebox.showerror("Error", "Please enter a valid URL.")

    def load_queue(self):
        
        self.queue_listbox.delete(0, END)
        pending_downloads = self.db_manager.get_pending_downloads()
        
        for download_id, url, retry_count in pending_downloads:
            item_text = f"ID {download_id}: {url} (Retry: {retry_count})"
            self.queue_listbox.insert(END, item_text)
            
            btn_frame = tk.Frame(self.home, bg="#148483")
            tk.Button(btn_frame, text="Pause", command=lambda id=download_id: self.pause_download(id)).pack(side="left")
            tk.Button(btn_frame, text="Resume", command=lambda id=download_id: self.resume_download(id)).pack(side="left")
            tk.Button(btn_frame, text="Stop", command=lambda id=download_id: self.stop_download(id)).pack(side="left")
            tk.Button(btn_frame, text="Remove", command=lambda id=download_id: self.remove_download(id)).pack(side="left")
            btn_frame.pack()
            """for download_id, url, retry_count in pending_downloads:
            self.queue_listbox.insert(END, f"ID {download_id}: {url} (Retry: {retry_count})")"""
    
    def pause_download(self, download_id):
        self.file_downloader.pause_download(download_id)
        messagebox.showinfo("Info", f"Download {download_id} paused.")

    def resume_download(self, download_id):
        self.file_downloader.resume_download(download_id)
        messagebox.showinfo("Info", f"Download {download_id} resumed.")

    def stop_download(self, download_id):
        self.file_downloader.stop_download(download_id)
        messagebox.showinfo("Info", f"Download {download_id} stopped.")
    
    def remove_download(self, download_id):
        # Remove download from queue in FileDownloader
        self.file_downloader.remove_download(download_id)
        
        # Update database and reload queue
        self.db_manager.delete_download(download_id)  # Assuming a delete method exists
        self.load_queue()
        messagebox.showinfo("Info", f"Download {download_id} removed from the queue.")
    
    def start_downloads(self):
        threading.Thread(target=self._start_downloads, daemon=True).start()

    def _start_downloads(self):
        pending_downloads = self.db_manager.get_pending_downloads()
        for download_id, url, retry_count in pending_downloads:
            self.file_downloader.tasks.put((download_id, url, retry_count))
        self.file_downloader.start_downloading()
        self.load_queue()

    def view_history(self):
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
            bg_color = "#f0f0f0" if status.strip().casefold() == "complete" else "#ffd4d4" if status.strip().casefold() == "failed" else "#d4fdd4"

            tk.Label(frame, text=f"Record {idx}", font=("Arial", 10, "bold"), bg="#f0f0f0", anchor="w").pack(fill="x", pady=(10, 0))
            tk.Label(frame, text=f"URL: {url}", font=("Arial", 9), bg=bg_color, anchor="w").pack(fill="x", padx=10)
            tk.Label(frame, text=f"Status: {status}", font=("Arial", 9), bg=bg_color, anchor="w").pack(fill="x", padx=10)
            tk.Label(frame, text=f"Local File Path: {file_path}", font=("Arial", 9), bg=bg_color, anchor="w").pack(fill="x", padx=10)
   
   