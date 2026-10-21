"""Tüm hataları {"detay": "Türkçe açıklama"} biçiminde döndürür."""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.services.hatalar import IsKuraliHatasi

VARSAYILAN = {404: "Kaynak bulunamadı", 405: "Bu yönteme izin verilmiyor"}


def hata_isleyicileri_kur(uygulama: FastAPI) -> None:
    @uygulama.exception_handler(IsKuraliHatasi)
    async def is_kurali_hatasi(_, hata: IsKuraliHatasi):
        return JSONResponse(status_code=hata.kod, content={"detay": hata.mesaj})

    @uygulama.exception_handler(StarletteHTTPException)
    async def http_hatasi(_, hata):
        if hata.detail in ("Not Found", "Method Not Allowed"):
            detay = VARSAYILAN.get(hata.status_code, str(hata.detail))
        else:
            detay = str(hata.detail)
        return JSONResponse(status_code=hata.status_code, content={"detay": detay})

    @uygulama.exception_handler(RequestValidationError)
    async def dogrulama_hatasi(_, hata):
        alanlar = ", ".join(sorted({".".join(str(x) for x in e["loc"][1:]) or "istek" for e in hata.errors()}))
        return JSONResponse(status_code=422, content={"detay": f"Geçersiz veya eksik alan: {alanlar}"})
