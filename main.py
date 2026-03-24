from __future__ import annotations
import tkinter as tk
from gui import DriftGUI
import ctypes
import os

def main() -> None:
    if os.name == 'nt':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()

    root: tk.Tk = tk.Tk()
    DriftGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
