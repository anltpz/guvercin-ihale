import { Link, useNavigate } from "react-router-dom";
import { Bird, LogOut, Plus, Gavel } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-surface/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link
          to="/"
          className="flex items-center gap-2 text-lg font-bold text-text transition hover:text-primary"
        >
          <Bird className="h-6 w-6 text-primary" />
          GüvercinIhale
        </Link>

        <div className="flex items-center gap-1">
          <Link
            to="/ilanlar"
            className="rounded-lg px-3 py-2 text-sm text-muted transition hover:bg-surface-2 hover:text-text"
          >
            İlanlar
          </Link>
          <Link
            to="/ihaleler"
            className="rounded-lg px-3 py-2 text-sm text-muted transition hover:bg-surface-2 hover:text-text"
          >
            <span className="flex items-center gap-1">
              <Gavel className="h-4 w-4" /> İhaleler
            </span>
          </Link>

          {user ? (
            <div className="ml-2 flex items-center gap-2">
              {user.roles.includes("seller") && (
                <Link
                  to="/ilan-ekle"
                  className="flex items-center gap-1 rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-white transition hover:bg-primary-hover"
                >
                  <Plus className="h-4 w-4" /> İlan Ekle
                </Link>
              )}
              <div className="flex items-center gap-2 rounded-lg bg-surface-2 px-3 py-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-xs font-bold text-white">
                  {user.username[0].toUpperCase()}
                </div>
                <span className="text-sm font-medium">{user.username}</span>
              </div>
              <button
                onClick={() => {
                  logout();
                  navigate("/");
                }}
                className="rounded-lg p-2 text-muted transition hover:bg-surface-2 hover:text-danger"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="ml-2 flex items-center gap-2">
              <Link
                to="/giris"
                className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-hover"
              >
                Giriş
              </Link>
              <Link
                to="/kayit"
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text transition hover:border-primary hover:text-primary"
              >
                Kayıt
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
