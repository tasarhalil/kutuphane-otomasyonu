import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import ayarlar
from app.database import Taban, veritabani_oturumu
from app.main import uygulama

IC = {"X-Ic-Anahtar": ayarlar.ic_anahtar}
YONETICI = {"X-Kullanici-Id": "9", "X-Kullanici-Rol": "YONETICI"}
UYE = {"X-Kullanici-Id": "1", "X-Kullanici-Rol": "UYE"}


@pytest.fixture
def istemci():
    motor = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Taban.metadata.create_all(motor)
    fabrika = sessionmaker(bind=motor)

    def oturum_ver():
        with fabrika() as o:
            yield o
    uygulama.dependency_overrides[veritabani_oturumu] = oturum_ver
    yield TestClient(uygulama)
    uygulama.dependency_overrides.clear()


def kitap_ekle(istemci, adet=1, isbn="111"):
    return istemci.post("/kitaplar", json={"baslik": "Sefiller", "yazar": "Hugo", "isbn": isbn, "toplamAdet": adet},
                        headers=YONETICI)


def test_ic_stok_dus_stok_yoksa_409(istemci):
    kid = kitap_ekle(istemci, adet=1).json()["kitapId"]
    assert istemci.post(f"/ic/kitaplar/{kid}/stok-dus", headers=IC).json()["mevcutAdet"] == 0
    assert istemci.post(f"/ic/kitaplar/{kid}/stok-dus", headers=IC).status_code == 409


def test_ic_stok_artir(istemci):
    kid = kitap_ekle(istemci, adet=2).json()["kitapId"]
    istemci.post(f"/ic/kitaplar/{kid}/stok-dus", headers=IC)
    assert istemci.post(f"/ic/kitaplar/{kid}/stok-artir", headers=IC).json()["mevcutAdet"] == 2


def test_ic_uc_noktalar_anahtarsiz_403_ve_bilinmeyen_kitap_404(istemci):
    assert istemci.post("/ic/kitaplar/1/stok-dus").status_code == 403
    assert istemci.post("/ic/kitaplar/999/stok-dus", headers=IC).status_code == 404


def test_kitap_ekleme_sadece_yonetici_ve_isbn_benzersiz(istemci):
    govde = {"baslik": "A", "yazar": "B", "isbn": "5", "toplamAdet": 1}
    assert istemci.post("/kitaplar", json=govde, headers=UYE).status_code == 403
    assert istemci.post("/kitaplar", json=govde, headers=YONETICI).status_code == 201
    assert istemci.post("/kitaplar", json=govde, headers=YONETICI).status_code == 409


def test_kitap_arama(istemci):
    kitap_ekle(istemci)
    assert len(istemci.get("/kitaplar", params={"arama": "sefil"}, headers=UYE).json()) == 1
    assert istemci.get("/kitaplar", params={"arama": "yok"}, headers=UYE).json() == []
