"""katalog paketi: Kitap ve Stok (1-1 kompozisyon)."""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Taban


class StokHatasi(Exception):
    """Stok işlemi yapılamadı."""


class Kitap(Taban):
    __tablename__ = "kitap"

    kitapId: Mapped[int] = mapped_column(primary_key=True)
    baslik: Mapped[str] = mapped_column(String(200), index=True)
    yazar: Mapped[str] = mapped_column(String(150), index=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True)

    # Kompozisyon: kitap silinirse stok da silinir
    stok: Mapped["Stok"] = relationship(back_populates="kitap", uselist=False, cascade="all, delete-orphan")


class Stok(Taban):
    __tablename__ = "stok"

    # Aynı servis içinde olduğu için Kitap'a bağlanabilir (başka servise FK YOKTUR)
    kitapId: Mapped[int] = mapped_column(ForeignKey("kitap.kitapId", ondelete="CASCADE"), primary_key=True)
    toplamAdet: Mapped[int] = mapped_column(default=0)
    mevcutAdet: Mapped[int] = mapped_column(default=0)

    kitap: Mapped[Kitap] = relationship(back_populates="stok")

    def stokDus(self) -> None:
        """Ödünç verilince mevcut adedi bir azaltır."""
        if self.mevcutAdet <= 0:
            raise StokHatasi("Kitap stokta yok")
        self.mevcutAdet -= 1

    def stokArtir(self) -> None:
        """İade edilince mevcut adedi bir artırır."""
        if self.mevcutAdet >= self.toplamAdet:
            raise StokHatasi("Mevcut adet toplam adedi aşamaz")
        self.mevcutAdet += 1
