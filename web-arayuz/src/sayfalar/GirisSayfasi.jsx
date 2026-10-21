import { useState } from "react";
import { girisYap, kayitOl } from "../api/kutuphane.js";
import { useToast } from "../bilesenler/Toast.jsx";

export default function GirisSayfasi({ girildi }) {
  const toast = useToast();
  const [kayitModu, setKayitModu] = useState(false);
  const [form, setForm] = useState({ ad: "", email: "", sifre: "" });
  const [bekliyor, setBekliyor] = useState(false);

  const degistir = (alan) => (e) => setForm({ ...form, [alan]: e.target.value });

  async function gonder(e) {
    e.preventDefault();
    setBekliyor(true);
    try {
      if (kayitModu) {
        await kayitOl(form.ad, form.email, form.sifre);
        toast.basari("Kayıt oluşturuldu");
      }
      girildi(await girisYap(form.email, form.sifre));
    } catch (err) {
      toast.hata(err.message);
    } finally {
      setBekliyor(false);
    }
  }

  const alan = "w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500";

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-violet-600 to-fuchsia-600 p-6">
      <form onSubmit={gonder} className="bg-white/95 rounded-2xl shadow-2xl p-8 w-full max-w-sm space-y-4">
        <div className="text-center space-y-1">
          <div className="text-4xl">📚</div>
          <h1 className="text-2xl font-bold text-indigo-700">Kütüphane Otomasyonu</h1>
          <p className="text-sm text-slate-500">{kayitModu ? "Yeni hesap oluşturun" : "Hesabınıza giriş yapın"}</p>
        </div>
        {kayitModu && (
          <input id="ad" className={alan} placeholder="Ad Soyad" minLength={2} value={form.ad} onChange={degistir("ad")} required />
        )}
        <input id="email" className={alan} placeholder="E-posta" autoComplete="username" value={form.email} onChange={degistir("email")} required />
        <input id="sifre" type="password" className={alan} placeholder="Şifre" minLength={kayitModu ? 6 : 1}
          autoComplete={kayitModu ? "new-password" : "current-password"} value={form.sifre} onChange={degistir("sifre")} required />
        <button id="gonder" disabled={bekliyor}
          className="w-full rounded-lg bg-indigo-600 py-2 font-semibold text-white hover:bg-indigo-700 transition disabled:opacity-60">
          {bekliyor ? "Bekleyin..." : kayitModu ? "Kayıt Ol" : "Giriş Yap"}
        </button>
        <button type="button" id="mod-degistir" onClick={() => setKayitModu(!kayitModu)} className="w-full text-sm text-indigo-600 hover:underline">
          {kayitModu ? "Hesabım var, giriş yap" : "Hesabın yok mu? Kayıt ol"}
        </button>
      </form>
    </main>
  );
}
