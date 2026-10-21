import { useEffect, useState } from "react";
import { OTURUM_BITTI_OLAYI, oturumuKaydet, oturumuOku, oturumuSil } from "./api/istemci.js";
import UstMenu from "./bilesenler/UstMenu.jsx";
import { ToastSaglayici, useToast } from "./bilesenler/Toast.jsx";
import GirisSayfasi from "./sayfalar/GirisSayfasi.jsx";
import KitaplarSayfasi from "./sayfalar/KitaplarSayfasi.jsx";
import OduncelerimSayfasi from "./sayfalar/OduncelerimSayfasi.jsx";
import YonetimSayfasi from "./sayfalar/YonetimSayfasi.jsx";

function Icerik() {
  const toast = useToast();
  const [oturum, setOturum] = useState(oturumuOku());
  const [sayfa, setSayfa] = useState("kitaplar");

  // İstemci 401 alırsa oturum silinir; kullanıcı girişe yönlendirilir
  useEffect(() => {
    const bitti = () => { setOturum(null); toast.hata("Oturum süresi doldu, lütfen tekrar giriş yapın"); };
    window.addEventListener(OTURUM_BITTI_OLAYI, bitti);
    return () => window.removeEventListener(OTURUM_BITTI_OLAYI, bitti);
  }, [toast]);

  if (!oturum) {
    return <GirisSayfasi girildi={(o) => { oturumuKaydet(o); setOturum(o); setSayfa("kitaplar"); toast.basari(`Hoş geldiniz, ${o.ad}`); }} />;
  }

  const yonetici = oturum.rol === "YONETICI";
  // Yönetici paneline yalnızca YONETICI erişir
  const aktif = sayfa === "yonetim" && !yonetici ? "kitaplar" : sayfa;

  return (
    <div className="min-h-screen">
      <UstMenu oturum={oturum} sayfa={aktif} sayfaDegistir={setSayfa}
        cikis={() => { oturumuSil(); setOturum(null); toast.bilgi("Çıkış yapıldı"); }} />
      <main>
        {aktif === "kitaplar" && <KitaplarSayfasi oturum={oturum} />}
        {aktif === "oduncelerim" && <OduncelerimSayfasi />}
        {aktif === "yonetim" && yonetici && <YonetimSayfasi />}
      </main>
    </div>
  );
}

export default function Uygulama() {
  return (
    <ToastSaglayici>
      <Icerik />
    </ToastSaglayici>
  );
}
