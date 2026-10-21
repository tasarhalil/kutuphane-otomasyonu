import { useEffect, useState } from "react";
import { anlikGecikmeler, kayitliGecikmeler, kitapEkle } from "../api/kutuphane.js";
import { useToast } from "../bilesenler/Toast.jsx";

const BOS = { baslik: "", yazar: "", isbn: "", toplamAdet: 1 };

export default function YonetimSayfasi() {
  const toast = useToast();
  const [form, setForm] = useState(BOS);
  const [sekme, setSekme] = useState("anlik");
  const [anlik, setAnlik] = useState([]);
  const [kayitli, setKayitli] = useState([]);

  useEffect(() => {
    anlikGecikmeler().then(setAnlik).catch((e) => toast.hata(e.message));
    kayitliGecikmeler().then(setKayitli).catch((e) => toast.hata(e.message));
  }, []);

  async function ekle(e) {
    e.preventDefault();
    try {
      await kitapEkle({ ...form, toplamAdet: Number(form.toplamAdet) });
      toast.basari("Kitap eklendi.");
      setForm(BOS);
    } catch (err) {
      toast.hata(err.message);
    }
  }

  const alan = "rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500";
  const degistir = (a) => (e) => setForm({ ...form, [a]: e.target.value });

  const satirlar = sekme === "anlik" ? anlik : kayitli;
  const toplamCeza = satirlar.reduce((t, g) => t + Number(g.cezaTutari || 0), 0);

  return (
    <section className="max-w-5xl mx-auto p-4 space-y-8">
      <form onSubmit={ekle} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 grid gap-3 sm:grid-cols-4">
        <h2 className="sm:col-span-4 text-xl font-bold">Kitap Ekle</h2>
        <input id="kitap-baslik" className={alan} placeholder="Başlık" value={form.baslik} onChange={degistir("baslik")} required />
        <input id="kitap-yazar" className={alan} placeholder="Yazar" value={form.yazar} onChange={degistir("yazar")} required />
        <input id="kitap-isbn" className={alan} placeholder="ISBN" value={form.isbn} onChange={degistir("isbn")} required />
        <input id="kitap-adet" type="number" min="1" className={alan} placeholder="Adet" value={form.toplamAdet} onChange={degistir("toplamAdet")} required />
        <button id="kitap-ekle" className="sm:col-span-4 rounded-lg bg-indigo-600 py-2 font-medium text-white hover:bg-indigo-700 transition">Ekle</button>
      </form>

      <div className="space-y-3">
        <h2 className="text-xl font-bold">Gecikme Raporu</h2>
        <div role="tablist" className="inline-flex rounded-lg bg-slate-200/70 p-1">
          {[["anlik", "Anlık"], ["kayitli", "Kayıtlı"]].map(([k, ad]) => (
            <button key={k} id={`sekme-${k}`} role="tab" aria-selected={sekme === k} onClick={() => setSekme(k)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${sekme === k ? "bg-white shadow text-indigo-700" : "text-slate-600"}`}>
              {ad} ({(k === "anlik" ? anlik : kayitli).length})
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between rounded-2xl bg-gradient-to-r from-rose-500 to-orange-500 p-4 text-white shadow">
          <span className="text-sm font-medium opacity-90">Toplam ceza</span>
          <span id="toplam-ceza" className="text-2xl font-bold">{toplamCeza.toFixed(2)} TL</span>
        </div>

        <ul className="space-y-2">
          {satirlar.length === 0 && <li className="text-slate-500 text-center py-6">Gecikme kaydı yok.</li>}
          {satirlar.map((g) => (
            <li key={g.oduncId} className="bg-white rounded-xl border border-slate-200 p-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
              <span className="font-medium">Üye #{g.uyeId}</span>
              <span className="text-slate-500">Kitap #{g.kitapId}</span>
              {g.sonTeslimTarihi && <span className="text-slate-500">Son teslim {g.sonTeslimTarihi}</span>}
              <span className="rounded-full bg-rose-100 px-2 py-0.5 text-xs font-semibold text-rose-700">{g.gecikmeGun} gün</span>
              <span className="ml-auto font-semibold text-rose-600">{Number(g.cezaTutari).toFixed(2)} TL</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
