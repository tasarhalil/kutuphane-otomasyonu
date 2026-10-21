from fastapi import APIRouter, Depends

from app.routers.bagimliliklar import (KimlikBilgisi, ic_cagri_dogrula, kullanici_servisi_al,
                                       mevcut_kullanici)
from app.schemas.kullanici import KullaniciCikti
from app.services.kullanici_servisi import KullaniciServisi

yonlendirici = APIRouter(tags=["kullanicilar"])


@yonlendirici.get("/kullanicilar/ben", response_model=KullaniciCikti)
def ben(kimlik: KimlikBilgisi = Depends(mevcut_kullanici),
        servis: KullaniciServisi = Depends(kullanici_servisi_al)):
    return servis.kullaniciGetir(kimlik.kimlik)


# İç uç nokta: yalnızca diğer servisler çağırır (X-Ic-Anahtar ile korunur)
@yonlendirici.get("/ic/kullanicilar/{kullanici_id}", response_model=KullaniciCikti,
                  dependencies=[Depends(ic_cagri_dogrula)])
def ic_kullanici_getir(kullanici_id: int, servis: KullaniciServisi = Depends(kullanici_servisi_al)):
    """Üye doğrulama: kullanıcı var mı ve rolü ne?"""
    return servis.kullaniciGetir(kullanici_id)
