from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models import OduncDurumu


class OduncGirdi(BaseModel):
    kitapId: int


class OduncCikti(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    oduncId: int
    uyeId: int
    kitapId: int
    alisTarihi: date
    sonTeslimTarihi: date
    iadeTarihi: date | None = None
    durum: OduncDurumu
    gecikmeGun: int = 0
    cezaTutari: float = 0.0

    @classmethod
    def oduncten(cls, odunc) -> "OduncCikti":
        """Varsa gecikme raporundaki gün ve ceza bilgisiyle birlikte."""
        rapor = odunc.gecikmeRaporu
        return cls(oduncId=odunc.oduncId, uyeId=odunc.uyeId, kitapId=odunc.kitapId,
                   alisTarihi=odunc.alisTarihi, sonTeslimTarihi=odunc.sonTeslimTarihi,
                   iadeTarihi=odunc.iadeTarihi, durum=odunc.durum,
                   gecikmeGun=rapor.gecikmeGun if rapor else 0,
                   cezaTutari=float(rapor.cezaTutari) if rapor else 0.0)


class KayitliGecikmeCikti(BaseModel):
    oduncId: int
    uyeId: int
    kitapId: int
    gecikmeGun: int
    cezaTutari: float


class AnlikGecikmeCikti(BaseModel):
    oduncId: int
    uyeId: int
    kitapId: int
    sonTeslimTarihi: date
    gecikmeGun: int
    cezaTutari: float
