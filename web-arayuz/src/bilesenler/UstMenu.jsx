export default function UstMenu({ oturum, sayfa, sayfaDegistir, cikis }) {
  const sekmeler = oturum.rol === "YONETICI"
    ? [["kitaplar", "Kitaplar"], ["yonetim", "Yönetim"]]
    : [["kitaplar", "Kitaplar"], ["oduncelerim", "Ödünçlerim"]];

  return (
    <header className="bg-white/80 backdrop-blur border-b border-slate-200 sticky top-0 z-10">
      <nav className="max-w-5xl mx-auto px-4 py-3 flex flex-wrap items-center gap-2 sm:gap-4">
        <span className="text-lg font-bold text-indigo-700 mr-2 sm:mr-4">📚 Kütüphane</span>
        {sekmeler.map(([anahtar, ad]) => (
          <button
            key={anahtar}
            id={`menu-${anahtar}`}
            onClick={() => sayfaDegistir(anahtar)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
              sayfa === anahtar ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {ad}
          </button>
        ))}
        <span className="ml-auto text-sm text-slate-500 hidden sm:inline">
          {oturum.ad}
          {oturum.rol === "YONETICI" && (
            <span className="ml-2 rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-700">Yönetici</span>
          )}
        </span>
        <button id="menu-cikis" onClick={cikis}
          className="ml-auto sm:ml-0 rounded-lg px-3 py-1.5 text-sm text-rose-600 hover:bg-rose-50 transition">
          Çıkış
        </button>
      </nav>
    </header>
  );
}
