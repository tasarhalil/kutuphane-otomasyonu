import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import jwt

import app.main as main
from app.repositories.kullanici_repository import KullaniciDeposu
from app.services.kullanici_servisi import KullaniciServisi
from app.config import ayarlar
from app.database import Taban, veritabani_oturumu

IC = {"X-Ic-Anahtar": ayarlar.ic_anahtar}
KAYIT = {"ad": "Ali Veli", "email": "Ali@Uni.edu", "sifre": "gizli123"}


@pytest.fixture
def istemci(monkeypatch):
    motor = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Taban.metadata.create_all(motor)
    fabrika = sessionmaker(bind=motor)

    def oturum_ver():
        with fabrika() as o:
            yield o
    main.uygulama.dependency_overrides[veritabani_oturumu] = oturum_ver
    monkeypatch.setattr(main, "OturumYapici", fabrika)
    yield TestClient(main.uygulama)
    main.uygulama.dependency_overrides.clear()


def test_kayit_uye_olusturur_ve_uyeno_uretir(istemci):
    yanit = istemci.post("/auth/kayit", json=KAYIT)
    assert yanit.status_code == 201
    veri = yanit.json()
    assert veri["rol"] == "UYE" and veri["email"] == "ali@uni.edu"
    assert veri["uyeNo"].endswith(f"{veri['id']:05d}")
    assert "sifre" not in veri and "sifreHash" not in veri


def test_ayni_email_409(istemci):
    istemci.post("/auth/kayit", json=KAYIT)
    yanit = istemci.post("/auth/kayit", json=KAYIT)
    assert yanit.status_code == 409 and "detay" in yanit.json()


def test_kayit_dogrulama_422(istemci):
    assert istemci.post("/auth/kayit", json={"ad": "A", "email": "bozuk", "sifre": "1"}).status_code == 422


def test_giris_token_rol_ad_dondurur(istemci):
    istemci.post("/auth/kayit", json=KAYIT)
    yanit = istemci.post("/auth/giris", json={"email": "ali@uni.edu", "sifre": "gizli123"})
    assert yanit.status_code == 200
    veri = yanit.json()
    assert veri["rol"] == "UYE" and veri["ad"] == "Ali Veli"
    cozulen = jwt.decode(veri["access_token"], ayarlar.jwt_gizli_anahtar, algorithms=[ayarlar.jwt_algoritma])
    assert cozulen["rol"] == "UYE"


def test_yanlis_sifre_401(istemci):
    istemci.post("/auth/kayit", json=KAYIT)
    assert istemci.post("/auth/giris", json={"email": "ali@uni.edu", "sifre": "yanlis1"}).status_code == 401
    assert istemci.post("/auth/giris", json={"email": "yok@uni.edu", "sifre": "x"}).status_code == 401


def test_kullanicilar_ben(istemci):
    uye = istemci.post("/auth/kayit", json=KAYIT).json()
    basliklar = {"X-Kullanici-Id": str(uye["id"]), "X-Kullanici-Rol": "UYE"}
    assert istemci.get("/kullanicilar/ben", headers=basliklar).json()["email"] == "ali@uni.edu"
    assert istemci.get("/kullanicilar/ben").status_code == 401
    assert istemci.get("/kullanicilar/ben", headers={"X-Kullanici-Id": "999"}).status_code == 404


def test_ic_kullanici_dogrulama(istemci):
    uye = istemci.post("/auth/kayit", json=KAYIT).json()
    assert istemci.get(f"/ic/kullanicilar/{uye['id']}").status_code == 403  # anahtarsız
    yanit = istemci.get(f"/ic/kullanicilar/{uye['id']}", headers=IC)
    assert yanit.status_code == 200 and yanit.json()["rol"] == "UYE"
    assert istemci.get("/ic/kullanicilar/999", headers=IC).status_code == 404


def test_ilk_yonetici_tohumlanir_ve_tekrarlanmaz(istemci):
    with main.OturumYapici() as o:
        KullaniciServisi(KullaniciDeposu(o)).ilkYoneticiOlustur()
    with main.OturumYapici() as o:
        KullaniciServisi(KullaniciDeposu(o)).ilkYoneticiOlustur()
    yanit = istemci.post("/auth/giris", json={"email": ayarlar.yonetici_email, "sifre": ayarlar.admin_sifre})
    assert yanit.status_code == 200 and yanit.json()["rol"] == "YONETICI"
