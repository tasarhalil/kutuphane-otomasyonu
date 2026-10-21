"""Kullanici Servisi ayarları (ortam değişkenlerinden okunur)."""
from pydantic_settings import BaseSettings


class Ayarlar(BaseSettings):
    # Yalnızca bu servisin KENDİ veritabanı
    veritabani_url: str = "postgresql+psycopg2://kutuphane:sifre@kullanici_db:5432/kullanici_db"
    ic_anahtar: str = "gelistirme-ic-anahtari"
    # Gateway ile aynı anahtar/algoritma kullanılır
    jwt_gizli_anahtar: str = "gelistirme-anahtari"
    jwt_algoritma: str = "HS256"
    jwt_sure_dakika: int = 60
    # Açılışta yoksa oluşturulan ilk yönetici hesabı
    yonetici_ad: str = "Sistem Yöneticisi"
    yonetici_email: str = "admin@kutuphane.local"
    admin_sifre: str = "Admin123!"  # ADMIN_SIFRE


ayarlar = Ayarlar()
