"""Katalog başlangıç verisi: katalog boşsa örnek kitaplar ve stok eklenir."""
from app.models import Kitap, Stok
from app.repositories.kitap_repository import KitapDeposu

# (baslik, yazar, isbn, toplamAdet)
ORNEK_KITAPLAR = [
    ("Suç ve Ceza", "Fyodor Dostoyevski", "9789750719387", 5),
    ("Sefiller", "Victor Hugo", "9789750738609", 3),
    ("1984", "George Orwell", "9789750718533", 4),
    ("Simyacı", "Paulo Coelho", "9789750726439", 6),
    ("Kürk Mantolu Madonna", "Sabahattin Ali", "9789753638029", 4),
    ("Tutunamayanlar", "Oğuz Atay", "9789754700114", 2),
    ("Temiz Kod", "Robert C. Martin", "9786055273521", 3),
    ("Tasarım Desenleri", "Erich Gamma", "9780201633610", 2),
    ("Algoritmalara Giriş", "Thomas H. Cormen", "9780262033848", 2),
    ("Sapiens: Hayvanlardan Tanrılara", "Yuval Noah Harari", "9786053609728", 5),
]


def ornek_veri_ekle(depo: KitapDeposu) -> int:
    """Katalog boşsa örnek kitapları ekler; eklenen kitap sayısını döndürür."""
    if depo.sayi() > 0:
        return 0
    for baslik, yazar, isbn, adet in ORNEK_KITAPLAR:
        kitap = Kitap(baslik=baslik, yazar=yazar, isbn=isbn)
        kitap.stok = Stok(toplamAdet=adet, mevcutAdet=adet)
        depo.ekle(kitap)
    depo.kaydet()
    return len(ORNEK_KITAPLAR)
