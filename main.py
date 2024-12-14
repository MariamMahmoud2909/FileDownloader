from tkinter import Tk
from gui import FileDownloaderApp

if __name__ == "__main__":
    home = Tk() # inits the main app window for gui app [root window]
    home.withdraw()
    app = FileDownloaderApp(home)
    home.deiconify()
    home.mainloop()