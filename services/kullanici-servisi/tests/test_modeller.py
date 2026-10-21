import jwt
import pytest

from app.config import ayarlar
from app.models import GirisHatasi, Kullanici, Uye, Yonetici


def uye_olustur(oturum, email="ali@uni.edu"):
    uye = Uye(ad="Ali", email=email, uyeNo="2024001")
    uye.sifreAyarla("gizli123")
    oturum.add(uye)
    oturum.commit()
    return uye


def test_kullanici_soyut():
    with pytest.raises(TypeError):
        Kullanici(ad="x")


def test_single_table_kalitim(oturum):
    uye_olustur(oturum)
    y = Yonetici(ad="Admin", email="a@uni.edu")
    y.sifreAyarla("x")
    oturum.add(y)
    oturum.commit()
    assert {k.rol for k in oturum.query(Kullanici).all()} == {"UYE", "YONETICI"}
    assert isinstance(oturum.query(Kullanici).filter_by(email="a@uni.edu").one(), Yonetici)


def test_giris_yap_jwt_dondurur(oturum):
    uye = uye_olustur(oturum)
    token = uye.girisYap("ali@uni.edu", "gizli123")
    veri = jwt.decode(token, ayarlar.jwt_gizli_anahtar, algorithms=[ayarlar.jwt_algoritma])
    assert veri["sub"] == str(uye.id) and veri["rol"] == "UYE"
    assert uye.sifreHash != "gizli123"


def test_yanlis_sifre(oturum):
    uye = uye_olustur(oturum)
    with pytest.raises(GirisHatasi):
        uye.girisYap("ali@uni.edu", "yanlis")


def test_email_benzersiz(oturum):
    from sqlalchemy.exc import IntegrityError
    uye_olustur(oturum)
    with pytest.raises(IntegrityError):
        uye_olustur(oturum)
