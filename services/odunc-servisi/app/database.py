"""Odunc Servisi: kendi veritabanı bağlantısı ve oturum yönetimi."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import ayarlar

# create_engine bağlantıyı hemen açmaz; ilk sorguda bağlanır
motor = create_engine(ayarlar.veritabani_url, pool_pre_ping=True)
OturumYapici = sessionmaker(bind=motor, autoflush=False)


class Taban(DeclarativeBase):
    """Bu servisin tüm tablo sınıflarının atası."""


def veritabani_oturumu():
    oturum = OturumYapici()
    try:
        yield oturum
    finally:
        oturum.close()
