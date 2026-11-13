import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

import data

# ====== Warna (sama dengan halaman login & kasir) ======
PANEL_BG   = "#FFFBF7"
PANEL_LINE = "#D9C3B0"
CARD_BG    = "#F8E8E3"
TITLE      = "#5C3A21"
LABEL      = "#6E4A35"
SOFT       = "#A08375"
BTN        = "#C88A75"
BTN_HOVER  = "#B27460"
BTN_SOFT   = "#E8C6B8"
RED        = "#C0475F"
RED_HOVER  = "#A33A50"

FONT = "Poppins"
BASE = os.path.dirname(os.path.abspath(__file__))


def rupiah(n):
    return "Rp" + f"{int(n):,}".replace(",", ".")


def make_button(parent, text, command, bg=BTN, fg="white", font_size=11,
                ipadx=14, ipady=5, width=None, hover=None):
    hover = hover or (BTN_HOVER if bg == BTN else BTN)
    b = tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg,
        activebackground=hover, activeforeground="white",
        font=(FONT, font_size, "bold"), relief="flat", bd=0, cursor="hand2",
        padx=ipadx, pady=ipady,
    )
    if width:
        b.config(width=width)
    b.bind("<Enter>", lambda e: b.config(bg=hover, fg="white"))
    b.bind("<Leave>", lambda e: b.config(bg=bg, fg=fg))
    return b


def create_admin_frame(window, logout):
    admin_frame = tk.Frame(window)
    editing = {"nama": None}      # None = tambah menu baru, isi = nama menu yang diubah

    # ---------- Background ----------
    bg_label = tk.Label(admin_frame)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bg_original = Image.open(os.path.join(BASE, "background.jpg"))
    last = {"size": (0, 0)}

    def resize_bg(event):
        size = (event.width, event.height)
        if event.width < 10 or event.height < 10 or size == last["size"]:
            return
        last["size"] = size
        photo = ImageTk.PhotoImage(bg_original.resize(size, Image.LANCZOS))
        bg_label.config(image=photo)
        bg_label.image = photo

    admin_frame.bind("<Configure>", resize_bg)

    # =====================================================
    #                 PANEL 1: DAFTAR MENU
    # =====================================================
    list_panel = tk.Frame(admin_frame, bg=PANEL_BG,
                          highlightbackground=PANEL_LINE, highlightthickness=2)
    list_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.92)

    header = tk.Frame(list_panel, bg=PANEL_BG)
    header.pack(pady=(14, 6))
    logo_img = Image.open(os.path.join(BASE, "logopurr.png")).resize((70, 70), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    tk.Label(header, image=logo_photo, bg=PANEL_BG).pack(side="left", padx=(0, 12))
    header.logo_ref = logo_photo
    tk.Label(header, text="Kelola Menu", font=(FONT, 24, "bold"),
             bg=PANEL_BG, fg=TITLE).pack(side="left")

    bar = tk.Frame(list_panel, bg=PANEL_BG)
    bar.pack(fill="x", padx=25, pady=(4, 8))
    tk.Label(bar, text="Atur menu yang tampil di halaman pembeli.", font=(FONT, 10),
             bg=PANEL_BG, fg=SOFT).pack(side="left")

    # Tombol Logout (dipack dulu supaya selalu terlihat di bawah)
    make_button(list_panel, "Logout", logout, bg=BTN_SOFT, fg=LABEL,
                font_size=11, ipadx=18).pack(side="bottom", pady=12)

    wrap = tk.Frame(list_panel, bg=PANEL_BG)
    wrap.pack(fill="both", expand=True, padx=25)
    canvas = tk.Canvas(wrap, bg=PANEL_BG, highlightthickness=0)
    sb = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    inner = tk.Frame(canvas, bg=PANEL_BG)
    win = canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))

    def on_wheel(e):
        canvas.yview_scroll(int(-e.delta / 120), "units")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_wheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # ---------- Isi daftar ----------
    def add_card(item):
        card = tk.Frame(inner, bg=CARD_BG, highlightbackground=PANEL_LINE, highlightthickness=1)
        card.pack(fill="x", pady=6, padx=(0, 8))

        info = tk.Frame(card, bg=CARD_BG)
        info.pack(side="left", fill="both", expand=True, padx=16, pady=12)
        tk.Label(info, text=item["nama"], bg=CARD_BG, fg=TITLE,
                 font=(FONT, 15, "bold")).pack(anchor="w")
        tk.Label(info, text=f"{item['kategori']}  —  {rupiah(item['harga'])}", bg=CARD_BG,
                 fg=LABEL, font=(FONT, 11)).pack(anchor="w")
        tk.Label(info, text="Gambar: " + (item.get("image") or "-"), bg=CARD_BG, fg=SOFT,
                 font=(FONT, 9)).pack(anchor="w")

        btns = tk.Frame(card, bg=CARD_BG)
        btns.pack(side="right", padx=16)
        make_button(btns, "Edit", lambda x=item: open_form(x), font_size=10,
                    ipady=5, ipadx=16).pack(side="left", padx=4)
        make_button(btns, "Hapus", lambda x=item: hapus(x), bg=RED, hover=RED_HOVER,
                    font_size=10, ipady=5, ipadx=14).pack(side="left", padx=4)

    def refresh():
        for w in inner.winfo_children():
            w.destroy()
        menu = data.get_menu()
        for item in menu:
            add_card(item)
        if not menu:
            tk.Label(inner, text="Belum ada menu. Klik 'Tambah Menu'.", bg=PANEL_BG,
                     fg=SOFT, font=(FONT, 12)).pack(pady=30)
        canvas.yview_moveto(0)

    make_button(bar, "+ Tambah Menu", lambda: open_form(None), font_size=10,
                ipady=4, ipadx=14).pack(side="right")

    def hapus(item):
        if messagebox.askyesno("Hapus Menu", f"Hapus menu '{item['nama']}'?"):
            data.hapus_menu(item["nama"])
            refresh()

    # =====================================================
    #               PANEL 2: FORM TAMBAH / UBAH
    # =====================================================
    form_panel = tk.Frame(admin_frame, bg=PANEL_BG,
                          highlightbackground=PANEL_LINE, highlightthickness=2)

    form_title = tk.Label(form_panel, text="", font=(FONT, 18, "bold"),
                          bg=PANEL_BG, fg=TITLE)
    form_title.pack(pady=(28, 6))

    def make_entry(width=26):
        return tk.Entry(form_panel, font=(FONT, 12), width=width, relief="flat",
                        bg="white", fg=LABEL, highlightbackground=PANEL_LINE,
                        highlightcolor=BTN, highlightthickness=2, justify="center")

    def field_label(text):
        tk.Label(form_panel, text=text, font=(FONT, 10, "bold"),
                 bg=PANEL_BG, fg=LABEL).pack(pady=(10, 2))

    field_label("Nama Menu")
    ent_nama = make_entry()
    ent_nama.pack(ipady=5)

    field_label("Kategori")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Admin.TCombobox", fieldbackground="white", background=BTN_SOFT,
                    foreground=LABEL, bordercolor=PANEL_LINE, arrowcolor=LABEL)
    kategori_var = tk.StringVar(value="Makanan")
    combo_kategori = ttk.Combobox(form_panel, textvariable=kategori_var, state="readonly",
                                  values=["Makanan", "Minuman"], style="Admin.TCombobox",
                                  font=(FONT, 12), width=24, justify="center")
    combo_kategori.pack(ipady=3)

    field_label("Harga (Rp)")
    ent_harga = make_entry()
    ent_harga.pack(ipady=5)

    field_label("File Gambar (opsional, contoh: croissant.jpg)")
    ent_gambar = make_entry()
    ent_gambar.pack(ipady=5)

    def parse_harga(teks):
        """Terima '20000', '20.000', 'Rp 20.000'. Hasilnya harus bilangan bulat > 0."""
        t = teks.lower().replace("rp", "").replace(" ", "")
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", t):     # format ribuan: 20.000
            t = t.replace(".", "")
        if not re.fullmatch(r"\d+", t) or int(t) <= 0:
            return None
        return int(t)

    def simpan():
        nama = ent_nama.get().strip()
        kategori = kategori_var.get()
        gambar = ent_gambar.get().strip()

        if not nama:
            messagebox.showerror("Nama Kosong", "Nama menu wajib diisi.")
            return
        for m in data.get_menu():
            if m["nama"].lower() == nama.lower() and m["nama"] != editing["nama"]:
                messagebox.showerror("Nama Sudah Ada", f"Menu '{m['nama']}' sudah ada.")
                return

        harga = parse_harga(ent_harga.get())
        if harga is None:
            messagebox.showerror("Harga Tidak Valid",
                                 "Harga harus berupa angka bulat lebih dari 0, contoh: 20000.")
            return

        if gambar and not os.path.exists(os.path.join(BASE, gambar)):
            if not messagebox.askyesno(
                    "Gambar Tidak Ditemukan",
                    f"File '{gambar}' tidak ada di folder program.\nTetap simpan?"):
                return

        if editing["nama"] is None:
            data.tambah_menu(nama, kategori, harga, gambar)
        else:
            data.ubah_menu(editing["nama"], nama, kategori, harga, gambar)
        show_list()

    make_button(form_panel, "Simpan", simpan, font_size=12, ipady=8, ipadx=30).pack(pady=(22, 6))
    make_button(form_panel, "Batal", lambda: show_list(), bg=BTN_SOFT, fg=LABEL,
                font_size=10, ipady=3, ipadx=16).pack()
    for e in (ent_nama, ent_harga, ent_gambar):
        e.bind("<Return>", lambda ev: simpan())

    # ---------- Pindah panel ----------
    def show_list():
        form_panel.place_forget()
        list_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.92)
        refresh()

    def open_form(item):
        editing["nama"] = item["nama"] if item else None
        form_title.config(text="───  Ubah Menu  ───" if item else "───  Tambah Menu  ───")
        for e in (ent_nama, ent_harga, ent_gambar):
            e.delete(0, "end")
        if item:
            ent_nama.insert(0, item["nama"])
            kategori_var.set(item["kategori"])
            ent_harga.insert(0, str(item["harga"]))
            ent_gambar.insert(0, item.get("image") or "")
        else:
            kategori_var.set("Makanan")
        list_panel.place_forget()
        form_panel.place(relx=0.5, rely=0.5, anchor="center", width=480, height=600)
        ent_nama.focus_set()

    refresh()
    return admin_frame