"""Servis katmanı hataları (HTTP'den bağımsız; router bunları yanıta çevirir)."""


class IsKuraliHatasi(Exception):
    """Bir iş kuralı ihlal edildi. `kod` istemciye dönecek HTTP durum koduna karşılık gelir."""

    def __init__(self, kod: int, mesaj: str):
        super().__init__(mesaj)
        self.kod = kod
        self.mesaj = mesaj
