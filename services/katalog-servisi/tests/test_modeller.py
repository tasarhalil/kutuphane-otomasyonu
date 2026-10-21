import pytest
from sqlalchemy import event, text

from app.models import Kitap, Stok, StokHatasi


def kitap_olustur(oturum, toplam=2):
    kitap = Kitap(baslik="Sefiller", yazar="V. Hugo", isbn="111")
    kitap.stok = Stok(toplamAdet=toplam, mevcutAdet=toplam)
    oturum.add(kitap)
    oturum.commit()
    return kitap


def test_stok_dus_ve_artir(oturum):
    stok = kitap_olustur(oturum).stok
    stok.stokDus()
    assert stok.mevcutAdet == 1
    stok.stokArtir()
    assert stok.mevcutAdet == 2


def test_stok_sinirlari(oturum):
    stok = kitap_olustur(oturum, toplam=1).stok
    stok.stokDus()
    with pytest.raises(StokHatasi):
        stok.stokDus()
    stok.stokArtir()
    with pytest.raises(StokHatasi):
        stok.stokArtir()


def test_kitap_silinince_stok_silinir(oturum):
    kitap = kitap_olustur(oturum)
    oturum.delete(kitap)
    oturum.commit()
    assert oturum.query(Stok).count() == 0


def test_isbn_benzersiz(oturum):
    from sqlalchemy.exc import IntegrityError
    kitap_olustur(oturum)
    with pytest.raises(IntegrityError):
        oturum.add(Kitap(baslik="B", yazar="Y", isbn="111"))
        oturum.commit()
