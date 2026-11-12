"""
data.py - penghubung pesanan antara pembeli.py, waiter.py, dan kasir.py

Pembeli  : memanggil tambah_pesanan(...) saat pesanan dikirim
Kasir    : memanggil get_orders() untuk menampilkan, update_pesanan(...) saat bayar

Data disimpan di pesanan.json (satu folder dengan file ini), jadi
tidak hilang walau aplikasi ditutup. Hapus pesanan.json untuk mengosongkan.
"""
import json
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE, "pesanan.json")


def _load():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save(orders):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


def get_orders():
    """Semua pesanan (list of dict)."""
    return _load()


def tambah_pesanan(nama, items, total):
    """
    Dipanggil dari pembeli.py saat pesanan dikirim.

    nama  : nama pembeli, contoh "Adi"
    items : string "Nasi Goreng (x1), Mie Ayam (x2)"
            atau list of (nama_menu, jumlah), contoh [("Nasi Goreng", 1), ("Mie Ayam", 2)]
    total : total harga (angka), contoh 56000
    """
    if not isinstance(items, str):
        items = ", ".join(f"{n} (x{q})" for n, q in items)

    orders = _load()
    now = datetime.now()
    order = {
        "id": (max((o["id"] for o in orders), default=0) + 1),
        "tgl": f"{now.day}/{now.month}/{now.year}",
        "nama": nama,
        "pesanan": items,
        "total": int(total),
        "status": "Belum Lunas",
        "metode": "-",
    }
    orders.append(order)
    _save(orders)
    return order


def update_pesanan(order_id, **perubahan):
    """Dipanggil dari kasir.py, contoh: update_pesanan(3, status="Lunas", metode="QRIS")"""
    orders = _load()
    for o in orders:
        if o["id"] == order_id:
            o.update(perubahan)
            break
    _save(orders)


# ---------- Kode redeem (voucher sekali pakai) ----------
USED_FILE = os.path.join(BASE, "kode_terpakai.json")


def _load_used():
    if not os.path.exists(USED_FILE):
        return []
    try:
        with open(USED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def kode_terpakai(kode):
    """True kalau kode redeem sudah pernah dipakai."""
    return kode.upper() in _load_used()


def pakai_kode(kode):
    """Tandai kode redeem sudah dipakai."""
    used = _load_used()
    if kode.upper() not in used:
        used.append(kode.upper())
        with open(USED_FILE, "w", encoding="utf-8") as f:
            json.dump(used, f, ensure_ascii=False, indent=2)


# ---------- Menu cafe (diubah oleh Admin, dibaca oleh Pembeli) ----------
MENU_FILE = os.path.join(BASE, "menu.json")

DEFAULT_MENU = [
    {"nama": "Croissant", "kategori": "Makanan", "harga": 20000, "image": "croissant.jpg"},
    {"nama": "Es Teh",    "kategori": "Minuman", "harga": 5000,  "image": "es_teh.jpg"},
    {"nama": "Mie Ayam",  "kategori": "Makanan", "harga": 18000, "image": "mie_ayam.jpg"},
    {"nama": "Kopi Susu", "kategori": "Minuman", "harga": 15000, "image": "kopi_susu.jpg"},
]


def _save_menu(menu):
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=2)


def get_menu():
    """Daftar menu. Kalau menu.json belum ada, dibuat dari DEFAULT_MENU."""
    if not os.path.exists(MENU_FILE):
        _save_menu(DEFAULT_MENU)
        return [dict(m) for m in DEFAULT_MENU]
    try:
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return [dict(m) for m in DEFAULT_MENU]


def tambah_menu(nama, kategori, harga, image=""):
    menu = get_menu()
    menu.append({"nama": nama, "kategori": kategori, "harga": int(harga), "image": image})
    _save_menu(menu)


def ubah_menu(nama_lama, nama, kategori, harga, image=""):
    menu = get_menu()
    for m in menu:
        if m["nama"] == nama_lama:
            m.update({"nama": nama, "kategori": kategori, "harga": int(harga), "image": image})
            break
    _save_menu(menu)


def hapus_menu(nama):
    _save_menu([m for m in get_menu() if m["nama"] != nama])