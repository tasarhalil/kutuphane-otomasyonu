"""Kullanıcı veri erişimi (yalnızca veritabanı işlemleri, iş kuralı yok)."""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Kullanici, Rol


class BenzersizlikHatasi(Exception):
    """Benzersiz alan (ör. e-posta) zaten kayıtlı."""


class KullaniciDeposu:
    def __init__(self, oturum: Session):
        self.oturum = oturum

    def idIleGetir(self, kullaniciId: int) -> Kullanici | None:
        return self.oturum.get(Kullanici, kullaniciId)

    def emailIleGetir(self, email: str) -> Kullanici | None:
        return self.oturum.scalars(select(Kullanici).where(Kullanici.email == email)).first()

    def yoneticiVarMi(self) -> bool:
        return self.oturum.scalars(select(Kullanici).where(Kullanici.rol == Rol.YONETICI)).first() is not None

    def ekle(self, kullanici: Kullanici) -> None:
        """Ekler ve id üretilsin diye flush eder; benzersizlik ihlalinde BenzersizlikHatasi fırlatır."""
        self.oturum.add(kullanici)
        try:
            self.oturum.flush()
        except IntegrityError:
            self.oturum.rollback()
            raise BenzersizlikHatasi()

    def kaydet(self) -> None:
        self.oturum.commit()
