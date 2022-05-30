import tkinter as tk
from tkinter import messagebox

class Win: # Popup window to show alerts
    def popup(self, title="", message=""):
        tk.Tk().withdraw()
        name = messagebox.showwarning(title=title, message=message)
            