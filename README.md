# Kütüphane Otomasyonu (Mikroservis Mimarisi)

Yazılım Tasarım ve Mimarisi dersi ödevi.

## Mimari özet
Tarayıcı yalnızca **web-arayuz** (Nginx) ile konuşur; Nginx `/api` isteklerini **api-gateway**'e iletir.
Gateway JWT'yi doğrular, `X-Kullanici-Id` / `X-Kullanici-Rol` başlıklarını ekler ve isteği ilgili servise yönlendirir.
Her servisin kendi PostgreSQL veritabanı vardır; servisler birbirinin veritabanına erişmez, yalnızca ID ile ilişki kurar (foreign key yok).

```
Tarayıcı -> web-arayuz (:3000) -> api-gateway (:8000) -> kullanici-servisi (:8001) -> kullanici-db
                                                      -> katalog-servisi  (:8002) -> katalog-db
                                                      -> odunc-servisi    (:8003) -> odunc-db
odunc-servisi -> kullanici-servisi (üye doğrulama), katalog-servisi (stok düş/artır)   [X-Ic-Anahtar]
```

## Teknoloji yığını
- Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2
- PostgreSQL 16 (her servis için ayrı veritabanı container'ı)
- Servisler arası iletişim: REST (httpx), iç uç noktalar `X-Ic-Anahtar` ile korunur
- Kimlik doğrulama: JWT (PyJWT), şifreler bcrypt ile hashlenir
- Arayüz: React + Vite + Tailwind CSS, Nginx ile sunulur
- Test: pytest

## Çalıştırma
```
copy .env.example .env
docker compose up --build
```
- Arayüz: http://localhost:3000
- Gateway: http://localhost:8000 (kök adres sayfa sunmaz; `/saglik` ve `/docs` çalışır)
- Swagger: Kullanici http://localhost:8001/docs - Katalog http://localhost:8002/docs - Odunc http://localhost:8003/docs

## Varsayılan hesap
- **Yönetici:** `admin@kutuphane.local` / `Admin123!` (şifre `.env` içindeki `ADMIN_SIFRE`)
- Öğrenci hesabı arayüzdeki "Kayıt ol" ile oluşturulur.

## Uç nokta listesi
Arayüz ve dış istemciler yalnızca gateway üzerinden `/api/...` yoluyla erişir (aşağıdaki yollar `/api` önekiyle).

| Yöntem | Yol | Yetki | Servis |
|---|---|---|---|
| POST | `/auth/kayit` | herkese açık | kullanici |
| POST | `/auth/giris` | herkese açık | kullanici |
| GET | `/kullanicilar/ben` | giriş yapmış | kullanici |
| GET | `/kitaplar?arama=` | giriş yapmış | katalog |
| GET | `/kitaplar/{id}` | giriş yapmış | katalog |
| POST | `/kitaplar` | YONETICI | katalog |
| POST | `/oduncler` | UYE | odunc |
| GET | `/oduncler/benim` | giriş yapmış | odunc |
| GET | `/oduncler?durum=` | YONETICI | odunc |
| POST | `/oduncler/{id}/iade` | ödüncü alan üye | odunc |
| GET | `/raporlar/gecikme/anlik` | YONETICI | odunc |
| GET | `/raporlar/gecikme/kayitlar` | YONETICI | odunc |

İç uç noktalar (gateway dışarıya kapatır, `X-Ic-Anahtar` gerekir):
`GET /ic/kullanicilar/{id}`, `POST /ic/kitaplar/{id}/stok-dus`, `POST /ic/kitaplar/{id}/stok-artir`.

## Klasör yapısı
```
docs/            UML diyagramları (PlantUML)
api-gateway/     tek giriş noktası (JWT doğrulama, yönlendirme)
services/
  kullanici-servisi/   kayıt, giriş, kullanıcı doğrulama
  katalog-servisi/     kitap ve stok
  odunc-servisi/       ödünç, iade, gecikme raporu
web-arayuz/      React arayüzü + Nginx
docker-compose.yml, .env.example
```

## Katmanlı mimari (her serviste)
`routers` → `services` (iş kuralları) → `repositories` (veri erişimi) → `models`

İş kuralları router içine yazılmaz; router yalnızca isteği alır, servise iletir ve yanıtı döndürür.

## Başlangıç verisi (seed)
- **Yönetici hesabı:** Kullanici Servisi ilk açılışta yönetici yoksa oluşturur.
- **Örnek kitaplar:** Katalog Servisi katalog boşsa 10 örnek kitabı stoklarıyla ekler.

Her iki işlem de tekrar çalıştırıldığında mevcut veriyi değiştirmez.

## Ödünç kuralları
- Bir üye en fazla 5 aktif ödünç alabilir; aynı kitabı iade etmeden tekrar alamaz.
- Ödünç alınca Katalog'da stok düşülür; kayıt başarısız olursa stok geri artırılır (telafi).
- Geç iade edilirse durum `GECIKMIS_IADE` olur ve gecikme günü x günlük ceza `GecikmeRaporu` olarak kaydedilir.
- `.env`: `ODUNC_SURE_GUN` (varsayılan 14), `GUNLUK_CEZA_TL` (varsayılan 5)

## Web arayüzü
Giriş/Kayıt, Kitaplar (arama, stok göstergesi, Ödünç Al), Ödünçlerim (kalan gün, gecikme uyarısı, İade Et)
ve yalnızca yöneticiye açık panel (Kitap Ekle, anlık/kayıtlı Gecikme Raporu). JWT `localStorage`'da tutulur,
401'de girişe yönlendirilir, mesajlar toast ile gösterilir. Arayüz yalnızca `/api` yoluna istek atar.

## Testler
Her servis (`api-gateway/` ve `services/*/`) kendi klasöründen: `python -m pytest`

## Ödev maddeleri ile eşleşme
| Ödev maddesi | Dosya |
|---|---|
| Class (sınıf) diyagramı | `docs/class-diagram.puml` |
| Object (nesne) diyagramı | `docs/object-diagram.puml` |
| Paket diyagramı | `docs/package-diagram.puml` |
| Deployment (dağıtım) diyagramı | `docs/deployment-diagram.puml` |

## Notlar (eksik ayrıntılar için yapılan basit tamamlamalar)
- Servislerin Swagger (`/docs`) sayfalarına erişim için Kullanici/Katalog/Odunc portları host'ta yalnızca `127.0.0.1`'e açıldı; dışarıdan erişilemez.
- Giriş şeması `EmailStr` kullanmaz; `admin@kutuphane.local` gibi özel alan adları reddedilmesin diye.
- `Uye.kitapAra/oduncAl` ve `Yonetici.kitapEkle/gecikmeRaporuAl` metotları, arayüzden gateway'e yapılacak çağrıyı temsil eden sözlük döndürür (servisler arası çağrı yapmaz).
- Kitap adları Ödünçlerim sayfasında katalog listesinden eşlenir (ayrı bir uç nokta eklenmedi).
- Üretimde `JWT_GIZLI_ANAHTAR` ve `ADMIN_SIFRE` değerlerini değiştirin; JWT anahtarı en az 32 bayt olmalıdır.
