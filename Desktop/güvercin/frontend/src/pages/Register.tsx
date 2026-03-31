import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bird } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [roles, setRoles] = useState<string[]>(["buyer"]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const toggleRole = (role: string) => {
    setRoles((prev) =>
      prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (roles.length === 0) {
      setError("En az bir rol seçin.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await register(username, email, password, roles);
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
          <h2 className="text-2xl font-bold">Kayıt Ol</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm text-muted">Kullanıcı Adı</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none transition focus:border-primary" />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted">E-posta</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none transition focus:border-primary" />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted">Şifre</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none transition focus:border-primary" />
          </div>
          <div>
            <label className="mb-2 block text-sm text-muted">Rol</label>
            <div className="flex gap-4">
              {[
                { key: "buyer", label: "Alıcı" },
                { key: "seller", label: "Satıcı" },
              ].map((r) => (
                <label
                  key={r.key}
                  className={`flex cursor-pointer items-center gap-2 rounded-xl border px-4 py-2.5 text-sm transition ${
                    roles.includes(r.key)
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-muted hover:border-primary/50"
                  }`}
                >
                  <input type="checkbox" checked={roles.includes(r.key)} onChange={() => toggleRole(r.key)} className="hidden" />
                  {r.label}
                </label>
              ))}
            </div>
          </div>

          {error && <p className="rounded-lg bg-danger/10 px-3 py-2 text-center text-sm text-danger">{error}</p>}

          <button type="submit" disabled={loading} className="w-full rounded-xl bg-primary py-3 font-semibold text-white transition hover:bg-primary-hover disabled:opacity-50">
            {loading ? "Yükleniyor..." : "Kayıt Ol"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          Zaten hesabın var mı?{" "}
          <Link to="/giris" className="text-primary hover:text-primary-hover">Giriş yap</Link>
        </p>
      </div>
    </div>
  );
}
