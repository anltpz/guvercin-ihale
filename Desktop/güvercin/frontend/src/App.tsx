import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Pigeons from "./pages/Pigeons";
import PigeonDetail from "./pages/PigeonDetail";
import PigeonForm from "./pages/PigeonForm";
import Auctions from "./pages/Auctions";
import AuctionLive from "./pages/AuctionLive";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="flex min-h-screen flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/giris" element={<Login />} />
              <Route path="/kayit" element={<Register />} />
              <Route path="/ilanlar" element={<Pigeons />} />
              <Route path="/ilan/:id" element={<PigeonDetail />} />
              <Route path="/ilan-ekle" element={<PigeonForm />} />
              <Route path="/ilan-duzenle/:id" element={<PigeonForm />} />
              <Route path="/ihaleler" element={<Auctions />} />
              <Route path="/ihale/:id" element={<AuctionLive />} />
            </Routes>
          </main>
          <footer className="border-t border-border py-6 text-center text-sm text-muted">
            GüvercinIhale &copy; 2026 — Güvercin severler için online ihale
            platformu
          </footer>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
