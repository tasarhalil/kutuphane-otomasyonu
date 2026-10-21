"""JWT doğrulama ve kimlik başlıklarının üretimi."""
import jwt

from app.config import ayarlar


class TokenHatasi(Exception):
    """Token geçersiz veya süresi dolmuş."""


def tokenDogrula(token: str) -> dict:
    """Token'ı çözer; geçersizse TokenHatasi fırlatır."""
    try:
        return jwt.decode(token, ayarlar.jwt_gizli_anahtar, algorithms=[ayarlar.jwt_algoritma])
    except jwt.PyJWTError as hata:
        raise TokenHatasi(str(hata))


def kimlikBasliklari(veri: dict) -> dict:
    """Servislerin güveneceği X-Kullanici-Id ve X-Kullanici-Rol başlıkları."""
    return {"X-Kullanici-Id": str(veri.get("sub", "")), "X-Kullanici-Rol": str(veri.get("rol", ""))}
