import { useEffect, useState } from "react";
import { kitapAra, oduncAl } from "../api/kutuphane.js";
import { useToast } from "../bilesenler/Toast.jsx";

function StokGostergesi({ mevcut, toplam }) {
  const oran = toplam > 0 ? Math.round((mevcut / toplam) * 100) : 0;
  const renk = mevcut === 0 ? "bg-rose-500" : oran <= 30 ? "bg-amber-500" : "bg-emerald-500";
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-500 mb-1">
        <span>Mevcut stok</span>
        <span className="font-semibold text-slate-700">{mevcut} / {toplam}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
        <div className={`h-full rounded-full transition-all ${renk}`} style={{ width: `${oran}%` }} />
      </div>
    </div>
  );
}

export default function KitaplarSayfasi({ oturum }) {
  const toast = useToast();
  const [arama, setArama] = useState("");
  const [kitaplar, setKitaplar] = useState([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  const yukle = (aranan = arama) => {
    setYukleniyor(true);
    return kitapAra(aranan).then(setKitaplar).catch((e) => toast.hata(e.message)).finally(() => setYukleniyor(false));
  };
  useEffect(() => { yukle(); }, []);

  async function oduncVer(kitapId) {
    try {
      const odunc = await oduncAl(kitapId);
      toast.basari(`Ödünç alındı. Son teslim: ${odunc.sonTeslimTarihi}`);
      yukle();
    } catch (e) {
      toast.hata(e.message);
    }
  }

  return (
    <section className="max-w-5xl mx-auto p-4 space-y-4">
      <h2 className="text-2xl font-bold">Kitaplar</h2>
      <form onSubmit={(e) => { e.preventDefault(); yukle(); }} className="flex gap-2">
        <input id="arama" value={arama} onChange={(e) => setArama(e.target.value)} placeholder="Başlık, yazar veya ISBN ara..."
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        <button id="ara" className="rounded-lg bg-indigo-600 px-5 font-medium text-white hover:bg-indigo-700 transition">Ara</button>
      </form>
      {!yukleniyor && kitaplar.length === 0 && (
        <p className="text-center text-slate-500 py-10">Kitap bulunamadı.</p>
      )}
      <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {kitaplar.map((k) => (
          <li key={k.kitapId}
            className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 flex flex-col gap-3 hover:shadow-md hover:-translate-y-0.5 transition">
            <div>
              <h3 className="font-semibold text-slate-900 leading-snug">{k.baslik}</h3>
              <p className="text-sm text-slate-500">{k.yazar}</p>
              <p className="text-xs text-slate-400 mt-0.5">ISBN {k.isbn}</p>
            </div>
            <StokGostergesi mevcut={k.mevcutAdet} toplam={k.toplamAdet} />
            {oturum.rol === "UYE" && (
              <button id={`odunc-${k.kitapId}`} disabled={k.mevcutAdet < 1} onClick={() => oduncVer(k.kitapId)}
                className="mt-auto rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 transition disabled:opacity-40 disabled:cursor-not-allowed">
                {k.mevcutAdet < 1 ? "Stokta yok" : "Ödünç Al"}
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
