"""Odunc Servisi (container içi port 8003)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401  (tabloları metadata'ya kaydeder)
from app.database import Taban, motor
from app.routers import oduncler, raporlar
from app.routers.hatalar import hata_isleyicileri_kur


@asynccontextmanager
async def yasam_dongusu(_: FastAPI):
    # Tablolar, bu servisin kendi veritabanında oluşturulur
    Taban.metadata.create_all(motor)
    yield


uygulama = FastAPI(title="Odunc Servisi", lifespan=yasam_dongusu)
hata_isleyicileri_kur(uygulama)
uygulama.include_router(oduncler.yonlendirici)
uygulama.include_router(raporlar.yonlendirici)


@uygulama.get("/saglik")
def saglik():
    return {"durum": "ok", "servis": "odunc-servisi"}
