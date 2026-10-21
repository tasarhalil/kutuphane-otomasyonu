from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import ayarlar
from app.database import Taban, veritabani_oturumu
from app.services.katalog_istemcisi import KatalogHatasi, katalog_istemcisi_al
from app.services.kullanici_istemcisi import KullaniciHatasi, kullanici_istemcisi_al
from app.main import uygulama
from app.models import GecikmeRaporu, Odunc, OduncDurumu

from types import SimpleNamespace

from app.repositories.odunc_repository import OduncDeposu
from app.services.hatalar import IsKuraliHatasi as KuralHatasi
from app.services.odunc_servisi import OduncServisi


is_kurallari = SimpleNamespace(
    oduncAl=lambda oturum, uye, kitap, katalog, kullanici, bugun=None:
        OduncServisi(OduncDeposu(oturum), katalog, kullanici).oduncAl(uye, kitap, bugun),
    iadeEt=lambda oturum, oduncId, uye, katalog, bugun=None:
        OduncServisi(OduncDeposu(oturum), katalog, None).iadeEt(oduncId, uye, bugun),
    anlikGecikmeler=lambda oturum, bugun=None:
        OduncServisi(OduncDeposu(oturum), None, None).anlikGecikmeler(bugun),
)


class SahteKatalog:
    """Katalog Servisi yerine geçer; çağrıları kaydeder."""

    def __init__(self, stok_var=True):
        self.stok_var = stok_var
        self.cagrilar = []

    def stokDus(self, kitapId):
        if not self.stok_var:
            raise KatalogHatasi(409, "Kitap stokta yok")
        self.cagrilar.append(("dus", kitapId))

    def stokArtir(self, kitapId):
        self.cagrilar.append(("artir", kitapId))


class SahteKullanici:
    """Kullanici Servisi yerine geçer; id 9 yönetici, 404 yok sayılır."""

    def uyeGetir(self, uyeId):
        if uyeId == 404:
            raise KullaniciHatasi(404, "yok")
        return {"id": uyeId, "rol": "YONETICI" if uyeId == 9 else "UYE"}


def test_son_teslim_tarihi_ayarli_sure_kadar(oturum):
    bugun = date(2025, 1, 1)
    odunc = is_kurallari.oduncAl(oturum, 1, 10, SahteKatalog(), SahteKullanici(), bugun)
    assert odunc.sonTeslimTarihi == bugun + timedelta(days=ayarlar.odunc_sure_gun) == date(2025, 1, 15)


def test_stok_yoksa_409_ve_kayit_olusmaz(oturum):
    with pytest.raises(KuralHatasi) as hata:
        is_kurallari.oduncAl(oturum, 1, 10, SahteKatalog(stok_var=False), SahteKullanici())
    assert hata.value.kod == 409
    assert oturum.query(Odunc).count() == 0


def test_ayni_kitap_tekrar_alinamaz(oturum):
    katalog = SahteKatalog()
    is_kurallari.oduncAl(oturum, 1, 10, katalog, SahteKullanici())
    with pytest.raises(KuralHatasi) as hata:
        is_kurallari.oduncAl(oturum, 1, 10, katalog, SahteKullanici())
    assert hata.value.kod == 409
    assert katalog.cagrilar == [("dus", 10)]  # ikinci denemede stok düşülmedi


def test_en_fazla_5_aktif_odunc(oturum):
    katalog = SahteKatalog()
    for kitap in range(1, 6):
        is_kurallari.oduncAl(oturum, 1, kitap, katalog, SahteKullanici())
    with pytest.raises(KuralHatasi) as hata:
        is_kurallari.oduncAl(oturum, 1, 6, katalog, SahteKullanici())
    assert hata.value.kod == 409
    # başka üye etkilenmez
    is_kurallari.oduncAl(oturum, 2, 6, katalog, SahteKullanici())


def test_kayit_basarisizsa_telafi_stok_artir(oturum, monkeypatch):
    katalog = SahteKatalog()

    def patla():
        raise RuntimeError("veritabanı hatası")
    monkeypatch.setattr(oturum, "commit", patla)
    with pytest.raises(RuntimeError):
        is_kurallari.oduncAl(oturum, 1, 10, katalog, SahteKullanici())
    assert katalog.cagrilar == [("dus", 10), ("artir", 10)]


def test_zamaninda_iade_stok_artar(oturum):
    katalog = SahteKatalog()
    odunc = is_kurallari.oduncAl(oturum, 1, 10, katalog, SahteKullanici())
    is_kurallari.iadeEt(oturum, odunc.oduncId, 1, katalog)
    assert odunc.durum == OduncDurumu.IADE_EDILDI
    assert katalog.cagrilar[-1] == ("artir", 10)


def test_gec_iade_rapor_otomatik(oturum):
    katalog = SahteKatalog()
    odunc = is_kurallari.oduncAl(oturum, 1, 10, katalog, SahteKullanici(), date.today() - timedelta(days=20))
    is_kurallari.iadeEt(oturum, odunc.oduncId, 1, katalog)
    assert odunc.durum == OduncDurumu.GECIKMIS_IADE
    rapor = oturum.scalars(select(GecikmeRaporu)).one()
    assert rapor.gecikmeGun == 6
    assert rapor.cezaTutari == Decimal("5") * 6 == Decimal(str(ayarlar.gunluk_ceza_tl)) * 6


def test_baskasinin_oduncu_iade_edilemez(oturum):
    katalog = SahteKatalog()
    odunc = is_kurallari.oduncAl(oturum, 1, 10, katalog, SahteKullanici())
    with pytest.raises(KuralHatasi) as hata:
        is_kurallari.iadeEt(oturum, odunc.oduncId, 2, katalog)
    assert hata.value.kod == 403


def test_iade_basarisizsa_kayit_yazilmaz(oturum):
    katalog = SahteKatalog()
    odunc = is_kurallari.oduncAl(oturum, 1, 10, katalog, SahteKullanici())

    def hatali(kitapId):
        raise KatalogHatasi(502, "ulaşılamadı")
    katalog.stokArtir = hatali
    with pytest.raises(KuralHatasi):
        is_kurallari.iadeEt(oturum, odunc.oduncId, 1, katalog)
    oturum.refresh(odunc)
    assert odunc.durum == OduncDurumu.AKTIF and odunc.iadeTarihi is None


def test_anlik_gecikme_yazmadan_hesaplanir(oturum):
    katalog = SahteKatalog()
    is_kurallari.oduncAl(oturum, 1, 10, katalog, SahteKullanici(), date.today() - timedelta(days=17))  # 3 gün gecikmiş
    is_kurallari.oduncAl(oturum, 1, 11, katalog, SahteKullanici())  # gecikmemiş
    liste = is_kurallari.anlikGecikmeler(oturum)
    assert len(liste) == 1 and liste[0]["gecikmeGun"] == 3 and liste[0]["cezaTutari"] == 15.0
    assert oturum.query(GecikmeRaporu).count() == 0


# ---------------- API (yetki) testleri ----------------
@pytest.fixture
def istemci():
    motor = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Taban.metadata.create_all(motor)
    fabrika = sessionmaker(bind=motor)
    katalog = SahteKatalog()

    def oturum_ver():
        with fabrika() as o:
            yield o
    uygulama.dependency_overrides[veritabani_oturumu] = oturum_ver
    uygulama.dependency_overrides[katalog_istemcisi_al] = lambda: katalog
    uygulama.dependency_overrides[kullanici_istemcisi_al] = lambda: SahteKullanici()
    yield TestClient(uygulama)
    uygulama.dependency_overrides.clear()


UYE1 = {"X-Kullanici-Id": "1", "X-Kullanici-Rol": "UYE"}
UYE2 = {"X-Kullanici-Id": "2", "X-Kullanici-Rol": "UYE"}
YONETICI = {"X-Kullanici-Id": "9", "X-Kullanici-Rol": "YONETICI"}


def test_api_uye_sadece_kendi_odunclerini_gorur(istemci):
    assert istemci.post("/oduncler", json={"kitapId": 3}, headers=UYE1).status_code == 201
    assert len(istemci.get("/oduncler/benim", headers=UYE1).json()) == 1
    assert istemci.get("/oduncler/benim", headers=UYE2).json() == []
    # tümü yalnızca yöneticiye açık
    assert istemci.get("/oduncler", headers=UYE1).status_code == 403
    assert len(istemci.get("/oduncler", headers=YONETICI).json()) == 1


def test_api_durum_filtresi(istemci):
    oid = istemci.post("/oduncler", json={"kitapId": 3}, headers=UYE1).json()["oduncId"]
    assert len(istemci.get("/oduncler?durum=AKTIF", headers=YONETICI).json()) == 1
    assert istemci.get("/oduncler?durum=IADE_EDILDI", headers=YONETICI).json() == []
    istemci.post(f"/oduncler/{oid}/iade", headers=UYE1)
    assert len(istemci.get("/oduncler?durum=IADE_EDILDI", headers=YONETICI).json()) == 1
    yanit = istemci.get("/oduncler?durum=BOZUK", headers=YONETICI)
    assert yanit.status_code == 422 and "detay" in yanit.json()


def test_api_iade_sahiplik(istemci):
    oid = istemci.post("/oduncler", json={"kitapId": 3}, headers=UYE1).json()["oduncId"]
    yanit = istemci.post(f"/oduncler/{oid}/iade", headers=UYE2)
    assert yanit.status_code == 403 and "detay" in yanit.json()
    assert istemci.post(f"/oduncler/{oid}/iade", headers=UYE1).json()["durum"] == "IADE_EDILDI"
    assert istemci.post(f"/oduncler/{oid}/iade", headers=UYE1).status_code == 409
    assert istemci.post("/oduncler/999/iade", headers=UYE1).status_code == 404


def test_api_uye_dogrulama(istemci):
    # Kullanici Servisi'nde bulunmayan üye ve yönetici ödünç alamaz
    assert istemci.post("/oduncler", json={"kitapId": 3}, headers={**UYE1, "X-Kullanici-Id": "404"}).status_code == 404
    assert istemci.post("/oduncler", json={"kitapId": 3}, headers=YONETICI).status_code == 403


def test_api_dogrulama_hatasi_422(istemci):
    assert istemci.post("/oduncler", json={}, headers=UYE1).status_code == 422


def test_api_gecikme_raporlari_sadece_yonetici(istemci):
    for yol in ("/raporlar/gecikme/kayitlar", "/raporlar/gecikme/anlik"):
        assert istemci.get(yol, headers=UYE1).status_code == 403
        assert istemci.get(yol, headers=YONETICI).status_code == 200
    assert istemci.get("/raporlar/gecikme/anlik").status_code == 401
