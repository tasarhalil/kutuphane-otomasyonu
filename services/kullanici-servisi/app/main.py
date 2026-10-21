"""Kullanici Servisi (container içi port 8001)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401  (tabloları metadata'ya kaydeder)
from app.database import OturumYapici, Taban, motor
from app.repositories.kullanici_repository import KullaniciDeposu
from app.routers import auth, kullanicilar
from app.routers.hatalar import hata_isleyicileri_kur
from app.services.kullanici_servisi import KullaniciServisi


@asynccontextmanager
async def yasam_dongusu(_: FastAPI):
    # Tablolar, bu servisin kendi veritabanında oluşturulur
    Taban.metadata.create_all(motor)
    with OturumYapici() as oturum:
        KullaniciServisi(KullaniciDeposu(oturum)).ilkYoneticiOlustur()
    yield


uygulama = FastAPI(title="Kullanici Servisi", lifespan=yasam_dongusu)
hata_isleyicileri_kur(uygulama)
uygulama.include_router(auth.yonlendirici)
uygulama.include_router(kullanicilar.yonlendirici)


@uygulama.get("/saglik")
def saglik():
    return {"durum": "ok", "servis": "kullanici-servisi"}
