"""API Gateway ayarları (ortam değişkenlerinden okunur)."""
from pydantic_settings import BaseSettings


class Ayarlar(BaseSettings):
    jwt_gizli_anahtar: str = "gelistirme-anahtari"
    jwt_algoritma: str = "HS256"
    # Servislerin iç ağdaki adresleri
    kullanici_url: str = "http://kullanici-servisi:8001"
    katalog_url: str = "http://katalog-servisi:8002"
    odunc_url: str = "http://odunc-servisi:8003"


ayarlar = Ayarlar()
