"""Ödünç ve gecikme raporu veri erişimi (yalnızca veritabanı işlemleri, iş kuralı yok)."""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import GecikmeRaporu, Odunc, OduncDurumu


class OduncDeposu:
    def __init__(self, oturum: Session):
        self.oturum = oturum

    def idIleGetir(self, oduncId: int) -> Odunc | None:
        return self.oturum.get(Odunc, oduncId)

    def uyeAktifKitapOduncuVarMi(self, uyeId: int, kitapId: int) -> bool:
        sorgu = select(Odunc).where(Odunc.uyeId == uyeId, Odunc.kitapId == kitapId,
                                    Odunc.durum == OduncDurumu.AKTIF)
        return self.oturum.scalars(sorgu).first() is not None

    def uyeAktifSayisi(self, uyeId: int) -> int:
        sorgu = select(func.count()).select_from(Odunc).where(Odunc.uyeId == uyeId,
                                                              Odunc.durum == OduncDurumu.AKTIF)
        return self.oturum.scalar(sorgu)

    def uyeninOduncleri(self, uyeId: int) -> list[Odunc]:
        return list(self.oturum.scalars(
            select(Odunc).where(Odunc.uyeId == uyeId).order_by(Odunc.oduncId.desc())))

    def tumOduncler(self, durum: OduncDurumu | None = None) -> list[Odunc]:
        sorgu = select(Odunc).order_by(Odunc.oduncId.desc())
        if durum:
            sorgu = sorgu.where(Odunc.durum == durum)
        return list(self.oturum.scalars(sorgu))

    def gecikmeRaporlari(self) -> list[GecikmeRaporu]:
        return list(self.oturum.scalars(select(GecikmeRaporu).order_by(GecikmeRaporu.oduncId.desc())))

    def suresiGecmisAktifler(self, bugun: date) -> list[Odunc]:
        sorgu = select(Odunc).where(Odunc.durum == OduncDurumu.AKTIF, Odunc.sonTeslimTarihi < bugun)
        return list(self.oturum.scalars(sorgu.order_by(Odunc.sonTeslimTarihi)))

    def ekle(self, odunc: Odunc) -> None:
        self.oturum.add(odunc)

    def flush(self) -> None:
        self.oturum.flush()

    def kaydet(self) -> None:
        self.oturum.commit()

    def geriAl(self) -> None:
        self.oturum.rollback()
