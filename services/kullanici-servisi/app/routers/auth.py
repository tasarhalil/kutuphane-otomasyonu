from fastapi import APIRouter, Depends

from app.routers.bagimliliklar import KimlikBilgisi, kullanici_servisi_al, mevcut_kullanici
from app.schemas.kullanici import GirisCikti, GirisGirdi, KayitGirdi, KullaniciCikti
from app.services.kullanici_servisi import KullaniciServisi

yonlendirici = APIRouter(prefix="/auth", tags=["auth"])


@yonlendirici.post("/kayit", response_model=KullaniciCikti, status_code=201)
def kayit(girdi: KayitGirdi, servis: KullaniciServisi = Depends(kullanici_servisi_al)):
    return servis.kayitOl(girdi)


@yonlendirici.post("/giris", response_model=GirisCikti)
def giris(girdi: GirisGirdi, servis: KullaniciServisi = Depends(kullanici_servisi_al)):
    return servis.girisYap(girdi)
