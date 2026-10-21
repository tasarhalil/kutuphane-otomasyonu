// Tüm istekler yalnızca API Gateway üzerinden (/api öneki, Nginx ile yönlendirilir) yapılır.
const OTURUM_ANAHTARI = "kutuphane_oturum";
export const OTURUM_BITTI_OLAYI = "oturum-bitti";

export function oturumuOku() {
  try {
    return JSON.parse(localStorage.getItem(OTURUM_ANAHTARI)) || null;
  } catch {
    return null;
  }
}

export function oturumuKaydet(oturum) {
  localStorage.setItem(OTURUM_ANAHTARI, JSON.stringify(oturum));
}

export function oturumuSil() {
  localStorage.removeItem(OTURUM_ANAHTARI);
}

export async function istek(yontem, yol, govde) {
  const oturum = oturumuOku();
  const basliklar = { "Content-Type": "application/json" };
  if (oturum?.access_token) basliklar.Authorization = `Bearer ${oturum.access_token}`;

  let yanit;
  try {
    yanit = await fetch(`/api${yol}`, {
      method: yontem,
      headers: basliklar,
      body: govde ? JSON.stringify(govde) : undefined,
    });
  } catch {
    throw new Error("Sunucuya ulaşılamadı");
  }
  const veri = await yanit.json().catch(() => null);
  if (yanit.status === 401 && oturum) {
    // Süresi dolmuş / geçersiz token: oturumu temizle ve girişe yönlendir
    oturumuSil();
    window.dispatchEvent(new Event(OTURUM_BITTI_OLAYI));
    throw new Error("Oturum süresi doldu, lütfen tekrar giriş yapın");
  }
  if (!yanit.ok) {
    const detay = veri?.detay ?? veri?.detail;
    throw new Error(typeof detay === "string" ? detay : "Beklenmeyen bir hata oluştu");
  }
  return veri;
}
