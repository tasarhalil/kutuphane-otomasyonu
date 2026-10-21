from pydantic import BaseModel, ConfigDict, EmailStr, Field


class KayitGirdi(BaseModel):
    ad: str = Field(min_length=2, max_length=100)
    email: EmailStr
    sifre: str = Field(min_length=6, max_length=72)


class GirisGirdi(BaseModel):
    # EmailStr kullanılmaz: admin@kutuphane.local gibi özel alan adlarını reddeder
    email: str = Field(min_length=3, max_length=150)
    sifre: str = Field(min_length=1, max_length=72)


class KullaniciCikti(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ad: str
    email: str
    rol: str
    uyeNo: str | None = None


class GirisCikti(BaseModel):
    access_token: str
    rol: str
    ad: str
