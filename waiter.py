import tkinter as tk


def create_waiter_frame(window, logout):
    waiter_frame = tk.Frame(window, bg="#F5E6E0")

    # Header Layout Meja
    header_waiter = tk.Frame(waiter_frame, bg="#E8C6B8", height=60)
    header_waiter.pack(fill="x")
    header_waiter.pack_propagate(False)

    tk.Label(
        header_waiter,
        text="◉  Layout Meja",
        font=("Poppins", 18, "bold"),
        bg="#E8C6B8",
        fg="#6E4A35"
    ).pack(expand=True)

    # Area daftar meja
    meja_container = tk.Frame(waiter_frame, bg="#F5E6E0")
    meja_container.place(relx=0.025, rely=0.09, relwidth=0.95, relheight=0.80)

    for kolom in range(5):
        meja_container.grid_columnconfigure(kolom, weight=1, uniform="meja")

    for baris in range(2):
        meja_container.grid_rowconfigure(baris, weight=1, uniform="meja")

    # Membuat 10 meja
    for nomor in range(1, 11):
        baris = (nomor - 1) // 5
        kolom = (nomor - 1) % 5

        meja_card = tk.Frame(meja_container, bg="#FFF8F0")
        meja_card.grid(row=baris, column=kolom, padx=12, pady=12, sticky="nsew")

        tk.Label(
            meja_card,
            text=f"Meja {nomor}\n(KOSONG)",
            font=("Poppins", 17, "bold"),
            bg="#FFF8F0",
            fg="#6E4A35",
            justify="center"
        ).pack(fill="both", expand=True)

    # Tombol Keluar
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
        command=logout
    )
    waiter_logout.place(relx=0.5, rely=0.98, anchor="s", width=100, height=38)

    return waiter_frame