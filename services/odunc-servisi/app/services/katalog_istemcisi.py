"""Katalog Servisi ile iç (servisler arası) iletişim: X-Ic-Anahtar ile korunur."""
import httpx

from app.config import ayarlar


class KatalogHatasi(Exception):
    """Katalog Servisi çağrısı başarısız oldu. `kod`: dönen HTTP kodu (ulaşılamadıysa 502)."""

    def __init__(self, kod: int, mesaj: str):
        super().__init__(mesaj)
        self.kod = kod
        self.mesaj = mesaj


class KatalogIstemcisi:
    def __init__(self, istemci: httpx.Client | None = None):
        self._istemci = istemci or httpx.Client(base_url=ayarlar.katalog_url, timeout=10.0)

    def _cagir(self, kitapId: int, islem: str) -> None:
        try:
            yanit = self._istemci.post(
                f"/ic/kitaplar/{kitapId}/{islem}", headers={"X-Ic-Anahtar": ayarlar.ic_anahtar}
            )
        except httpx.HTTPError:
            raise KatalogHatasi(502, "Katalog Servisine ulaşılamadı")
        if yanit.status_code != 200:
            try:
                mesaj = yanit.json().get("detay", "Katalog hatası")
            except ValueError:
                mesaj = "Katalog hatası"
            raise KatalogHatasi(yanit.status_code, mesaj)

    def stokDus(self, kitapId: int) -> None:
        self._cagir(kitapId, "stok-dus")

    def stokArtir(self, kitapId: int) -> None:
        self._cagir(kitapId, "stok-artir")


def katalog_istemcisi_al() -> KatalogIstemcisi:
    """FastAPI bağımlılığı (testlerde değiştirilebilir)."""
    return KatalogIstemcisi()
