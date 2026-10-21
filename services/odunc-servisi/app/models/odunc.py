"""odunc paketi: Odunc ve GecikmeRaporu (1 - 0..1 kompozisyon).

uyeId ve kitapId yalnızca ID'dir; başka servislerin tablolarına foreign key YOKTUR.
"""
import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import ayarlar
from app.database import Taban


class OduncDurumu(str, enum.Enum):
    AKTIF = "AKTIF"
    IADE_EDILDI = "IADE_EDILDI"
    GECIKMIS_IADE = "GECIKMIS_IADE"


class IadeHatasi(Exception):
    """Kitap zaten iade edilmiş."""


class Odunc(Taban):
    __tablename__ = "odunc"

    oduncId: Mapped[int] = mapped_column(primary_key=True)
    uyeId: Mapped[int] = mapped_column(index=True)   # FK yok, sadece ID
    kitapId: Mapped[int] = mapped_column(index=True)  # FK yok, sadece ID
    alisTarihi: Mapped[date]
    sonTeslimTarihi: Mapped[date]
    iadeTarihi: Mapped[date | None] = mapped_column(default=None)
    durum: Mapped[OduncDurumu] = mapped_column(
        SqlEnum(OduncDurumu, native_enum=False, length=20), default=OduncDurumu.AKTIF
    )

    # Kompozisyon: ödünç silinirse gecikme raporu da silinir
    gecikmeRaporu: Mapped["GecikmeRaporu | None"] = relationship(
        back_populates="odunc", uselist=False, cascade="all, delete-orphan"
    )

    def iadeEt(self, iadeTarihi: date | None = None) -> None:
        """Kitabı iade alır; geç ise durumu GECIKMIS_IADE yapıp gecikme raporu oluşturur."""
        if self.durum != OduncDurumu.AKTIF:
            raise IadeHatasi("Bu kitap zaten iade edilmiş")
        self.iadeTarihi = iadeTarihi or date.today()
        gecikme = (self.iadeTarihi - self.sonTeslimTarihi).days
        if gecikme > 0:
            self.durum = OduncDurumu.GECIKMIS_IADE
            rapor = GecikmeRaporu(gecikmeGun=gecikme)
            rapor.cezaHesapla()
            self.gecikmeRaporu = rapor
        else:
            self.durum = OduncDurumu.IADE_EDILDI


class GecikmeRaporu(Taban):
    __tablename__ = "gecikme_raporu"

    oduncId: Mapped[int] = mapped_column(ForeignKey("odunc.oduncId", ondelete="CASCADE"), primary_key=True)
    gecikmeGun: Mapped[int] = mapped_column(default=0)
    cezaTutari: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))

    odunc: Mapped[Odunc] = relationship(back_populates="gecikmeRaporu")

    def cezaHesapla(self) -> Decimal:
        """Ceza = gecikme günü x günlük ceza."""
        self.cezaTutari = Decimal(str(ayarlar.gunluk_ceza_tl)) * self.gecikmeGun
        return self.cezaTutari
