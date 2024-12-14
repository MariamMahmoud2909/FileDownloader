from tkinter import Tk
from gui import FileDownloaderApp

if __name__ == "__main__":
    home = Tk() # inits the main app window fir gui app [root window]
    app = FileDownloaderApp(home)
    home.mainloop()