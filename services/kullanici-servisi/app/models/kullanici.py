"""kullanici paketi: Kullanici (soyut), Uye ve Yonetici sınıfları (single-table inheritance)."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.config import ayarlar
from app.database import Taban


class Rol:
    UYE = "UYE"
    YONETICI = "YONETICI"


class GirisHatasi(Exception):
    """E-posta veya şifre hatalı."""


class Kullanici(Taban):
    """Soyut kullanıcı. Doğrudan örneklenemez; Uye veya Yonetici kullanılır.

    Tüm alt sınıflar tek tabloda tutulur; `rol` sütunu ayırt edicidir.
    """

    __tablename__ = "kullanici"

    id: Mapped[int] = mapped_column(primary_key=True)
    ad: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    sifreHash: Mapped[str] = mapped_column(String(100))
    rol: Mapped[str] = mapped_column(String(20))
    # Yalnızca Uye için dolu olur (single-table inheritance)
    uyeNo: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    __mapper_args__ = {"polymorphic_on": "rol"}

    def __new__(cls, *args, **kwargs):
        if cls is Kullanici:
            raise TypeError("Kullanici soyut bir sınıftır; Uye veya Yonetici oluşturun")
        return super().__new__(cls)

    # ---- Şifre yardımcıları (bcrypt) ----
    def sifreAyarla(self, sifre: str) -> None:
        self.sifreHash = bcrypt.hashpw(sifre.encode(), bcrypt.gensalt()).decode()

    def sifreDogrula(self, sifre: str) -> bool:
        return bcrypt.checkpw(sifre.encode(), self.sifreHash.encode())

    def girisYap(self, email: str, sifre: str) -> str:
        """E-posta ve şifre bu kullanıcıya aitse JWT döndürür, değilse GirisHatasi fırlatır.

        Kullanıcıyı e-postayla bulmak veri erişimidir; servis katmanı bunu depodan yapar.
        """
        if self.email.lower() != email.lower() or not self.sifreDogrula(sifre):
            raise GirisHatasi("E-posta veya şifre hatalı")
        bitis = datetime.now(timezone.utc) + timedelta(minutes=ayarlar.jwt_sure_dakika)
        return jwt.encode(
            {"sub": str(self.id), "rol": self.rol, "exp": bitis},
            ayarlar.jwt_gizli_anahtar,
            algorithm=ayarlar.jwt_algoritma,
        )


class Uye(Kullanici):
    """Kitap arayıp ödünç alan öğrenci."""

    __mapper_args__ = {"polymorphic_identity": Rol.UYE}

    def kitapAra(self, anahtar: str) -> dict:
        """Arayüzden gateway'e yapılan çağrıyı temsil eder (servisler arası çağrı yapmaz)."""
        return {"yontem": "GET", "yol": "/api/kitaplar", "parametreler": {"arama": anahtar}}

    def oduncAl(self, kitapId: int) -> dict:
        """Arayüzden gateway'e yapılan çağrıyı temsil eder."""
        return {"yontem": "POST", "yol": "/api/oduncler", "govde": {"kitapId": kitapId}}


class Yonetici(Kullanici):
    """Kitap ekleyen ve gecikme raporu alan yönetici."""

    __mapper_args__ = {"polymorphic_identity": Rol.YONETICI}

    def kitapEkle(self, kitap: dict) -> dict:
        """Arayüzden gateway'e yapılan çağrıyı temsil eder."""
        return {"yontem": "POST", "yol": "/api/kitaplar", "govde": kitap}

    def gecikmeRaporuAl(self) -> dict:
        """Arayüzden gateway'e yapılan çağrıyı temsil eder."""
        return {"yontem": "GET", "yol": "/api/raporlar/gecikme/anlik"}
