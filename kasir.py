import os
import re
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import qrcode

import data

# ====== Warna (mengikuti tema halaman login) ======
PANEL_BG   = "#FFFBF7"   # krem putih
PANEL_LINE = "#D9C3B0"   # border panel
CARD_BG    = "#F8E8E3"   # kartu pesanan (pink krem)
TITLE      = "#5C3A21"   # cokelat judul
LABEL      = "#6E4A35"   # cokelat teks
SOFT       = "#A08375"   # teks pudar
BTN        = "#C88A75"   # dusty rose
BTN_HOVER  = "#B27460"
BTN_SOFT   = "#E8C6B8"   # tombol sekunder
GREEN      = "#3C8D5A"
RED        = "#C0475F"

FONT = "Poppins"

# ====== Kode redeem yang berlaku: kode -> nilai voucher (Rp). Ubah sesuai kebutuhan ======
REDEEM_CODES = {
    "PURR10K":  10000,
    "NGOPI25":  25000,
    "PURR50":   50000,
    "FREEPURR": 100000,
}
BASE = os.path.dirname(os.path.abspath(__file__))

def rupiah(n):
    return "Rp" + f"{n:,}".replace(",", ".")


def make_button(parent, text, command, bg=BTN, fg="white", font_size=11,
                ipadx=14, ipady=5, width=None):
    hover = BTN_HOVER if bg == BTN else BTN
    b = tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg,
        activebackground=BTN_HOVER, activeforeground="white",
        font=(FONT, font_size, "bold"), relief="flat", bd=0, cursor="hand2",
        padx=ipadx, pady=ipady,
    )
    if width:
        b.config(width=width)
    b.bind("<Enter>", lambda e: b.config(bg=hover, fg="white"))
    b.bind("<Leave>", lambda e: b.config(bg=bg, fg=fg))
    return b


def create_kasir_frame(window, logout):
    kasir_frame = tk.Frame(window)
    selected = {"order": None}

    #  Background 
    bg_label = tk.Label(kasir_frame)
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

    kasir_frame.bind("<Configure>", resize_bg)

    # =====================================================
    #                 PANEL 1: LIST PELANGGAN
    # =====================================================
    list_panel = tk.Frame(kasir_frame, bg=PANEL_BG,
                          highlightbackground=PANEL_LINE, highlightthickness=2)
    list_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.92)

    # Header: logo + judul
    header = tk.Frame(list_panel, bg=PANEL_BG)
    header.pack(pady=(14, 6))
    logo_img = Image.open(os.path.join(BASE, "logopurr.png")).resize((70, 70), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    tk.Label(header, image=logo_photo, bg=PANEL_BG).pack(side="left", padx=(0, 12))
    logo_ref = logo_photo  # noqa: F841 (jaga referensi gambar)
    header.logo_ref = logo_photo
    tk.Label(header, text="List Pelanggan", font=(FONT, 24, "bold"),
             bg=PANEL_BG, fg=TITLE).pack(side="left")

    # Bar pencarian
    bar = tk.Frame(list_panel, bg=PANEL_BG)
    bar.pack(fill="x", padx=25, pady=(4, 8))

    tk.Label(bar, text="Cari:", bg=PANEL_BG, fg=LABEL,
             font=(FONT, 10, "bold")).pack(side="left")
    search_var = tk.StringVar()
    ent = tk.Entry(bar, textvariable=search_var, font=(FONT, 11), relief="flat",
                   bg="white", fg=LABEL, highlightbackground=PANEL_LINE,
                   highlightcolor=BTN, highlightthickness=2)
    ent.pack(side="left", fill="x", expand=True, padx=8, ipady=3)

    tk.Label(bar, text="Status:", bg=PANEL_BG, fg=LABEL,
             font=(FONT, 10, "bold")).pack(side="left", padx=(8, 4))
    status_var = tk.StringVar(value="Semua")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Kasir.TCombobox", fieldbackground="white", background=BTN_SOFT,
                    foreground=LABEL, bordercolor=PANEL_LINE, arrowcolor=LABEL)
    combo = ttk.Combobox(bar, textvariable=status_var, state="readonly", width=12,
                         values=["Semua", "Lunas", "Belum Lunas"],
                         style="Kasir.TCombobox", font=(FONT, 10))
    combo.pack(side="left")

    # Tombol Keluar (dipack dulu supaya selalu terlihat di bawah)
    make_button(list_panel, "Keluar", logout, bg=BTN_SOFT, fg=LABEL,
                font_size=11, ipadx=18).pack(side="bottom", pady=12)

    # Area scroll
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

    #  Isi list 
    def add_card(o):
        card = tk.Frame(inner, bg=CARD_BG, highlightbackground=PANEL_LINE, highlightthickness=1)
        card.pack(fill="x", pady=6, padx=(0, 8))

        info = tk.Frame(card, bg=CARD_BG)
        info.pack(side="left", fill="both", expand=True, padx=16, pady=12)

        tk.Label(info, text=o["tgl"], bg=CARD_BG, fg=LABEL,
                 font=(FONT, 10, "bold")).pack(anchor="w")
        tk.Label(info, text=o["nama"], bg=CARD_BG, fg=TITLE,
                 font=(FONT, 16, "bold")).pack(anchor="w")
        tk.Label(info, text="Pesanan: " + o["pesanan"], bg=CARD_BG, fg=SOFT,
                 font=(FONT, 9)).pack(anchor="w")
        tk.Label(info, text="Total: " + rupiah(o["total"]), bg=CARD_BG, fg=LABEL,
                 font=(FONT, 12, "bold")).pack(anchor="w", pady=(2, 0))
        warna = GREEN if o["status"] == "Lunas" else RED
        tk.Label(info, text="Status: " + o["status"], bg=CARD_BG, fg=warna,
                 font=(FONT, 9, "bold")).pack(anchor="w")
        tk.Label(info, text="Metode: " + o["metode"], bg=CARD_BG, fg=SOFT,
                 font=(FONT, 9)).pack(anchor="w")

        if o["status"] != "Lunas":
            make_button(card, "Bayar", lambda x=o: open_payment(x),
                        font_size=12, ipadx=18, ipady=8).pack(side="right", padx=20)

    state = {"sig": None}

    def refresh(*_, auto=False):
        kw = search_var.get().lower().strip()
        st = status_var.get()
        rows = []
        for o in reversed(data.get_orders()):   # pesanan terbaru di atas
            if st != "Semua" and o["status"] != st:
                continue
            if kw and kw not in o["nama"].lower() and kw not in o["pesanan"].lower():
                continue
            rows.append(o)

        sig = json.dumps(rows, sort_keys=True)
        if auto and sig == state["sig"]:
            return                      # tidak ada perubahan, jangan gambar ulang
        state["sig"] = sig

        pos = canvas.yview()[0]
        for w in inner.winfo_children():
            w.destroy()
        for o in rows:
            add_card(o)
        if not rows:
            tk.Label(inner, text="Belum ada pesanan masuk", bg=PANEL_BG, fg=SOFT,
                     font=(FONT, 12)).pack(pady=30)
        canvas.after_idle(lambda: canvas.yview_moveto(pos if auto else 0))

    def auto_refresh():
        """Cek pesanan baru dari pembeli setiap 2 detik."""
        if list_panel.winfo_ismapped():
            refresh(auto=True)
        kasir_frame.after(2000, auto_refresh)

    make_button(bar, "Tampilkan", refresh, font_size=10, ipady=3).pack(side="left", padx=(8, 0))
    ent.bind("<Return>", refresh)
    combo.bind("<<ComboboxSelected>>", refresh)

    # =====================================================
    #               PANEL 2: METODE PEMBAYARAN
    # =====================================================
    pay_panel = tk.Frame(kasir_frame, bg=PANEL_BG,
                         highlightbackground=PANEL_LINE, highlightthickness=2)

    tk.Label(pay_panel, text="───  Metode Pembayaran  ───", font=(FONT, 18, "bold"),
             bg=PANEL_BG, fg=TITLE).pack(pady=(35, 6))
    pay_info = tk.Label(pay_panel, text="", font=(FONT, 11), bg=PANEL_BG, fg=SOFT)
    pay_info.pack(pady=(0, 20))

    def selesai_bayar(metode, pesan=None, **extra):
        o = selected["order"]
        if not o:
            return
        data.update_pesanan(o["id"], status="Lunas", metode=metode, **extra)
        messagebox.showinfo("Berhasil",
                            pesan or f"Pembayaran {o['nama']} via {metode} berhasil!")
        selected["order"] = None
        show_list()

    def choose(metode):
        if metode == "Tunai":
            open_tunai()
        elif metode == "QRIS":
            open_qris()
        elif metode == "Kartu Kredit":
            open_kartu()
        elif metode == "Redeem Code":
            open_redeem()

    for m in ("Tunai", "QRIS", "Kartu Kredit", "Redeem Code"):
        make_button(pay_panel, m, lambda x=m: choose(x), font_size=12,
                    ipady=10, width=26).pack(pady=7)

    make_button(pay_panel, "Batal", lambda: show_list(), bg=BTN_SOFT, fg=LABEL,
                font_size=10, ipady=3, ipadx=16).pack(pady=(22, 0))

    # =====================================================
    #               PANEL 3: QRIS (QR DIGAMBAR DI CANVAS)
    # =====================================================
    qris_panel = tk.Frame(kasir_frame, bg=PANEL_BG,
                          highlightbackground=PANEL_LINE, highlightthickness=2)

    tk.Label(qris_panel, text="───  Scan QRIS  ───", font=(FONT, 18, "bold"),
             bg=PANEL_BG, fg=TITLE).pack(pady=(25, 4))
    qris_info = tk.Label(qris_panel, text="", font=(FONT, 11), bg=PANEL_BG, fg=SOFT)
    qris_info.pack()

    # QR dibuat dari library qrcode lalu digambar kotak per kotak di Canvas
    qr_canvas = tk.Canvas(qris_panel, width=260, height=260, bg="white",
                          highlightbackground=PANEL_LINE, highlightthickness=2)
    qr_canvas.pack(pady=15)

    def draw_qr(teks, ukuran=256):
        """Buat QR dari teks lalu gambar kotak-kotaknya di Canvas."""
        qr_canvas.delete("all")
        qr = qrcode.QRCode(border=4, error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(teks)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        sel = max(1, ukuran // len(matrix))          # ukuran 1 kotak
        offset = (260 - sel * len(matrix)) // 2      # biar QR di tengah
        for r, baris in enumerate(matrix):
            for c, gelap in enumerate(baris):
                if gelap:
                    x, y = offset + c * sel, offset + r * sel
                    qr_canvas.create_rectangle(x, y, x + sel, y + sel,
                                               fill="black", outline="black")

    tk.Label(qris_panel, text="Minta pelanggan scan QR di atas,\nlalu tekan tombol setelah pembayaran berhasil.",
             font=(FONT, 10), bg=PANEL_BG, fg=SOFT, justify="center").pack()

    make_button(qris_panel, "Sudah Dibayar", lambda: selesai_bayar("QRIS"),
                font_size=12, ipady=8, ipadx=20).pack(pady=(14, 6))
    make_button(qris_panel, "Kembali", lambda: show_payment_methods(), bg=BTN_SOFT,
                fg=LABEL, font_size=10, ipady=3, ipadx=16).pack()

    # =====================================================
    #        PANEL 4-6: TUNAI, KARTU KREDIT, REDEEM CODE
    # =====================================================
    def make_entry(parent, show="", width=24):
        return tk.Entry(parent, font=(FONT, 12), width=width, show=show, relief="flat",
                        bg="white", fg=LABEL, highlightbackground=PANEL_LINE,
                        highlightcolor=BTN, highlightthickness=2, justify="center")

    def field_label(parent, text):
        tk.Label(parent, text=text, font=(FONT, 10, "bold"),
                 bg=PANEL_BG, fg=LABEL).pack(pady=(10, 2))

    def new_panel(title):
        p = tk.Frame(kasir_frame, bg=PANEL_BG,
                     highlightbackground=PANEL_LINE, highlightthickness=2)
        tk.Label(p, text=title, font=(FONT, 18, "bold"),
                 bg=PANEL_BG, fg=TITLE).pack(pady=(28, 4))
        info = tk.Label(p, text="", font=(FONT, 11), bg=PANEL_BG, fg=SOFT)
        info.pack()
        return p, info

    def digits(text):
        return "".join(c for c in text if c.isdigit())

    #  TUNAI 
    # Aturan: uang diterima harus >= total, kembalian dihitung otomatis.
    tunai_panel, tunai_info = new_panel("───  Pembayaran Tunai  ───")
    field_label(tunai_panel, "Uang diterima (Rp)")
    tunai_entry = make_entry(tunai_panel)
    tunai_entry.pack(ipady=6)
    tunai_hasil = tk.Label(tunai_panel, text="", font=(FONT, 13, "bold"),
                           bg=PANEL_BG, fg=SOFT)
    tunai_hasil.pack(pady=14)

    def hitung_kembalian(*_):
        o = selected["order"]
        if not o:
            return
        uang = int(digits(tunai_entry.get()) or 0)
        if uang == 0:
            tunai_hasil.config(text="")
        elif uang >= o["total"]:
            tunai_hasil.config(text=f"Kembalian: {rupiah(uang - o['total'])}", fg=GREEN)
        else:
            tunai_hasil.config(text=f"Kurang: {rupiah(o['total'] - uang)}", fg=RED)

    tunai_entry.bind("<KeyRelease>", hitung_kembalian)

    def uang_pas():
        o = selected["order"]
        if not o:
            return
        tunai_entry.delete(0, "end")
        tunai_entry.insert(0, str(o["total"]))
        hitung_kembalian()

    def bayar_tunai():
        o = selected["order"]
        if not o:
            return
        teks = digits(tunai_entry.get())
        if not teks or int(teks) == 0:
            messagebox.showwarning("Uang Kosong", "Masukkan jumlah uang yang diterima.")
            return
        uang = int(teks)
        if uang < o["total"]:
            messagebox.showerror("Uang Kurang",
                                 f"Uang kurang {rupiah(o['total'] - uang)} dari total {rupiah(o['total'])}.")
            return
        kembalian = uang - o["total"]
        selesai_bayar(
            "Tunai", dibayar=uang, kembalian=kembalian,
            pesan=f"Pembayaran {o['nama']} berhasil!\n\nDiterima : {rupiah(uang)}\n"
                  f"Total    : {rupiah(o['total'])}\nKembalian: {rupiah(kembalian)}")

    tunai_entry.bind("<Return>", lambda e: bayar_tunai())
    make_button(tunai_panel, "Uang Pas", uang_pas, bg=BTN_SOFT, fg=LABEL,
                font_size=10, ipady=3, ipadx=16).pack()
    make_button(tunai_panel, "Bayar", bayar_tunai, font_size=12,
                ipady=8, ipadx=30).pack(pady=(18, 6))
    make_button(tunai_panel, "Kembali", lambda: show_payment_methods(), bg=BTN_SOFT,
                fg=LABEL, font_size=10, ipady=3, ipadx=16).pack()

    #  KARTU KREDIT 
    # Aturan: nomor 16 digit & lolos cek Luhn, nama diisi, masa berlaku MM/YY
    # belum lewat, CVV 3 digit. Data kartu TIDAK disimpan.
    kartu_panel, kartu_info = new_panel("───  Kartu Kredit  ───")
    field_label(kartu_panel, "Nomor Kartu (16 digit)")
    kartu_no = make_entry(kartu_panel)
    kartu_no.pack(ipady=5)
    field_label(kartu_panel, "Nama Pemegang Kartu")
    kartu_nama = make_entry(kartu_panel)
    kartu_nama.pack(ipady=5)
    field_label(kartu_panel, "Masa Berlaku (MM/YY)")
    kartu_exp = make_entry(kartu_panel, width=10)
    kartu_exp.pack(ipady=5)
    field_label(kartu_panel, "CVV (3 digit)")
    kartu_cvv = make_entry(kartu_panel, show="•", width=6)
    kartu_cvv.pack(ipady=5)

    def luhn_ok(nomor):
        total = 0
        for i, ch in enumerate(reversed(nomor)):
            n = int(ch)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0

    def bayar_kartu():
        o = selected["order"]
        if not o:
            return
        nomor = digits(kartu_no.get())
        nama = kartu_nama.get().strip()
        exp = kartu_exp.get().strip()
        cvv = kartu_cvv.get().strip()

        if len(nomor) != 16:
            messagebox.showerror("Nomor Kartu", "Nomor kartu harus 16 digit.")
            return
        if not luhn_ok(nomor):
            messagebox.showerror("Nomor Kartu", "Nomor kartu tidak valid.")
            return
        if not nama:
            messagebox.showerror("Nama Kosong", "Nama pemegang kartu wajib diisi.")
            return
        m = re.fullmatch(r"(0[1-9]|1[0-2])/(\d{2})", exp)
        if not m:
            messagebox.showerror("Masa Berlaku", "Format masa berlaku harus MM/YY, contoh 08/29.")
            return
        now = datetime.now()
        if (2000 + int(m.group(2)), int(m.group(1))) < (now.year, now.month):
            messagebox.showerror("Masa Berlaku", "Kartu sudah kedaluwarsa.")
            return
        if not (cvv.isdigit() and len(cvv) == 3):
            messagebox.showerror("CVV", "CVV harus 3 digit angka.")
            return

        selesai_bayar(
            "Kartu Kredit",
            pesan=f"Pembayaran {o['nama']} via kartu berakhiran {nomor[-4:]} berhasil!")

    make_button(kartu_panel, "Bayar", bayar_kartu, font_size=12,
                ipady=8, ipadx=30).pack(pady=(18, 6))
    make_button(kartu_panel, "Kembali", lambda: show_payment_methods(), bg=BTN_SOFT,
                fg=LABEL, font_size=10, ipady=3, ipadx=16).pack()

    #  REDEEM CODE 
    # Aturan: kode harus terdaftar, belum pernah dipakai, dan nilai voucher
    # harus cukup menutup total pesanan.
    redeem_panel, redeem_info = new_panel("───  Redeem Code  ───")
    field_label(redeem_panel, "Masukkan kode voucher")
    redeem_entry = make_entry(redeem_panel)
    redeem_entry.pack(ipady=6)

    def bayar_redeem():
        o = selected["order"]
        if not o:
            return
        kode = redeem_entry.get().strip().upper()
        if not kode:
            messagebox.showwarning("Kode Kosong", "Masukkan kode voucher terlebih dahulu.")
            return
        if kode not in REDEEM_CODES:
            messagebox.showerror("Kode Tidak Valid", "Kode voucher tidak terdaftar.")
            return
        if data.kode_terpakai(kode):
            messagebox.showerror("Kode Terpakai", "Kode voucher ini sudah pernah digunakan.")
            return
        nilai = REDEEM_CODES[kode]
        if nilai < o["total"]:
            messagebox.showerror(
                "Nilai Voucher Kurang",
                f"Nilai voucher {rupiah(nilai)} kurang {rupiah(o['total'] - nilai)} "
                f"dari total {rupiah(o['total'])}.\nSilakan pakai metode pembayaran lain.")
            return
        data.pakai_kode(kode)
        selesai_bayar(
            "Redeem Code",
            pesan=f"Pembayaran {o['nama']} dengan kode {kode} berhasil!\n"
                  f"Nilai voucher {rupiah(nilai)} untuk total {rupiah(o['total'])}.")

    redeem_entry.bind("<Return>", lambda e: bayar_redeem())
    make_button(redeem_panel, "Gunakan Kode", bayar_redeem, font_size=12,
                ipady=8, ipadx=24).pack(pady=(20, 6))
    make_button(redeem_panel, "Kembali", lambda: show_payment_methods(), bg=BTN_SOFT,
                fg=LABEL, font_size=10, ipady=3, ipadx=16).pack()

    #  Pindah halaman dalam kasir 
    panels = {
        "pay":    (pay_panel,    480, 520),
        "qris":   (qris_panel,   480, 600),
        "tunai":  (tunai_panel,  480, 540),
        "kartu":  (kartu_panel,  480, 640),
        "redeem": (redeem_panel, 480, 420),
    }

    def hide_panels():
        for p, _, _ in panels.values():
            p.place_forget()

    def show_panel(name):
        list_panel.place_forget()
        hide_panels()
        p, w, h = panels[name]
        p.place(relx=0.5, rely=0.5, anchor="center", width=w, height=h)

    def show_list():
        hide_panels()
        list_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.92)
        refresh()

    def info_text(o):
        return f"{o['nama']}  •  {rupiah(o['total'])}"

    def open_payment(order):
        selected["order"] = order
        pay_info.config(text=info_text(order))
        show_panel("pay")

    def show_payment_methods():
        show_panel("pay")

    def open_qris():
        o = selected["order"]
        if o:
            qris_info.config(text=info_text(o))
            draw_qr(f"{o['nama']}_total_Rp {o['total']}")
            show_panel("qris")

    def open_tunai():
        o = selected["order"]
        if o:
            tunai_info.config(text=info_text(o))
            tunai_entry.delete(0, "end")
            tunai_hasil.config(text="")
            show_panel("tunai")
            tunai_entry.focus_set()

    def open_kartu():
        o = selected["order"]
        if o:
            kartu_info.config(text=info_text(o))
            for e in (kartu_no, kartu_nama, kartu_exp, kartu_cvv):
                e.delete(0, "end")
            show_panel("kartu")
            kartu_no.focus_set()

    def open_redeem():
        o = selected["order"]
        if o:
            redeem_info.config(text=info_text(o))
            redeem_entry.delete(0, "end")
            show_panel("redeem")
            redeem_entry.focus_set()

    refresh()
    auto_refresh()
    return kasir_frame