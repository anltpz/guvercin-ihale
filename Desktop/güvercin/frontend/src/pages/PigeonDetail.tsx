import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Bird, Gavel, Pencil, Trash2, X } from "lucide-react";
import { api, type Pigeon, type Auction } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function PigeonDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [pigeon, setPigeon] = useState<Pigeon | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [duration, setDuration] = useState(300);
  const [startingPrice, setStartingPrice] = useState(0);
  const [error, setError] = useState("");
  const [auctionLoading, setAuctionLoading] = useState(false);

  useEffect(() => {
    api.get<Pigeon>(`/pigeons/${id}`).then(setPigeon).catch(() => navigate("/ilanlar"));
  }, [id]);

  const startAuction = async () => {
    setAuctionLoading(true);
    setError("");
    try {
      const auction = await api.post<Auction>("/auctions/", {
        pigeon_id: Number(id),
        duration_seconds: duration,
        starting_price: startingPrice,
      });
      navigate(`/ihale/${auction.id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAuctionLoading(false);
    }
  };

  const deletePigeon = async () => {
    if (!confirm("Bu ilanı silmek istediğinize emin misiniz?")) return;
    try {
      await api.del(`/pigeons/${id}`);
      navigate("/ilanlar");
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (!pigeon) return null;

  const isOwner = user?.id === pigeon.seller_id && user?.roles.includes("seller");

  const specs = [
    pigeon.age && `${pigeon.age} yaş`,
    pigeon.gender,
    pigeon.color,
    pigeon.weight_kg && `${pigeon.weight_kg} kg`,
  ].filter(Boolean);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="grid gap-8 md:grid-cols-2">
        {/* Image */}
        <div
          className="flex h-80 items-center justify-center rounded-2xl border border-border bg-surface-2 bg-cover bg-center md:h-[420px]"
          style={pigeon.photo_url ? { backgroundImage: `url(${pigeon.photo_url})` } : {}}
        >
          {!pigeon.photo_url && <Bird className="h-20 w-20 text-border" />}
        </div>

        {/* Info */}
        <div>
          <h1 className="text-3xl font-bold">{pigeon.name}</h1>
          <span className="mt-2 inline-block rounded-full bg-primary/10 px-4 py-1 text-sm font-medium text-primary">
            {pigeon.breed}
          </span>

          {specs.length > 0 && (
            <div className="mt-5 flex flex-wrap gap-2">
              {specs.map((s) => (
                <span key={s} className="rounded-lg bg-surface-2 px-3 py-1.5 text-sm text-muted">
                  {s}
                </span>
              ))}
            </div>
          )}

          <p className="mt-6 leading-relaxed text-muted">
            {pigeon.description || "Açıklama eklenmemiş."}
          </p>

          {isOwner && (
            <div className="mt-8 flex gap-3">
              <button
                onClick={() => setShowModal(true)}
                className="flex items-center gap-2 rounded-xl bg-accent px-5 py-3 font-semibold text-white transition hover:bg-accent-hover"
              >
                <Gavel className="h-4 w-4" /> İhale Başlat
              </button>
              <Link
                to={`/ilan-duzenle/${pigeon.id}`}
                className="flex items-center gap-2 rounded-xl border border-border px-4 py-3 text-sm transition hover:border-primary hover:text-primary"
              >
                <Pencil className="h-4 w-4" /> Düzenle
              </Link>
              <button
                onClick={deletePigeon}
                className="flex items-center gap-2 rounded-xl border border-border px-4 py-3 text-sm text-danger transition hover:border-danger hover:bg-danger/10"
              >
                <Trash2 className="h-4 w-4" /> Sil
              </button>
            </div>
          )}

          {error && <p className="mt-4 rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>}
        </div>
      </div>

      {/* Auction Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowModal(false)}>
          <div className="w-full max-w-md rounded-2xl border border-border bg-surface p-8" onClick={(e) => e.stopPropagation()}>
            <div className="mb-6 flex items-center justify-between">
              <h3 className="text-xl font-bold">İhale Başlat</h3>
              <button onClick={() => setShowModal(false)} className="text-muted hover:text-text"><X className="h-5 w-5" /></button>
            </div>
            <p className="mb-6 text-sm text-muted">{pigeon.name} için ihale ayarları</p>

            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm text-muted">Süre</label>
                <select value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary">
                  <option value={120}>2 dakika</option>
                  <option value={300}>5 dakika</option>
                  <option value={600}>10 dakika</option>
                  <option value={1800}>30 dakika</option>
                  <option value={3600}>1 saat</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm text-muted">Başlangıç Fiyatı (₺)</label>
                <input type="number" value={startingPrice} onChange={(e) => setStartingPrice(Number(e.target.value))} min={0} step={50} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary" />
              </div>
            </div>

            {error && <p className="mt-3 text-center text-sm text-danger">{error}</p>}

            <div className="mt-6 flex gap-3">
              <button onClick={startAuction} disabled={auctionLoading} className="flex-1 rounded-xl bg-accent py-3 font-semibold text-white transition hover:bg-accent-hover disabled:opacity-50">
                {auctionLoading ? "Başlatılıyor..." : "Başlat"}
              </button>
              <button onClick={() => setShowModal(false)} className="rounded-xl border border-border px-6 py-3 transition hover:border-primary">
                İptal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
