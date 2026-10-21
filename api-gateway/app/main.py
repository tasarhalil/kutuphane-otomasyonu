"""API Gateway: /api altındaki istekleri JWT doğrular, kimlik başlıklarını ekleyip servislere iletir."""
import json

from fastapi import FastAPI, Request, Response

from app import guvenlik, yonlendirme

uygulama = FastAPI(title="API Gateway")


def hata(kod: int, mesaj: str) -> Response:
    """Hata biçimi: {"detay": "..."}"""
    return Response(content=json.dumps({"detay": mesaj}, ensure_ascii=False), status_code=kod,
                    media_type="application/json")


@uygulama.get("/saglik")
def saglik():
    return {"durum": "ok", "servis": "api-gateway"}


@uygulama.api_route("/api/{yol:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def yonlendir(yol: str, istek: Request):
    yol = yol.strip("/")
    servis = yonlendirme.hedefServis(yol)
    if servis is None:
        return hata(404, "Kaynak bulunamadı")

    ekBasliklar: dict = {}
    if not yonlendirme.herkeseAcikMi(istek.method, yol):
        yetki = istek.headers.get("authorization", "")
        if not yetki.lower().startswith("bearer "):
            return hata(401, "Kimlik doğrulama gerekli")
        try:
            veri = guvenlik.tokenDogrula(yetki[7:])
        except guvenlik.TokenHatasi:
            return hata(401, "Geçersiz veya süresi dolmuş token")
        ekBasliklar = guvenlik.kimlikBasliklari(veri)

    try:
        return await yonlendirme.ilet(istek, servis, yol, ekBasliklar)
    except yonlendirme.ServiseUlasilamadi:
        return hata(502, "Servise ulaşılamadı")
