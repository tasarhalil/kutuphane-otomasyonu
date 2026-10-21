import { useEffect, useState } from "react";
import { iadeEt, kitapAra, oduncelerim } from "../api/kutuphane.js";
import { useToast } from "../bilesenler/Toast.jsx";

// "YYYY-MM-DD" -> bugüne göre kalan gün (negatif: gecikmiş)
function kalanGunHesapla(tarih) {
  const [y, a, g] = tarih.split("-").map(Number);
  const bugun = new Date();
  const bugunUtc = Date.UTC(bugun.getFullYear(), bugun.getMonth(), bugun.getDate());
  return Math.round((Date.UTC(y, a - 1, g) - bugunUtc) / 86400000);
}

function Rozet({ odunc }) {
  if (odunc.durum !== "AKTIF") {
    return <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">İade edildi</span>;
  }
  const kalan = kalanGunHesapla(odunc.sonTeslimTarihi);
  if (kalan < 0) {
    return <span className="rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-700">⚠ {-kalan} gün gecikmiş</span>;
  }
  const renk = kalan <= 3 ? "bg-amber-100 text-amber-700" : "bg-emerald-100 text-emerald-700";
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${renk}`}>{kalan === 0 ? "Son gün bugün" : `${kalan} gün kaldı`}</span>;
}

export default function OduncelerimSayfasi() {
  const toast = useToast();
  const [liste, setListe] = useState([]);
  const [basliklar, setBasliklar] = useState({});
  const [yukleniyor, setYukleniyor] = useState(true);

  const yukle = () => oduncelerim().then(setListe).catch((e) => toast.hata(e.message)).finally(() => setYukleniyor(false));
  useEffect(() => {
    yukle();
    // Kitap adlarını göstermek için katalogdan başlıklar alınır
    kitapAra("").then((k) => setBasliklar(Object.fromEntries(k.map((x) => [x.kitapId, x.baslik])))).catch(() => {});
  }, []);

  async function iade(id) {
    try {
      const o = await iadeEt(id);
      toast.basari(o.cezaTutari > 0 ? `İade edildi. Gecikme cezası: ${o.cezaTutari} TL` : "İade edildi.");
      yukle();
    } catch (e) {
      toast.hata(e.message);
    }
  }

  const sirali = [...liste].sort((a, b) => (a.durum === "AKTIF" ? 0 : 1) - (b.durum === "AKTIF" ? 0 : 1));

  return (
    <section className="max-w-5xl mx-auto p-4 space-y-4">
      <h2 className="text-2xl font-bold">Ödünçlerim</h2>
      {!yukleniyor && liste.length === 0 && <p className="text-center text-slate-500 py-10">Henüz ödünç aldığınız kitap yok.</p>}
      <ul className="space-y-3">
        {sirali.map((o) => {
          const gecikti = o.durum === "AKTIF" && kalanGunHesapla(o.sonTeslimTarihi) < 0;
          return (
            <li key={o.oduncId}
              className={`bg-white rounded-2xl border p-4 flex flex-col sm:flex-row sm:items-center gap-3 shadow-sm ${gecikti ? "border-rose-300 bg-rose-50/40" : "border-slate-200"}`}>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold truncate">{basliklar[o.kitapId] || `Kitap #${o.kitapId}`}</h3>
                <p className="text-sm text-slate-500">
                  Son teslim: <span className="font-medium text-slate-700">{o.sonTeslimTarihi}</span>
                  {o.iadeTarihi && <> · İade: {o.iadeTarihi}</>}
                  {o.cezaTutari > 0 && <> · Ceza: <span className="font-semibold text-rose-600">{o.cezaTutari} TL</span></>}
                </p>
              </div>
              <Rozet odunc={o} />
              {o.durum === "AKTIF" && (
                <button id={`iade-${o.oduncId}`} onClick={() => iade(o.oduncId)}
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition">
                  İade Et
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
