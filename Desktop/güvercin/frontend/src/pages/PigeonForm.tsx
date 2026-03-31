import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, type Pigeon } from "../api/client";

export default function PigeonForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [breed, setBreed] = useState("");
  const [age, setAge] = useState<number | "">("");
  const [gender, setGender] = useState("");
  const [color, setColor] = useState("");
  const [weightKg, setWeightKg] = useState<number | "">("");
  const [photoUrl, setPhotoUrl] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isEdit) {
      api.get<Pigeon>(`/pigeons/${id}`).then((p) => {
        setName(p.name);
        setBreed(p.breed);
        setAge(p.age ?? "");
        setGender(p.gender ?? "");
        setColor(p.color ?? "");
        setWeightKg(p.weight_kg ?? "");
        setPhotoUrl(p.photo_url ?? "");
        setDescription(p.description ?? "");
      });
    }
  }, [id, isEdit]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const body = {
      name,
      breed,
      age: age || null,
      gender: gender || null,
      color: color || null,
      weight_kg: weightKg || null,
      photo_url: photoUrl || null,
      description: description || null,
    };
    try {
      if (isEdit) {
        await api.put(`/pigeons/${id}`, body);
        navigate(`/ilan/${id}`);
      } else {
        const p = await api.post<Pigeon>("/pigeons/", body);
        navigate(`/ilan/${p.id}`);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4 py-10">
      <div className="w-full max-w-lg rounded-2xl border border-border bg-surface p-8">
        <h2 className="mb-6 text-center text-2xl font-bold">
          {isEdit ? "İlan Düzenle" : "Güvercin İlanı Ekle"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 sm:col-span-1">
              <label className="mb-1 block text-sm text-muted">İsim *</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} required minLength={2} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary" />
            </div>
            <div className="col-span-2 sm:col-span-1">
              <label className="mb-1 block text-sm text-muted">Cins *</label>
              <input type="text" value={breed} onChange={(e) => setBreed(e.target.value)} required minLength={2} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm text-muted">Yaş</label>
              <input type="number" value={age} onChange={(e) => setAge(e.target.value ? Number(e.target.value) : "")} min={0} max={30} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm text-muted">Cinsiyet</label>
              <select value={gender} onChange={(e) => setGender(e.target.value)} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary">
                <option value="">Seçiniz</option>
                <option value="erkek">Erkek</option>
                <option value="disi">Dişi</option>
                <option value="bilinmiyor">Bilinmiyor</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm text-muted">Renk</label>
              <input type="text" value={color} onChange={(e) => setColor(e.target.value)} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary" />
            </div>
            <div>
              <label className="mb-1 block text-sm text-muted">Ağırlık (kg)</label>
              <input type="number" value={weightKg} onChange={(e) => setWeightKg(e.target.value ? Number(e.target.value) : "")} min={0} max={5} step={0.01} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary" />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm text-muted">Fotoğraf URL</label>
            <input type="url" value={photoUrl} onChange={(e) => setPhotoUrl(e.target.value)} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary" />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted">Açıklama</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} className="w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-text outline-none focus:border-primary" />
          </div>

          {error && <p className="rounded-lg bg-danger/10 px-3 py-2 text-center text-sm text-danger">{error}</p>}

          <button type="submit" disabled={loading} className="w-full rounded-xl bg-primary py-3 font-semibold text-white transition hover:bg-primary-hover disabled:opacity-50">
            {loading ? "Yükleniyor..." : isEdit ? "Kaydet" : "İlan Ekle"}
          </button>
        </form>
      </div>
    </div>
  );
}
