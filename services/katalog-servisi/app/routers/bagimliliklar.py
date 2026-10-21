"""FastAPI bağımlılıkları: kimlik başlıkları, iç çağrı anahtarı ve servis nesnelerinin kurulumu."""
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import ayarlar
from app.database import veritabani_oturumu
from app.repositories.kitap_repository import KitapDeposu
from app.services.kitap_servisi import KitapServisi


class KimlikBilgisi:
    """Gateway'in eklediği başlıklardan gelen kimlik. Servisler bu başlıklara güvenir."""

    def __init__(self, kimlik: int, rol: str):
        self.kimlik = kimlik
        self.rol = rol


def mevcut_kullanici(
    x_kullanici_id: str | None = Header(default=None),
    x_kullanici_rol: str | None = Header(default=None),
) -> KimlikBilgisi:
    if not x_kullanici_id or not x_kullanici_id.isdigit():
        raise HTTPException(status_code=401, detail="Kimlik bilgisi yok")
    return KimlikBilgisi(int(x_kullanici_id), x_kullanici_rol or "")


def yonetici_gerekli(kimlik: KimlikBilgisi = Depends(mevcut_kullanici)) -> KimlikBilgisi:
    """Yalnızca YONETICI rolüne izin verir."""
    if kimlik.rol != "YONETICI":
        raise HTTPException(status_code=403, detail="Bu işlem için yönetici yetkisi gerekli")
    return kimlik


def ic_cagri_dogrula(x_ic_anahtar: str | None = Header(default=None)) -> None:
    """Servisler arası çağrılar X-Ic-Anahtar başlığıyla korunur."""
    if x_ic_anahtar != ayarlar.ic_anahtar:
        raise HTTPException(status_code=403, detail="İç anahtar geçersiz")


def kitap_servisi_al(oturum: Session = Depends(veritabani_oturumu)) -> KitapServisi:
    return KitapServisi(KitapDeposu(oturum))
