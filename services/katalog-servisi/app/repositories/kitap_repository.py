"""Kitap ve stok veri erişimi (yalnızca veritabanı işlemleri, iş kuralı yok)."""
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Kitap, Stok


class BenzersizlikHatasi(Exception):
    """ISBN zaten kayıtlı."""


class KitapDeposu:
    def __init__(self, oturum: Session):
        self.oturum = oturum

    def ara(self, arama: str) -> list[Kitap]:
        """Başlık, yazar veya ISBN içinde arar; boşsa tümünü döndürür."""
        sorgu = select(Kitap)
        if arama:
            desen = f"%{arama}%"
            sorgu = sorgu.where(or_(Kitap.baslik.ilike(desen), Kitap.yazar.ilike(desen), Kitap.isbn.ilike(desen)))
        return list(self.oturum.scalars(sorgu.order_by(Kitap.baslik)))

    def idIleGetir(self, kitapId: int) -> Kitap | None:
        return self.oturum.get(Kitap, kitapId)

    def sayi(self) -> int:
        return self.oturum.scalar(select(func.count()).select_from(Kitap))

    def ekle(self, kitap: Kitap) -> None:
        self.oturum.add(kitap)
        try:
            self.oturum.flush()
        except IntegrityError:
            self.oturum.rollback()
            raise BenzersizlikHatasi()

    def stokKilitle(self, kitapId: int) -> Stok | None:
        """Eşzamanlı ödünçlerde stok bozulmasın diye stok satırını kilitleyerek getirir."""
        return self.oturum.scalars(select(Stok).where(Stok.kitapId == kitapId).with_for_update()).first()

    def kaydet(self) -> None:
        self.oturum.commit()
