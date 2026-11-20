import tkinter as tk
from tkinter import messagebox, simpledialog


def create_waiter_frame(parent, on_logout=None):

    # Frame utama waiter
    waiter_frame = tk.Frame(
        parent,
        bg="#F5E6E0"
    )

    # Header Layout Meja
    header_waiter = tk.Frame(
        waiter_frame,
        bg="#E8C6B8",
        height=60
    )

    header_waiter.pack(fill="x")
    header_waiter.pack_propagate(False)

    tk.Label(
        header_waiter,
        text="◉ Layout Meja",
        font=("Poppins", 18, "bold"),
        bg="#E8C6B8",
        fg="#6E4A35"
    ).pack(expand=True)

    # Area daftar meja
    meja_container = tk.Frame(
        waiter_frame,
        bg="#F5E6E0"
    )

    meja_container.place(
        relx=0.025,
        rely=0.09,
        relwidth=0.95,
        relheight=0.80
    )

    # Mengatur ukuran kolom
    for kolom in range(5):
        meja_container.grid_columnconfigure(
            kolom,
            weight=1,
            uniform="meja"
        )

    # Mengatur ukuran baris
    for baris in range(2):
        meja_container.grid_rowconfigure(
            baris,
            weight=1,
            uniform="meja"
        )

    # Menyimpan status meja
    status_meja = {
        nomor: {
            "status": "KOSONG",
            "nama": ""
        }
        for nomor in range(1, 11)
    }

    tombol_meja_list = {}

    # Fungsi memperbarui tampilan meja
    def update_meja(nomor):

        data = status_meja[nomor]
        tombol = tombol_meja_list[nomor]

        if data["status"] == "KOSONG":

            tombol.config(
                text=f"Meja {nomor}\nKOSONG",
                font=("Poppins", 17, "bold"),
                wraplength=0,
                justify="center",
                bg="#FFF8F0",
                fg="#6E4A35",
                activebackground="#E8C6B8"
            )

        else:

            tombol.config(
                text=(
                    f"Meja {nomor}\n"
                    f"DIBOOKING\n"
                    f"Atas nama: {data['nama']}"
                ),
                font=("Poppins", 12, "bold"),
                wraplength=280,
                justify="center",
                bg="#D9A18F",
                fg="white",
                activebackground="#C88A75"
            )

    # Fungsi booking meja
    def booking_meja(nomor):

        data = status_meja[nomor]

        # Jika meja kosong
        if data["status"] == "KOSONG":

            nama = simpledialog.askstring(
                "Booking Meja",
                f"Meja {nomor}\nAtas nama siapa?",
                parent=waiter_frame.winfo_toplevel()
            )

            if nama is None:
                return

            nama = nama.strip()

            if nama == "":
                messagebox.showwarning(
                    "Nama Kosong",
                    "Silakan masukkan nama pelanggan!",
                    parent=waiter_frame.winfo_toplevel()
                )
                return

            data["status"] = "DIBOOKING"
            data["nama"] = nama

            update_meja(nomor)

            messagebox.showinfo(
                "Booking Berhasil",
                f"Meja {nomor} berhasil dibooking "
                f"atas nama {nama}.",
                parent=waiter_frame.winfo_toplevel()
            )

        # Jika meja sudah dibooking
        else:

            pilihan = messagebox.askyesno(
                "Selesaikan Booking",
                f"Meja {nomor} sedang dibooking "
                f"atas nama {data['nama']}.\n\n"
                "Apakah booking ingin diselesaikan?",
                parent=waiter_frame.winfo_toplevel()
            )

            if pilihan:

                data["status"] = "KOSONG"
                data["nama"] = ""

                update_meja(nomor)

                messagebox.showinfo(
                    "Booking Selesai",
                    f"Meja {nomor} sekarang sudah kosong.",
                    parent=waiter_frame.winfo_toplevel()
                )

    # Membuat 10 meja
    for nomor in range(1, 11):

        baris = (nomor - 1) // 5
        kolom = (nomor - 1) % 5

        meja_card = tk.Frame(
            meja_container,
            bg="#FFF8F0"
        )

        meja_card.grid(
            row=baris,
            column=kolom,
            padx=12,
            pady=12,
            sticky="nsew"
        )

        tombol_meja = tk.Button(
            meja_card,
            text=f"Meja {nomor}\nKOSONG",
            font=("Poppins", 17, "bold"),
            bg="#FFF8F0",
            fg="#6E4A35",
            activebackground="#E8C6B8",
            activeforeground="#6E4A35",
            relief="flat",
            cursor="hand2",
            command=lambda n=nomor: booking_meja(n)
        )

        tombol_meja.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        tombol_meja_list[nomor] = tombol_meja

    # Tombol Keluar
    def keluar():

        if on_logout is not None:
            on_logout()
        else:
            waiter_frame.pack_forget()

    waiter_logout = tk.Button(
        waiter_frame,
        text="Keluar",
        font=("Poppins", 11),
        bg="#E8C6B8",
        fg="#402721",
        activebackground="#D2A18F",
        activeforeground="#402721",
        relief="flat",
        cursor="hand2",
        command=keluar
    )

    waiter_logout.place(
        relx=0.5,
        rely=0.98,
        anchor="s",
        width=100,
        height=38
    )

    return waiter_frame