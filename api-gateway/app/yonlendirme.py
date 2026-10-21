"""Yönlendirme tablosu ve isteğin hedef servise iletilmesi."""
import httpx
from fastapi import Request, Response

from app.config import ayarlar

# /api/<ilk-parça>/... -> hedef servis. "ic" parçası burada yok, yani iç uç noktalar dışarıya kapalı
ROTALAR = {
    "auth": "kullanici",
    "kullanicilar": "kullanici",
    "kitaplar": "katalog",
    "oduncler": "odunc",
    "raporlar": "odunc",
}

# Token gerektirmeyen (yöntem, yol) çiftleri
HERKESE_ACIK = {("POST", "auth/giris"), ("POST", "auth/kayit")}

# Dışarıdan gelmesine izin verilmeyen / sahte olabilecek başlıklar
ENGELLENEN_ISTEK_BASLIKLARI = {"host", "content-length", "x-kullanici-id", "x-kullanici-rol", "x-ic-anahtar"}
ENGELLENEN_YANIT_BASLIKLARI = {"content-length", "transfer-encoding", "content-encoding", "connection"}

_istemci: httpx.AsyncClient | None = None


def istemci_al() -> httpx.AsyncClient:
    """Tek bir httpx istemcisi paylaşılır."""
    global _istemci
    if _istemci is None:
        _istemci = httpx.AsyncClient(timeout=15.0)
    return _istemci


def servisAdresi(servis: str) -> str:
    return {"kullanici": ayarlar.kullanici_url, "katalog": ayarlar.katalog_url, "odunc": ayarlar.odunc_url}[servis]


def hedefServis(yol: str) -> str | None:
    """Yolun ilk parçasına göre servis adı; bilinmiyorsa None."""
    return ROTALAR.get(yol.split("/")[0])


def herkeseAcikMi(yontem: str, yol: str) -> bool:
    return (yontem, yol) in HERKESE_ACIK


def istekBasliklari(basliklar) -> dict:
    return {k: v for k, v in basliklar.items() if k.lower() not in ENGELLENEN_ISTEK_BASLIKLARI}


async def ilet(istek: Request, servis: str, yol: str, ekBasliklar: dict) -> Response:
    """İsteği hedef servise iletir ve yanıtı olduğu gibi döndürür."""
    basliklar = {**istekBasliklari(istek.headers), **ekBasliklar}
    try:
        yanit = await istemci_al().request(
            istek.method, f"{servisAdresi(servis)}/{yol}", params=istek.query_params,
            headers=basliklar, content=await istek.body(),
        )
    except httpx.HTTPError:
        raise ServiseUlasilamadi()
    yanitBasliklari = {k: v for k, v in yanit.headers.items() if k.lower() not in ENGELLENEN_YANIT_BASLIKLARI}
    return Response(content=yanit.content, status_code=yanit.status_code, headers=yanitBasliklari)


class ServiseUlasilamadi(Exception):
    """Hedef servise bağlanılamadı."""
