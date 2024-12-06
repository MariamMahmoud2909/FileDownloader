from tkinter import Tk
from gui import FileDownloaderApp

if __name__ == "__main__":
    home = Tk()
    app = FileDownloaderApp(home)
    home.mainloop()