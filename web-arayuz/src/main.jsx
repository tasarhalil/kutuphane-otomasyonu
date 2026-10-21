import React from "react";
import { createRoot } from "react-dom/client";
import Uygulama from "./Uygulama.jsx";
import "./index.css";

// Uygulamayı kök elemana bağla
createRoot(document.getElementById("kok")).render(
  <React.StrictMode>
    <Uygulama />
  </React.StrictMode>
);
