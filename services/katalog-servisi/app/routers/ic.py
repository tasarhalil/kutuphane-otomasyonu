from fastapi import APIRouter, Depends

from app.routers.bagimliliklar import ic_cagri_dogrula, kitap_servisi_al
from app.schemas.kitap import StokCikti
from app.services.kitap_servisi import KitapServisi

# İç uç noktalar: yalnızca diğer servisler çağırır (X-Ic-Anahtar ile korunur)
yonlendirici = APIRouter(prefix="/ic/kitaplar", tags=["ic"], dependencies=[Depends(ic_cagri_dogrula)])


@yonlendirici.post("/{kitap_id}/stok-dus", response_model=StokCikti)
def stok_dus(kitap_id: int, servis: KitapServisi = Depends(kitap_servisi_al)):
    stok = servis.stokDus(kitap_id)
    return StokCikti(kitapId=stok.kitapId, mevcutAdet=stok.mevcutAdet)


@yonlendirici.post("/{kitap_id}/stok-artir", response_model=StokCikti)
def stok_artir(kitap_id: int, servis: KitapServisi = Depends(kitap_servisi_al)):
    stok = servis.stokArtir(kitap_id)
    return StokCikti(kitapId=stok.kitapId, mevcutAdet=stok.mevcutAdet)
