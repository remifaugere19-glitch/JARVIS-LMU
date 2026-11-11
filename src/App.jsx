import { useState } from "react";
import TracksPage from "./pages/TracksPage.jsx";
import CarsPage from "./pages/CarsPage.jsx";
import BrakingMarkersPage from "./pages/BrakingMarkersPage.jsx";

const PAGES = [
  { id: "markers", label: "Repères de freinage", Component: BrakingMarkersPage },
  { id: "tracks", label: "Circuits", Component: TracksPage },
  { id: "cars", label: "Voitures", Component: CarsPage },
];

export default function App() {
  const [pageId, setPageId] = useState("markers");
  const current = PAGES.find((page) => page.id === pageId);
  const Page = current.Component;

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">JARVIS-LMU</div>
        <nav className="app-nav" aria-label="Navigation principale">
          {PAGES.map((page) => (
            <button
              key={page.id}
              type="button"
              className={page.id === pageId ? "nav-button active" : "nav-button"}
              onClick={() => setPageId(page.id)}
            >
              {page.label}
            </button>
          ))}
        </nav>
      </header>
      <main className="app-main">
        <Page />
      </main>
    </div>
  );
}
