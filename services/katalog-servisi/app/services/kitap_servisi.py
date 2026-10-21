"""Katalog iş kuralları: kitap arama/ekleme ve stok işlemleri."""
from app.models import Kitap, Stok, StokHatasi
from app.repositories.kitap_repository import BenzersizlikHatasi, KitapDeposu
from app.schemas.kitap import KitapGirdi
from app.services.hatalar import IsKuraliHatasi


class KitapServisi:
    def __init__(self, depo: KitapDeposu):
        self.depo = depo

    def ara(self, arama: str = "") -> list[Kitap]:
        return self.depo.ara(arama)

    def getir(self, kitapId: int) -> Kitap:
        kitap = self.depo.idIleGetir(kitapId)
        if kitap is None:
            raise IsKuraliHatasi(404, "Kitap bulunamadı")
        return kitap

    def ekle(self, girdi: KitapGirdi) -> Kitap:
        kitap = Kitap(baslik=girdi.baslik, yazar=girdi.yazar, isbn=girdi.isbn)
        kitap.stok = Stok(toplamAdet=girdi.toplamAdet, mevcutAdet=girdi.toplamAdet)
        try:
            self.depo.ekle(kitap)
        except BenzersizlikHatasi:
            raise IsKuraliHatasi(409, "Bu ISBN zaten kayıtlı")
        self.depo.kaydet()
        return kitap

    def _stokGetir(self, kitapId: int) -> Stok:
        stok = self.depo.stokKilitle(kitapId)
        if stok is None:
            raise IsKuraliHatasi(404, "Kitap bulunamadı")
        return stok

    def stokDus(self, kitapId: int) -> Stok:
        """Ödünç verilirken çağrılır; stok yoksa 409."""
        stok = self._stokGetir(kitapId)
        try:
            stok.stokDus()
        except StokHatasi as hata:
            raise IsKuraliHatasi(409, str(hata))
        self.depo.kaydet()
        return stok

    def stokArtir(self, kitapId: int) -> Stok:
        """İade veya telafi sırasında çağrılır."""
        stok = self._stokGetir(kitapId)
        try:
            stok.stokArtir()
        except StokHatasi as hata:
            raise IsKuraliHatasi(409, str(hata))
        self.depo.kaydet()
        return stok
