import { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";

const ToastBaglami = createContext(null);

const STILLER = {
  basari: "bg-emerald-600 text-white",
  hata: "bg-rose-600 text-white",
  bilgi: "bg-slate-800 text-white",
};
const SIMGELER = { basari: "✓", hata: "!", bilgi: "i" };

export function ToastSaglayici({ children }) {
  const [liste, setListe] = useState([]);
  const sayac = useRef(0);

  const kapat = useCallback((id) => setListe((l) => l.filter((t) => t.id !== id)), []);

  const goster = useCallback((tur, mesaj) => {
    const id = ++sayac.current;
    setListe((l) => [...l, { id, tur, mesaj }]);
    setTimeout(() => kapat(id), 4000);
  }, [kapat]);

  const api = useMemo(() => ({
    basari: (m) => goster("basari", m),
    hata: (m) => goster("hata", m),
    bilgi: (m) => goster("bilgi", m),
  }), [goster]);

  return (
    <ToastBaglami.Provider value={api}>
      {children}
      <div aria-live="polite" className="fixed top-4 right-4 left-4 sm:left-auto z-50 flex flex-col gap-2 sm:w-96">
        {liste.map((t) => (
          <div key={t.id} role="status" onClick={() => kapat(t.id)}
            className={`toast-giris flex items-start gap-3 rounded-xl px-4 py-3 shadow-lg cursor-pointer ${STILLER[t.tur]}`}>
            <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/25 text-xs font-bold">
              {SIMGELER[t.tur]}
            </span>
            <span className="text-sm font-medium">{t.mesaj}</span>
          </div>
        ))}
      </div>
    </ToastBaglami.Provider>
  );
}

export const useToast = () => useContext(ToastBaglami);
