"""Kullanici Servisi ile iç (servisler arası) iletişim: X-Ic-Anahtar ile korunur."""
import httpx

from app.config import ayarlar


class KullaniciHatasi(Exception):
    """Kullanici Servisi çağrısı başarısız oldu. `kod`: HTTP kodu (ulaşılamadıysa 502)."""

    def __init__(self, kod: int, mesaj: str):
        super().__init__(mesaj)
        self.kod = kod
        self.mesaj = mesaj


class KullaniciIstemcisi:
    def __init__(self, istemci: httpx.Client | None = None):
        self._istemci = istemci or httpx.Client(base_url=ayarlar.kullanici_url, timeout=10.0)

    def uyeGetir(self, uyeId: int) -> dict:
        """Üye doğrulama: {id, ad, email, rol, uyeNo} döndürür."""
        try:
            yanit = self._istemci.get(
                f"/ic/kullanicilar/{uyeId}", headers={"X-Ic-Anahtar": ayarlar.ic_anahtar}
            )
        except httpx.HTTPError:
            raise KullaniciHatasi(502, "Kullanıcı Servisine ulaşılamadı")
        if yanit.status_code != 200:
            raise KullaniciHatasi(yanit.status_code, "Üye doğrulanamadı")
        return yanit.json()


def kullanici_istemcisi_al() -> KullaniciIstemcisi:
    """FastAPI bağımlılığı (testlerde değiştirilebilir)."""
    return KullaniciIstemcisi()
