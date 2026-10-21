"""Kullanıcı iş kuralları: kayıt, giriş, kimlik sorgulama, ilk yönetici."""
from datetime import date

from app.config import ayarlar
from app.models import GirisHatasi, Kullanici, Uye, Yonetici
from app.repositories.kullanici_repository import BenzersizlikHatasi, KullaniciDeposu
from app.schemas.kullanici import GirisGirdi, KayitGirdi
from app.services.hatalar import IsKuraliHatasi


class KullaniciServisi:
    def __init__(self, depo: KullaniciDeposu):
        self.depo = depo

    def kayitOl(self, girdi: KayitGirdi) -> Uye:
        """Yeni üye oluşturur (rol UYE); uyeNo yıl + 5 haneli id olarak üretilir."""
        uye = Uye(ad=girdi.ad.strip(), email=girdi.email.lower())
        uye.sifreAyarla(girdi.sifre)
        try:
            self.depo.ekle(uye)
        except BenzersizlikHatasi:
            raise IsKuraliHatasi(409, "Bu e-posta adresi zaten kayıtlı")
        uye.uyeNo = f"{date.today().year}{uye.id:05d}"
        self.depo.kaydet()
        return uye

    def girisYap(self, girdi: GirisGirdi) -> dict:
        """Bilgiler doğruysa {access_token, rol, ad} döndürür."""
        kullanici = self.depo.emailIleGetir(girdi.email.lower())
        if kullanici is None:
            raise IsKuraliHatasi(401, "E-posta veya şifre hatalı")
        try:
            token = kullanici.girisYap(girdi.email, girdi.sifre)
        except GirisHatasi as hata:
            raise IsKuraliHatasi(401, str(hata))
        return {"access_token": token, "rol": kullanici.rol, "ad": kullanici.ad}

    def kullaniciGetir(self, kullaniciId: int) -> Kullanici:
        kullanici = self.depo.idIleGetir(kullaniciId)
        if kullanici is None:
            raise IsKuraliHatasi(404, "Kullanıcı bulunamadı")
        return kullanici

    def ilkYoneticiOlustur(self) -> None:
        """Hiç yönetici yoksa .env'deki bilgilerle bir yönetici oluşturur."""
        if self.depo.yoneticiVarMi():
            return
        yonetici = Yonetici(ad=ayarlar.yonetici_ad, email=ayarlar.yonetici_email.lower())
        yonetici.sifreAyarla(ayarlar.admin_sifre)
        self.depo.ekle(yonetici)
        self.depo.kaydet()
