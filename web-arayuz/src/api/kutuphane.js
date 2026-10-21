import { istek } from "./istemci.js";

export const girisYap = (email, sifre) => istek("POST", "/auth/giris", { email, sifre });
export const kayitOl = (ad, email, sifre) => istek("POST", "/auth/kayit", { ad, email, sifre });

export const kitapAra = (arama = "") => istek("GET", `/kitaplar?arama=${encodeURIComponent(arama)}`);
export const kitapEkle = (kitap) => istek("POST", "/kitaplar", kitap);

export const oduncAl = (kitapId) => istek("POST", "/oduncler", { kitapId });
export const oduncelerim = () => istek("GET", "/oduncler/benim");
export const iadeEt = (oduncId) => istek("POST", `/oduncler/${oduncId}/iade`);

export const anlikGecikmeler = () => istek("GET", "/raporlar/gecikme/anlik");
export const kayitliGecikmeler = () => istek("GET", "/raporlar/gecikme/kayitlar");
