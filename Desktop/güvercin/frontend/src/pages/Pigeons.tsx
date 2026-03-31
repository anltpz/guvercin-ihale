import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Bird, ChevronLeft, ChevronRight } from "lucide-react";
import { api, type Pigeon } from "../api/client";

export default function Pigeons() {
  const [pigeons, setPigeons] = useState<Pigeon[]>([]);
  const [skip, setSkip] = useState(0);
  const limit = 12;

  useEffect(() => {
    api.get<Pigeon[]>(`/pigeons/?skip=${skip}&limit=${limit}`).then(setPigeons);
  }, [skip]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="mb-8 text-3xl font-bold">Güvercin İlanları</h1>

      {pigeons.length === 0 ? (
        <div className="flex flex-col items-center py-20 text-muted">
          <Bird className="mb-4 h-16 w-16 opacity-20" />
          <p>Henüz ilan yok.</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {pigeons.map((p, i) => (
            <motion.div
              key={p.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link
                to={`/ilan/${p.id}`}
                className="group block overflow-hidden rounded-2xl border border-border bg-surface transition hover:border-primary/40 hover:-translate-y-1"
              >
                <div
                  className="flex h-44 items-center justify-center bg-surface-2 bg-cover bg-center text-5xl"
                  style={
                    p.photo_url
                      ? { backgroundImage: `url(${p.photo_url})` }
                      : {}
                  }
                >
                  {!p.photo_url && (
                    <Bird className="h-12 w-12 text-border" />
                  )}
                </div>
                <div className="p-5">
                  <h3 className="mb-1 text-lg font-semibold group-hover:text-primary transition">
                    {p.name}
                  </h3>
                  <span className="inline-block rounded-full bg-surface-2 px-3 py-0.5 text-xs text-muted">
                    {p.breed}
                  </span>
                  <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted">
                    {p.age && (
                      <span className="rounded-md bg-surface-2 px-2 py-0.5">
                        {p.age} yaş
                      </span>
                    )}
                    {p.gender && (
                      <span className="rounded-md bg-surface-2 px-2 py-0.5">
                        {p.gender}
                      </span>
                    )}
                    {p.color && (
                      <span className="rounded-md bg-surface-2 px-2 py-0.5">
                        {p.color}
                      </span>
                    )}
                    {p.weight_kg && (
                      <span className="rounded-md bg-surface-2 px-2 py-0.5">
                        {p.weight_kg} kg
                      </span>
                    )}
                  </div>
                  <p className="mt-3 line-clamp-2 text-sm text-muted">
                    {p.description || "Açıklama yok."}
                  </p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}

      {pigeons.length >= limit && (
        <div className="mt-8 flex justify-center gap-3">
          <button
            onClick={() => setSkip(Math.max(0, skip - limit))}
            disabled={skip === 0}
            className="flex items-center gap-1 rounded-lg border border-border px-4 py-2 text-sm transition hover:border-primary disabled:opacity-30"
          >
            <ChevronLeft className="h-4 w-4" /> Önceki
          </button>
          <button
            onClick={() => setSkip(skip + limit)}
            className="flex items-center gap-1 rounded-lg border border-border px-4 py-2 text-sm transition hover:border-primary"
          >
            Sonraki <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
