import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# ================= DATABASE =================
conn = sqlite3.connect("banking.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    balance REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    type TEXT,
    amount REAL,
    date TEXT
)
""")

conn.commit()

# ================= APP =================
root = tk.Tk()
root.title("Banking System")
root.geometry("420x520")

current_user = None


# ================= PLACEHOLDER ENTRY =================
def create_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg="grey")

    def on_focus_in(e):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def on_focus_out(e):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg="grey")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


# ================= CLEAR SCREEN =================
def clear():
    for widget in root.winfo_children():
        widget.destroy()


# ================= REGISTER SCREEN =================
def register_screen():
    clear()

    tk.Label(root, text="REGISTER", font=("Arial", 18, "bold")).pack(pady=20)

    username_entry = tk.Entry(root, font=("Arial", 12))
    username_entry.pack(pady=5)
    create_placeholder(username_entry, "Username or Email")

    password_entry = tk.Entry(root, font=("Arial", 12))
    password_entry.pack(pady=5)
    create_placeholder(password_entry, "Password")


    def register():
        user = username_entry.get()
        pw = password_entry.get()

        if user == "" or user == "Username or Email" or pw == "" or pw == "Password":
            messagebox.showerror("Error", "Fill all fields")
            return

        try:
            cursor.execute(
                "INSERT INTO users(username, password) VALUES (?,?)",
                (user, pw)
            )
            conn.commit()
            messagebox.showinfo("Success", "Account created! Please login.")
            login_screen()
        except:
            messagebox.showerror("Error", "Username already exists")


    tk.Button(root, text="Register", command=register, bg="green", fg="white").pack(pady=10)
    tk.Button(root, text="Go to Login", command=login_screen).pack()


# ================= LOGIN SCREEN =================
def login_screen():
    clear()

    tk.Label(root, text="LOGIN", font=("Arial", 18, "bold")).pack(pady=20)

    username_entry = tk.Entry(root, font=("Arial", 12))
    username_entry.pack(pady=5)
    create_placeholder(username_entry, "Username or Email")

    password_entry = tk.Entry(root, font=("Arial", 12))
    password_entry.pack(pady=5)
    create_placeholder(password_entry, "Password")


    def login():
        global current_user

        user = username_entry.get()
        pw = password_entry.get()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user, pw)
        )

        result = cursor.fetchone()

        if result:
            current_user = user
            dashboard()
        else:
            messagebox.showerror("Error", "Invalid login")


    tk.Button(root, text="Login", command=login, bg="blue", fg="white").pack(pady=10)
    tk.Button(root, text="Go to Register", command=register_screen).pack()


# ================= DASHBOARD =================
def dashboard():
    clear()

    tk.Label(root, text=f"Welcome {current_user}", font=("Arial", 16, "bold")).pack(pady=10)

    cursor.execute("SELECT balance FROM users WHERE username=?", (current_user,))
    balance = cursor.fetchone()[0]

    tk.Label(root, text=f"Balance: ₱{balance:.2f}", fg="green").pack(pady=5)

    amount_entry = tk.Entry(root)
    amount_entry.pack(pady=10)


    def get_amount():
        try:
            value = float(amount_entry.get())
            if value <= 0:
                raise ValueError
            return value
        except:
            messagebox.showerror("Error", "Invalid amount")
            return None


    def deposit():
        amount = get_amount()
        if amount is None:
            return

        cursor.execute("UPDATE users SET balance = balance + ? WHERE username=?",
                       (amount, current_user))

        cursor.execute("INSERT INTO transactions VALUES (NULL,?,?,?,?)",
                       (current_user, "Deposit", amount,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        messagebox.showinfo("Success", "Deposited")
        dashboard()


    def withdraw():
        amount = get_amount()
        if amount is None:
            return

        cursor.execute("SELECT balance FROM users WHERE username=?", (current_user,))
        bal = cursor.fetchone()[0]

        if amount > bal:
            messagebox.showerror("Error", "Insufficient balance")
            return

        cursor.execute("UPDATE users SET balance = balance - ? WHERE username=?",
                       (amount, current_user))

        cursor.execute("INSERT INTO transactions VALUES (NULL,?,?,?,?)",
                       (current_user, "Withdraw", amount,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        messagebox.showinfo("Success", "Withdraw successful")
        dashboard()


    def history():
        win = tk.Toplevel(root)
        win.title("History")
        win.geometry("400x350")

        tree = ttk.Treeview(win, columns=("Type", "Amount", "Date"), show="headings")
        tree.heading("Type", text="Type")
        tree.heading("Amount", text="Amount")
        tree.heading("Date", text="Date")
        tree.pack(fill="both", expand=True)

        cursor.execute("SELECT type, amount, date FROM transactions WHERE username=?",
                       (current_user,))

        for row in cursor.fetchall():
            tree.insert("", "end", values=row)


    tk.Button(root, text="Deposit", command=deposit, bg="green", fg="white").pack(pady=5)
    tk.Button(root, text="Withdraw", command=withdraw, bg="red", fg="white").pack(pady=5)
    tk.Button(root, text="History", command=history).pack(pady=5)
    tk.Button(root, text="Logout", command=login_screen).pack(pady=10)


# ================= START =================
login_screen()
root.mainloop()