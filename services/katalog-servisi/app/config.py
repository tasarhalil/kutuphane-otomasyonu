"""Katalog Servisi ayarları (ortam değişkenlerinden okunur)."""
from pydantic_settings import BaseSettings


class Ayarlar(BaseSettings):
    # Yalnızca bu servisin KENDİ veritabanı
    veritabani_url: str = "postgresql+psycopg2://kutuphane:sifre@katalog_db:5432/katalog_db"
    ic_anahtar: str = "gelistirme-ic-anahtari"


ayarlar = Ayarlar()
