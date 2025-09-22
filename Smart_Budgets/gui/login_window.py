import tkinter as tk
from tkinter import messagebox
from backend import user, budget
from gui.setup_wizard import SetupWizard
from gui.welcome_window import WelcomeWindow

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Smart Budget - Login")
        master.geometry("360x260")

        tk.Label(master, text="Welcome to Smart Budget", font=("Arial", 14, "bold")).pack(pady=10)

        form = tk.Frame(master)
        form.pack(pady=5)

        tk.Label(form, text="Username").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = tk.Entry(form, width=24)
        self.username_entry.grid(row=0, column=1)

        tk.Label(form, text="Password").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = tk.Entry(form, show="*", width=24)
        self.password_entry.grid(row=1, column=1)

        btns = tk.Frame(master)
        btns.pack(pady=10)

        tk.Button(btns, text="Login", width=12, command=self.login).grid(row=0, column=0, padx=6)
        tk.Button(btns, text="Sign Up", width=12, command=self.signup).grid(row=0, column=1, padx=6)

    def _open_next(self, username, user_id):
        self.master.destroy()
        if budget.user_has_setup(user_id):
            root = tk.Tk()
            WelcomeWindow(root, username, user_id)
            root.mainloop()
        else:
            root = tk.Tk()
            SetupWizard(root, username, user_id)
            root.mainloop()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        user_id = user.validate_login(username, password)
        if user_id:
            self._open_next(username, user_id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        uid = user.create_user(username, password)
        if uid:
            messagebox.showinfo("Sign Up", "Account created. Please log in.")
        else:
            messagebox.showerror("Sign Up Failed", "Username exists or invalid input.")
