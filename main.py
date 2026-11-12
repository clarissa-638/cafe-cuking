import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from admin import create_admin_frame
from kasir import create_kasir_frame
from waiter import create_waiter_frame
from pembeli import create_pembeli_frame


# Fungsi Login
def login():
    username = entry_username.get()
    password = entry_password.get()

    users = {
        "admin": {"password": "admin", "role": "admin"},
        "kasir": {"password": "kasir", "role": "kasir"},
        "waiter": {"password": "waiter", "role": "waiter"},
        "pembeli": {"password": "pembeli", "role": "pembeli"}
    }

    if username in users and password == users[username]["password"]:
        role = users[username]["role"]
        login_frame.place_forget()

        if role == "admin":
            admin_frame.place(x=0, y=0, relwidth=1, relheight=1)
        elif role == "kasir":
            kasir_frame.place(x=0, y=0, relwidth=1, relheight=1)
        elif role == "waiter":
            waiter_frame.place(x=0, y=0, relwidth=1, relheight=1)
        elif role == "pembeli":
            pembeli_frame.place(x=0, y=0, relwidth=1, relheight=1)
    else:
        messagebox.showerror("Login Gagal", "Username atau password salah!")


# Fungsi Logout
def logout():
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

    admin_frame.place_forget()
    kasir_frame.place_forget()
    waiter_frame.place_forget()
    pembeli_frame.place_forget()

    login_frame.place(x=0, y=0, relwidth=1, relheight=1)


# Window Utama
window = tk.Tk()
window.title("Welcome to Purrfect Day")
window.state("zoomed")
window.resizable(True, True)
window.configure(bg="#FFF8F0")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()


# Halaman Login
login_frame = tk.Frame(window, bg="#FFF8F0")
login_frame.place(x=0, y=0, relwidth=1, relheight=1)

# Background gambar hanya untuk Login
background_image = Image.open("background.jpg")
background_image = background_image.resize((screen_width, screen_height))
background_photo = ImageTk.PhotoImage(background_image)

login_background = tk.Label(login_frame, image=background_photo)
login_background.place(x=0, y=0, relwidth=1, relheight=1)

# Card Login
card = tk.Frame(
    login_frame,
    bg="#FFFBF7",
    width=440,
    height=530,
    highlightbackground="#D9C3B0",
    highlightthickness=2
)
card.place(relx=0.5, rely=0.5, anchor="center")
card.pack_propagate(False)

# Logo
logo_image = Image.open("logopurr.png")
logo_image = logo_image.resize((150, 150))
logo = ImageTk.PhotoImage(logo_image)

logo_label = tk.Label(card, image=logo, bg="#FFFBF7")
logo_label.pack(pady=(28, 10))

# Judul
judul = tk.Label(
    card,
    text="──── Cafe Login ────",
    font=("Poppins", 24, "bold"),
    bg="#FFFBF7",
    fg="#5C3A21"
)
judul.pack(pady=(0, 18))

# Username
label_username = tk.Label(
    card,
    text="Username",
    font=("Poppins", 11, "bold"),
    bg="#FFFBF7",
    fg="#6E4A35"
)
label_username.pack()

entry_username = tk.Entry(
    card,
    font=("Poppins", 11),
    bg="#FFFFFF",
    fg="#402721",
    relief="solid",
    bd=1,
    highlightbackground="#D9C3B0",
    width=22
)
entry_username.pack(pady=(6, 12), ipady=6)

# Password
label_password = tk.Label(
    card,
    text="Password",
    font=("Poppins", 11, "bold"),
    bg="#FFFBF7",
    fg="#6E4A35"
)
label_password.pack()

entry_password = tk.Entry(
    card,
    font=("Poppins", 11),
    bg="#FFFFFF",
    fg="#402721",
    relief="solid",
    bd=1,
    highlightbackground="#D9C3B0",
    width=22,
    show="*"
)
entry_password.pack(pady=(6, 22), ipady=6)

# Tombol Login
login_button = tk.Button(
    card,
    text="Login",
    font=("Poppins", 11, "bold"),
    bg="#C88A75",
    fg="white",
    activebackground="#B27460",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=login,
    width=10
)
login_button.pack(ipady=6)

# Footer
footer = tk.Label(
    card,
    text="By Clarissa, Jolin, Intan",
    font=("Poppins", 9),
    bg="#FFFBF7",
    fg="#A08375"
)
footer.pack(side="bottom", pady=15)


# Membuat halaman untuk setiap role
admin_frame = create_admin_frame(window, logout)
kasir_frame = create_kasir_frame(window, logout)
waiter_frame = create_waiter_frame(window, logout)
pembeli_frame = create_pembeli_frame(window, logout)

# Jalankan Program
window.mainloop()
