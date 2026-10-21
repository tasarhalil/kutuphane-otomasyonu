from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.models import GecikmeRaporu, IadeHatasi, Odunc, OduncDurumu


def odunc_olustur(oturum, son_teslim_gun=14):
    bugun = date.today()
    odunc = Odunc(uyeId=1, kitapId=2, alisTarihi=bugun - timedelta(days=14),
                  sonTeslimTarihi=bugun - timedelta(days=14 - son_teslim_gun))
    oturum.add(odunc)
    oturum.commit()
    return odunc


def test_zamaninda_iade(oturum):
    odunc = odunc_olustur(oturum)
    odunc.iadeEt()
    assert odunc.durum == OduncDurumu.IADE_EDILDI
    assert odunc.iadeTarihi is not None and odunc.gecikmeRaporu is None


def test_gecikmis_iade_rapor_ve_ceza(oturum):
    odunc = odunc_olustur(oturum, son_teslim_gun=0)
    odunc.iadeEt(odunc.sonTeslimTarihi + timedelta(days=3))
    oturum.commit()
    assert odunc.durum == OduncDurumu.GECIKMIS_IADE
    assert odunc.gecikmeRaporu.gecikmeGun == 3
    assert odunc.gecikmeRaporu.cezaTutari == Decimal("15")


def test_cifte_iade_hata(oturum):
    odunc = odunc_olustur(oturum)
    odunc.iadeEt()
    with pytest.raises(IadeHatasi):
        odunc.iadeEt()


def test_odunc_silinince_rapor_silinir(oturum):
    odunc = odunc_olustur(oturum, son_teslim_gun=0)
    odunc.iadeEt(odunc.sonTeslimTarihi + timedelta(days=1))
    oturum.commit()
    oturum.delete(odunc)
    oturum.commit()
    assert oturum.query(GecikmeRaporu).count() == 0


def test_baska_servise_foreign_key_yok():
    tablo = Odunc.__table__
    assert not tablo.foreign_keys
