from fastapi import APIRouter, Depends

from app.models import OduncDurumu
from app.routers.bagimliliklar import KimlikBilgisi, mevcut_kullanici, odunc_servisi_al, yonetici_gerekli
from app.schemas.odunc import OduncCikti, OduncGirdi
from app.services.odunc_servisi import OduncServisi

yonlendirici = APIRouter(prefix="/oduncler", tags=["oduncler"])


@yonlendirici.post("", response_model=OduncCikti, status_code=201)
def odunc_al(girdi: OduncGirdi, kimlik: KimlikBilgisi = Depends(mevcut_kullanici),
             servis: OduncServisi = Depends(odunc_servisi_al)):
    """uyeId JWT'den (gateway başlığından) alınır."""
    return OduncCikti.oduncten(servis.oduncAl(kimlik.kimlik, girdi.kitapId))


# Not: "/benim" sabit yolu, "/{id}/iade" ile çakışmaz
@yonlendirici.get("/benim", response_model=list[OduncCikti])
def benim_oduncelerim(kimlik: KimlikBilgisi = Depends(mevcut_kullanici),
                      servis: OduncServisi = Depends(odunc_servisi_al)):
    """Üyenin yalnızca kendi ödünçleri."""
    return [OduncCikti.oduncten(o) for o in servis.benimOduncler(kimlik.kimlik)]


@yonlendirici.get("", response_model=list[OduncCikti])
def tum_oduncler(durum: OduncDurumu | None = None, servis: OduncServisi = Depends(odunc_servisi_al),
                 _: KimlikBilgisi = Depends(yonetici_gerekli)):
    """Yönetici: tüm ödünçler, isteğe bağlı durum filtresi."""
    return [OduncCikti.oduncten(o) for o in servis.tumOduncler(durum)]


@yonlendirici.post("/{odunc_id}/iade", response_model=OduncCikti)
def iade_et(odunc_id: int, kimlik: KimlikBilgisi = Depends(mevcut_kullanici),
            servis: OduncServisi = Depends(odunc_servisi_al)):
    return OduncCikti.oduncten(servis.iadeEt(odunc_id, kimlik.kimlik))
