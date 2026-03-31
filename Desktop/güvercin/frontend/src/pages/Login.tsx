import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bird } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(username, password);
      navigate("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-border bg-surface p-8">
        <div className="mb-6 flex flex-col items-center">
          <Bird className="mb-2 h-10 w-10 text-primary" />
          <h2 className="text-2xl font-bold">Giriş Yap</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm text-muted">
              Kullanıcı Adı
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none transition focus:border-primary"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted">Şifre</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none transition focus:border-primary"
            />
          </div>

          {error && (
            <p className="rounded-lg bg-danger/10 px-3 py-2 text-center text-sm text-danger">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-primary py-3 font-semibold text-white transition hover:bg-primary-hover disabled:opacity-50"
          >
            {loading ? "Yükleniyor..." : "Giriş Yap"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Hesabın yok mu?{" "}
          <Link to="/kayit" className="text-primary hover:text-primary-hover">
            Kayıt ol
          </Link>
        </p>
      </div>
    </div>
  );
}
