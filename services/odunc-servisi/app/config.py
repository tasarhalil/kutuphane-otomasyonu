"""Odunc Servisi ayarları (ortam değişkenlerinden okunur)."""
from pydantic_settings import BaseSettings


class Ayarlar(BaseSettings):
    # Yalnızca bu servisin KENDİ veritabanı
    veritabani_url: str = "postgresql+psycopg2://kutuphane:sifre@odunc_db:5432/odunc_db"
    ic_anahtar: str = "gelistirme-ic-anahtari"
    # Gecikilen her gün için ceza (GUNLUK_CEZA_TL)
    gunluk_ceza_tl: float = 5.0
    # Ödünç süresi, gün (ODUNC_SURE_GUN)
    odunc_sure_gun: int = 14
    # Diğer servislerin iç adresleri
    katalog_url: str = "http://katalog-servisi:8002"
    kullanici_url: str = "http://kullanici-servisi:8001"


ayarlar = Ayarlar()
