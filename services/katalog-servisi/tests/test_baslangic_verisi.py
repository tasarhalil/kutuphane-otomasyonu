from sqlalchemy import func, select

from app.services.baslangic_verisi import ORNEK_KITAPLAR, ornek_veri_ekle
from app.models import Kitap, Stok
from app.repositories.kitap_repository import KitapDeposu


def test_bos_katalog_ornek_veriyle_dolar(oturum):
    assert 8 <= len(ORNEK_KITAPLAR) <= 10
    assert ornek_veri_ekle(KitapDeposu(oturum)) == len(ORNEK_KITAPLAR)
    assert oturum.scalar(select(func.count()).select_from(Stok)) == len(ORNEK_KITAPLAR)
    assert all(s.mevcutAdet == s.toplamAdet > 0 for s in oturum.scalars(select(Stok)))


def test_dolu_katalog_degismez(oturum):
    ornek_veri_ekle(KitapDeposu(oturum))
    assert ornek_veri_ekle(KitapDeposu(oturum)) == 0  # ikinci çağrıda tekrar eklenmez
    assert oturum.scalar(select(func.count()).select_from(Kitap)) == len(ORNEK_KITAPLAR)
