"""Katalog Servisi (container içi port 8002)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401  (tabloları metadata'ya kaydeder)
from app.database import OturumYapici, Taban, motor
from app.repositories.kitap_repository import KitapDeposu
from app.routers import ic, kitaplar
from app.routers.hatalar import hata_isleyicileri_kur
from app.services.baslangic_verisi import ornek_veri_ekle


@asynccontextmanager
async def yasam_dongusu(_: FastAPI):
    # Tablolar, bu servisin kendi veritabanında oluşturulur
    Taban.metadata.create_all(motor)
    with OturumYapici() as oturum:
        ornek_veri_ekle(KitapDeposu(oturum))  # katalog boşsa örnek kitaplar
    yield


uygulama = FastAPI(title="Katalog Servisi", lifespan=yasam_dongusu)
hata_isleyicileri_kur(uygulama)
uygulama.include_router(kitaplar.yonlendirici)
uygulama.include_router(ic.yonlendirici)


@uygulama.get("/saglik")
def saglik():
    return {"durum": "ok", "servis": "katalog-servisi"}
