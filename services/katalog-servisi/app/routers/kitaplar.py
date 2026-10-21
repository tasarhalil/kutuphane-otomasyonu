from fastapi import APIRouter, Depends

from app.routers.bagimliliklar import KimlikBilgisi, kitap_servisi_al, mevcut_kullanici, yonetici_gerekli
from app.schemas.kitap import KitapCikti, KitapGirdi
from app.services.kitap_servisi import KitapServisi

yonlendirici = APIRouter(prefix="/kitaplar", tags=["kitaplar"])


@yonlendirici.get("", response_model=list[KitapCikti])
def kitap_ara(arama: str = "", servis: KitapServisi = Depends(kitap_servisi_al),
              _: KimlikBilgisi = Depends(mevcut_kullanici)):
    return [KitapCikti.kitaptan(k) for k in servis.ara(arama)]


@yonlendirici.get("/{kitap_id}", response_model=KitapCikti)
def kitap_getir(kitap_id: int, servis: KitapServisi = Depends(kitap_servisi_al),
                _: KimlikBilgisi = Depends(mevcut_kullanici)):
    return KitapCikti.kitaptan(servis.getir(kitap_id))


@yonlendirici.post("", response_model=KitapCikti, status_code=201)
def kitap_ekle(girdi: KitapGirdi, servis: KitapServisi = Depends(kitap_servisi_al),
               _: KimlikBilgisi = Depends(yonetici_gerekli)):
    return KitapCikti.kitaptan(servis.ekle(girdi))
