import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from PIL import Image, ImageTk
import os
import json

import data

BASE = os.path.dirname(os.path.abspath(__file__))


def create_pembeli_frame(window, logout):
    pembeli_frame = tk.Frame(
        window,
        bg="#FFF8F0"
    )

    pembeli_frame.place_forget()


    # Data menu cafe (diambil dari data.py, bisa diubah oleh Admin)

    menu_items = data.get_menu()


    # Menyimpan jumlah setiap menu yang dipilih

    keranjang = {}


    # Background halaman pembeli

    pembeli_frame.configure(
        bg="#FFF8F0"
    )

    pembeli_frame.place_forget()


    # Panel utama

    buyer_card = tk.Frame(
        pembeli_frame,
        bg="#FFFBF7",
        bd=0,
        highlightthickness=0
    )

    buyer_card.place(
        relx=0.5,
        rely=0.5,
        relwidth=0.89,
        relheight=0.90,
        anchor="center"
    )


    # Bagian pencarian dan kategori

    search_frame = tk.Frame(
        buyer_card,
        bg="#F3E5E0"
    )

    search_frame.pack(
        padx=12,
        pady=12,
        fill="x",
        ipady=10,
        ipadx=12
    )

    tk.Label(
        search_frame,
        text="Cari:",
        bg="#F3E5E0",
        fg="#6E4A35",
        font=("Helvetica", 12)
    ).pack(side="left")
    search_var = tk.StringVar()

    entry_search = tk.Entry(
        search_frame,
        textvariable=search_var,
        bg="#FFFFFF",
        fg="#5C3A3A",
        relief="flat",
        font=("Helvetica", 11)
    )

    entry_search.pack(
        side="left",
        padx=7,
        fill="x",
        expand=True
    )

    tk.Label(
        search_frame,
        text="Kategori:",
        bg="#F3E5E0",
        fg="#6E4A35",
        font=("Helvetica", 12)
    ).pack(
        side="left",
        padx=(8, 4)
    )

    category_var = tk.StringVar(value="Semua")

    category_combo = ttk.Combobox(
        search_frame,
        textvariable=category_var,
        values=["Semua", "Makanan", "Minuman"],
        state="readonly",
        width=13
    )

    category_combo.pack(side="left", padx=5)


    # Area daftar menu yang bisa di-scroll

    list_frame = tk.Frame(
        buyer_card,
        bg="#F3E5E0"
    )

    list_frame.pack(
        padx=10,
        pady=5,
        fill="both",
        expand=True
    )

    menu_canvas = tk.Canvas(
        list_frame,
        bg="#F3E5E0",
        bd=0,
        highlightthickness=0
    )

    menu_scrollbar = ttk.Scrollbar(
        list_frame,
        orient="vertical",
        command=menu_canvas.yview
    )

    menu_list_frame = tk.Frame(
        menu_canvas,
        bg="#F3E5E0"
    )

    menu_list_frame.bind(
        "<Configure>",
        lambda event: menu_canvas.configure(
            scrollregion=menu_canvas.bbox("all")
        )
    )

    menu_canvas_window = menu_canvas.create_window(
        (0, 0),
        window=menu_list_frame,
        anchor="nw"
    )

    menu_canvas.configure(
        yscrollcommand=menu_scrollbar.set
    )

    menu_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    menu_scrollbar.pack(
        side="right",
        fill="y"
    )


    def sesuaikan_lebar_menu(event):
        menu_canvas.itemconfig(
            menu_canvas_window,
            width=event.width
        )


    menu_canvas.bind(
        "<Configure>",
        sesuaikan_lebar_menu
    )


    # Scroll daftar menu dengan mouse wheel

    def scroll_menu(event):
        menu_canvas.yview_scroll(int(-event.delta / 120), "units")

    menu_canvas.bind(
        "<Enter>",
        lambda event: menu_canvas.bind_all("<MouseWheel>", scroll_menu)
    )

    menu_canvas.bind(
        "<Leave>",
        lambda event: menu_canvas.unbind_all("<MouseWheel>")
    )


    # Total harga

    total_var = tk.StringVar(value="Total: Rp 0")

    tk.Label(
        buyer_card,
        textvariable=total_var,
        font=("Helvetica", 18, "bold"),
        bg="#F3E5E0",
        fg="#6E4A35"
    ).pack(pady=10)


    # Fungsi memperbarui total

    def update_total():
        total = 0

        for item in menu_items:
            nama = item["nama"]
            jumlah = keranjang.get(nama, 0)
            total += jumlah * item["harga"]

        total_var.set(
            "Total: Rp " + f"{total:,}".replace(",", ".")
        )


    # Fungsi menambah jumlah menu

    def tambah_item(nama, jumlah_label):
        keranjang[nama] = keranjang.get(nama, 0) + 1

        jumlah_label.config(
            text=str(keranjang[nama])
        )

        update_total()


    # Fungsi mengurangi jumlah menu

    def kurang_item(nama, jumlah_label):
        if nama not in keranjang:
            return

        keranjang[nama] -= 1

        if keranjang[nama] <= 0:
            del keranjang[nama]
            jumlah_label.config(text="0")
        else:
            jumlah_label.config(
                text=str(keranjang[nama])
            )

        update_total()


    # Menampilkan daftar menu sesuai pencarian dan kategori

    def tampilkan_menu():
        for widget in menu_list_frame.winfo_children():
            widget.destroy()

        keyword = search_var.get().strip().lower()
        kategori_pilihan = category_var.get()

        for item in menu_items:
            nama = item["nama"]
            kategori = item["kategori"]
            harga = item["harga"]
            image_path = os.path.join(BASE, item["image"])

            if keyword and keyword not in nama.lower():
                continue

            if kategori_pilihan != "Semua" and kategori != kategori_pilihan:
                continue

            # Kartu setiap menu

            menu_card = tk.Frame(
                menu_list_frame,
                bg="#F8E8E3",
                padx=10,
                pady=10
            )

            menu_card.pack(
                fill="x",
                pady=7
            )

            # Gambar menu

            if os.path.exists(image_path):
                try:
                    gambar = Image.open(image_path)
                    gambar.thumbnail((85, 85))
                    foto = ImageTk.PhotoImage(gambar)

                    gambar_label = tk.Label(
                        menu_card,
                        image=foto,
                        bg="#F8E8E3"
                    )

                    gambar_label.image = foto

                    gambar_label.pack(
                        side="left",
                        padx=(5, 10)
                    )

                except (OSError, ValueError):
                    tk.Label(
                        menu_card,
                        text="No Image",
                        width=10,
                        height=4,
                        bg="#F8E8E3",
                        fg="#6E4A35"
                    ).pack(side="left", padx=5)

            else:
                tk.Label(
                    menu_card,
                    text="No Image",
                    width=10,
                    height=4,
                    bg="#F8E8E3",
                    fg="#6E4A35"
                ).pack(side="left", padx=5)

            # Nama, kategori, dan harga

            info_frame = tk.Frame(
                menu_card,
                bg="#F8E8E3"
            )

            info_frame.pack(
                side="left",
                fill="x",
                expand=True
            )

            tk.Label(
                info_frame,
                text=nama,
                font=("Helvetica", 14, "bold"),
                bg="#F8E8E3",
                fg="#6E4A35"
            ).pack(anchor="w")

            tk.Label(
                info_frame,
                text=f"{kategori} — Rp{harga:,}".replace(",", "."),
                font=("Helvetica", 11),
                bg="#F8E8E3",
                fg="#6E4A35"
            ).pack(anchor="w")

            # Tombol kurang, tambah, dan jumlah

            control_frame = tk.Frame(
                menu_card,
                bg="#F8E8E3"
            )

            control_frame.pack(side="right")

            jumlah_label = tk.Label(
                control_frame,
                text=str(keranjang.get(nama, 0)),
                font=("Helvetica", 12),
                bg="#F8E8E3",
                fg="#6E4A35",
                width=3
            )

            jumlah_label.pack(
                side="right",
                padx=5
            )

            tk.Button(
                control_frame,
                text="+",
                width=3,
                bg="#E8C6B8",
                fg="black",
                relief="flat",
                cursor="hand2",
                command=lambda n=nama, label=jumlah_label:
                    tambah_item(n, label)
            ).pack(side="right")

            tk.Button(
                control_frame,
                text="-",
                width=3,
                bg="#E8C6B8",
                fg="black",
                relief="flat",
                cursor="hand2",
                command=lambda n=nama, label=jumlah_label:
                    kurang_item(n, label)
            ).pack(
                side="right",
                padx=5
            )

        update_total()


    # Fungsi konfirmasi pesanan
    def pesan_menu():
        if not keranjang:
            messagebox.showwarning(
                "Keranjang Kosong",
                "Silakan pilih menu terlebih dahulu!"
            )
            return

        # Menanyakan nama pemesan
        nama_pemesan = simpledialog.askstring(
            "Nama Pemesan",
            "Pesanan atas nama siapa?",
            parent=window
        )

        if nama_pemesan is None:
            return

        if not nama_pemesan.strip():
            messagebox.showwarning(
                "Nama Kosong",
                "Silakan masukkan nama pemesan!"
            )
            return

        rincian = f"Nama Pemesan: {nama_pemesan}\n\n"
        total = 0

        for item in menu_items:
            nama = item["nama"]
            jumlah = keranjang.get(nama, 0)

            if jumlah > 0:
                subtotal = jumlah * item["harga"]
                total += subtotal

                rincian += (
                    f"{nama} x {jumlah} = "
                    f"Rp{subtotal:,}\n".replace(",", ".")
                )

        rincian += (
            f"\nTotal pembayaran: Rp{total:,}".replace(",", ".")
        )

        if messagebox.askyesno(
            "Konfirmasi Pesanan",
            rincian + "\n\nApakah pesanan sudah benar?",
            parent=window
        ):
            # Kirim pesanan ke kasir
            data.tambah_pesanan(
                nama_pemesan.strip(),
                [(item["nama"], keranjang[item["nama"]])
                 for item in menu_items if keranjang.get(item["nama"], 0) > 0],
                total
            )

            keranjang.clear()
            tampilkan_menu()

            messagebox.showinfo(
                "Pesanan Berhasil",
                f"Pesanan atas nama {nama_pemesan} berhasil dibuat. "
                "Mohon menunggu."
            )



    # Tombol tampilkan hasil pencarian

    tk.Button(
        search_frame,
        text="Tampilkan",
        bg="#E8C6B8",
        fg="black",
        relief="flat",
        font=("Helvetica", 10, "bold"),
        cursor="hand2",
        command=tampilkan_menu
    ).pack(side="left", padx=5)


    # Tombol pesan

    tk.Button(
        buyer_card,
        text="Pesan",
        font=("Helvetica", 13, "bold"),
        bg="#C88A75",
        fg="white",
        relief="flat",
        padx=30,
        pady=5,
        cursor="hand2",
        command=pesan_menu
    ).pack(pady=(0, 8))


    # Tombol kembali ke halaman login

    tk.Button(
        buyer_card,
        text="Keluar",
        font=("Helvetica", 10),
        bg="#E8C6B8",
        fg="black",
        relief="flat",
        padx=15,
        pady=3,
        cursor="hand2",
        command=logout
    ).pack(pady=(0, 10))


    # Cek perubahan menu dari Admin setiap 2 detik

    menu_sig = {"v": json.dumps(menu_items, sort_keys=True)}

    def cek_menu():
        baru = data.get_menu()
        sig = json.dumps(baru, sort_keys=True)
        if sig != menu_sig["v"]:
            menu_sig["v"] = sig
            menu_items[:] = baru
            nama_ada = {item["nama"] for item in menu_items}
            for n in list(keranjang):
                if n not in nama_ada:
                    del keranjang[n]
            tampilkan_menu()
        pembeli_frame.after(2000, cek_menu)


    tampilkan_menu()
    cek_menu()

    return pembeli_frame