"""Ödünç iş kuralları: ödünç alma, iade ve anlık gecikme hesabı."""
import logging
from datetime import date, timedelta
from decimal import Decimal

from app.config import ayarlar
from app.models import GecikmeRaporu, IadeHatasi, Odunc, OduncDurumu
from app.repositories.odunc_repository import OduncDeposu
from app.services.hatalar import IsKuraliHatasi
from app.services.katalog_istemcisi import KatalogHatasi, KatalogIstemcisi
from app.services.kullanici_istemcisi import KullaniciHatasi, KullaniciIstemcisi

kayit = logging.getLogger("odunc")

MAKS_AKTIF_ODUNC = 5


class OduncServisi:
    def __init__(self, depo: OduncDeposu, katalog: KatalogIstemcisi, kullanicilar: KullaniciIstemcisi):
        self.depo = depo
        self.katalog = katalog
        self.kullanicilar = kullanicilar

    def oduncAl(self, uyeId: int, kitapId: int, bugun: date | None = None) -> Odunc:
        """Sıra: üye doğrulama -> kural kontrolü -> stok-dus -> kayıt oluştur -> hata olursa stok-artir (telafi)."""
        bugun = bugun or date.today()

        # Üye doğrulama (Kullanici Servisi'ne iç çağrı)
        try:
            uye = self.kullanicilar.uyeGetir(uyeId)
        except KullaniciHatasi as hata:
            if hata.kod == 404:
                raise IsKuraliHatasi(404, "Üye bulunamadı")
            raise IsKuraliHatasi(502, hata.mesaj)
        if uye.get("rol") != "UYE":
            raise IsKuraliHatasi(403, "Yalnızca üyeler ödünç alabilir")

        # Aynı kitabı iade etmeden tekrar alamaz
        if self.depo.uyeAktifKitapOduncuVarMi(uyeId, kitapId):
            raise IsKuraliHatasi(409, "Bu kitabı iade etmeden tekrar ödünç alamazsınız")
        # En fazla 5 aktif ödünç
        if self.depo.uyeAktifSayisi(uyeId) >= MAKS_AKTIF_ODUNC:
            raise IsKuraliHatasi(409, f"En fazla {MAKS_AKTIF_ODUNC} aktif ödünç alabilirsiniz")

        # (1) Katalog'da stok düş: stok yoksa 409 gelir ve işlem iptal olur
        try:
            self.katalog.stokDus(kitapId)
        except KatalogHatasi as hata:
            raise IsKuraliHatasi(hata.kod if hata.kod in (404, 409) else 502, hata.mesaj)

        # (2) Ödünç kaydını oluştur
        try:
            odunc = Odunc(uyeId=uyeId, kitapId=kitapId, alisTarihi=bugun,
                          sonTeslimTarihi=bugun + timedelta(days=ayarlar.odunc_sure_gun))
            self.depo.ekle(odunc)
            self.depo.kaydet()
        except Exception:
            # (3) Telafi: düşülen stoğu geri ver
            self.depo.geriAl()
            try:
                self.katalog.stokArtir(kitapId)
            except KatalogHatasi:
                kayit.error("Telafi başarısız: kitapId=%s için stok-artir çağrılamadı", kitapId)
            raise
        return odunc

    def iadeEt(self, oduncId: int, uyeId: int, bugun: date | None = None) -> Odunc:
        """Üye yalnızca kendi ödüncünü iade eder. İade tarihi yazılır, stok-artir çağrılır."""
        odunc = self.depo.idIleGetir(oduncId)
        if odunc is None:
            raise IsKuraliHatasi(404, "Ödünç kaydı bulunamadı")
        if odunc.uyeId != uyeId:
            raise IsKuraliHatasi(403, "Yalnızca kendi ödüncünüzü iade edebilirsiniz")
        try:
            odunc.iadeEt(bugun)  # geç ise GECIKMIS_IADE + GecikmeRaporu otomatik oluşur
            self.depo.flush()
            self.katalog.stokArtir(odunc.kitapId)
        except IadeHatasi as hata:
            self.depo.geriAl()
            raise IsKuraliHatasi(409, str(hata))
        except KatalogHatasi as hata:
            self.depo.geriAl()  # stok artırılamadıysa iade kaydı da yazılmaz
            raise IsKuraliHatasi(502, hata.mesaj)
        self.depo.kaydet()
        return odunc

    def benimOduncler(self, uyeId: int) -> list[Odunc]:
        return self.depo.uyeninOduncleri(uyeId)

    def tumOduncler(self, durum: OduncDurumu | None = None) -> list[Odunc]:
        return self.depo.tumOduncler(durum)

    def kayitliGecikmeler(self) -> list[GecikmeRaporu]:
        return self.depo.gecikmeRaporlari()

    def anlikGecikmeler(self, bugun: date | None = None) -> list[dict]:
        """Açık ve süresi geçmiş ödünçler için gecikmeyi anlık hesaplar (veritabanına YAZMAZ)."""
        bugun = bugun or date.today()
        sonuc = []
        for odunc in self.depo.suresiGecmisAktifler(bugun):
            gun = (bugun - odunc.sonTeslimTarihi).days
            sonuc.append({"oduncId": odunc.oduncId, "uyeId": odunc.uyeId, "kitapId": odunc.kitapId,
                          "sonTeslimTarihi": odunc.sonTeslimTarihi, "gecikmeGun": gun,
                          "cezaTutari": float(Decimal(str(ayarlar.gunluk_ceza_tl)) * gun)})
        return sonuc
