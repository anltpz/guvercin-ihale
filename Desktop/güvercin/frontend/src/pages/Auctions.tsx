import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Gavel } from "lucide-react";
import { api, type Auction } from "../api/client";

export default function Auctions() {
  const [auctions, setAuctions] = useState<Auction[]>([]);

  useEffect(() => {
    api.get<Auction[]>("/auctions/?limit=50").then(setAuctions);
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="mb-8 text-3xl font-bold">Aktif İhaleler</h1>

      {auctions.length === 0 ? (
        <div className="flex flex-col items-center py-20 text-muted">
          <Gavel className="mb-4 h-16 w-16 opacity-20" />
          <p>Henüz aktif ihale yok.</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {auctions.map((a, i) => (
            <motion.div
              key={a.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link
                to={`/ihale/${a.id}`}
                className="group block rounded-2xl border border-border bg-surface p-6 transition hover:border-accent/50 hover:-translate-y-1"
              >
                <div className="mb-4 flex items-center justify-between">
                  <span className="inline-block rounded-full bg-accent/10 px-3 py-1 text-xs font-bold uppercase text-accent">
                    Aktif
                  </span>
                  <span className="text-xs text-muted">
                    {Math.floor(a.duration_seconds / 60)} dk
                  </span>
                </div>
                <p className="text-2xl font-bold group-hover:text-accent transition">
                  İhale #{a.id}
                </p>
                <p className="mt-1 text-sm text-muted">
                  Güvercin #{a.pigeon_id}
                </p>
                <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
                  <span className="text-xs text-muted">Başlangıç</span>
                  <span className="text-lg font-bold text-accent">
                    {a.starting_price} ₺
                  </span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
