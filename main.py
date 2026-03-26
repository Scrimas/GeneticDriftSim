import customtkinter as ctk
from gui import DriftGUI
import ctypes
import os

def main() -> None:
    if os.name == 'nt':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    DriftGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
