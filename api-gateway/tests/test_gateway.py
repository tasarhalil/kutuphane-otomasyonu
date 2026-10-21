import httpx
import jwt
import pytest
from fastapi.testclient import TestClient

from app import yonlendirme
from app.config import ayarlar
from app.main import uygulama

istemci = TestClient(uygulama)


def token_uret(sub="5", rol="UYE"):
    return jwt.encode({"sub": sub, "rol": rol}, ayarlar.jwt_gizli_anahtar, algorithm=ayarlar.jwt_algoritma)


@pytest.fixture
def sahte_servisler(monkeypatch):
    """Servisleri taklit eder: aldığı başlıkları ve adresi geri döndürür."""
    def isleyici(istek: httpx.Request):
        return httpx.Response(200, json={"kullanici": istek.headers.get("x-kullanici-id"),
                                         "rol": istek.headers.get("x-kullanici-rol"),
                                         "adres": str(istek.url)})
    sahte = httpx.AsyncClient(transport=httpx.MockTransport(isleyici))
    monkeypatch.setattr(yonlendirme, "istemci_al", lambda: sahte)


def test_saglik():
    assert istemci.get("/saglik").status_code == 200


def test_tokensiz_istek_reddedilir():
    yanit = istemci.get("/api/kitaplar")
    assert yanit.status_code == 401 and "detay" in yanit.json()


def test_gecersiz_token_reddedilir():
    assert istemci.get("/api/kitaplar", headers={"Authorization": "Bearer bozuk"}).status_code == 401


def test_bilinmeyen_yol():
    assert istemci.get("/api/yok/x", headers={"Authorization": f"Bearer {token_uret()}"}).status_code == 404


def test_ic_uc_nokta_kapali():
    yanit = istemci.post("/api/ic/kitaplar/1/stok-dus", headers={"Authorization": f"Bearer {token_uret()}"})
    assert yanit.status_code == 404


def test_kimlik_basliklari_eklenir_ve_sahtesi_ezilir(sahte_servisler):
    yanit = istemci.get("/api/oduncler/benim", headers={"Authorization": f"Bearer {token_uret('5', 'UYE')}",
                                                       "X-Kullanici-Id": "1", "X-Kullanici-Rol": "YONETICI"})
    assert yanit.json()["kullanici"] == "5" and yanit.json()["rol"] == "UYE"


def test_yonlendirme_dogru_servise_ve_yola(sahte_servisler):
    t = {"Authorization": f"Bearer {token_uret()}"}
    assert istemci.get("/api/kitaplar?arama=x", headers=t).json()["adres"] == "http://katalog-servisi:8002/kitaplar?arama=x"
    assert istemci.get("/api/kullanicilar/ben", headers=t).json()["adres"].startswith("http://kullanici-servisi:8001/kullanicilar/ben")
    assert istemci.get("/api/raporlar/gecikme/anlik", headers=t).json()["adres"].startswith("http://odunc-servisi:8003/raporlar/gecikme/anlik")


def test_acik_yollar_tokensiz_gecer(sahte_servisler):
    assert istemci.post("/api/auth/giris", json={}).status_code == 200
    assert istemci.post("/api/auth/kayit", json={}).status_code == 200


def test_auth_disindaki_yollar_acik_degil(sahte_servisler):
    assert istemci.get("/api/auth/giris").status_code == 401
