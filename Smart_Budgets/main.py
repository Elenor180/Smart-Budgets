import tkinter as tk
from gui.login_window import LoginWindow

def main():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()

