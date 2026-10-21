from pydantic import BaseModel, Field


class KitapGirdi(BaseModel):
    baslik: str = Field(min_length=1, max_length=200)
    yazar: str = Field(min_length=1, max_length=150)
    isbn: str = Field(min_length=1, max_length=20)
    toplamAdet: int = Field(default=1, ge=1)


class KitapCikti(BaseModel):
    """Kitap ve stok bilgisi birlikte döner."""

    kitapId: int
    baslik: str
    yazar: str
    isbn: str
    toplamAdet: int
    mevcutAdet: int

    @classmethod
    def kitaptan(cls, kitap) -> "KitapCikti":
        return cls(kitapId=kitap.kitapId, baslik=kitap.baslik, yazar=kitap.yazar, isbn=kitap.isbn,
                   toplamAdet=kitap.stok.toplamAdet, mevcutAdet=kitap.stok.mevcutAdet)


class StokCikti(BaseModel):
    kitapId: int
    mevcutAdet: int
