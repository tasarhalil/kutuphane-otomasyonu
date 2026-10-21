from fastapi import APIRouter, Depends

from app.routers.bagimliliklar import KimlikBilgisi, odunc_servisi_al, yonetici_gerekli
from app.schemas.odunc import AnlikGecikmeCikti, KayitliGecikmeCikti
from app.services.odunc_servisi import OduncServisi

yonlendirici = APIRouter(prefix="/raporlar/gecikme", tags=["raporlar"])


@yonlendirici.get("/kayitlar", response_model=list[KayitliGecikmeCikti])
def kayitli_gecikme_raporu(servis: OduncServisi = Depends(odunc_servisi_al),
                           _: KimlikBilgisi = Depends(yonetici_gerekli)):
    """Geç iade edilmiş ödünçlerin kayıtlı gecikme raporları (yönetici)."""
    return [KayitliGecikmeCikti(oduncId=r.oduncId, uyeId=r.odunc.uyeId, kitapId=r.odunc.kitapId,
                                gecikmeGun=r.gecikmeGun, cezaTutari=float(r.cezaTutari))
            for r in servis.kayitliGecikmeler()]


@yonlendirici.get("/anlik", response_model=list[AnlikGecikmeCikti])
def anlik_gecikme_raporu(servis: OduncServisi = Depends(odunc_servisi_al),
                         _: KimlikBilgisi = Depends(yonetici_gerekli)):
    """Hâlâ iade edilmemiş ve süresi geçmiş ödünçler; anlık hesaplanır, veritabanına yazılmaz."""
    return servis.anlikGecikmeler()
