import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Timer, Shield, Banknote, ArrowRight } from "lucide-react";
import { api, type Auction } from "../api/client";

const features = [
  {
    icon: Timer,
    title: "Canlı Sayaç",
    desc: "Son saniyelerde gelen teklif süreyi uzatır. Her teklif eşit şansta.",
  },
  {
    icon: Shield,
    title: "Güvenli Sistem",
    desc: "JWT kimlik doğrulama, anlık WebSocket bildirimleri.",
  },
  {
    icon: Banknote,
    title: "Kolay Ödeme",
    desc: "İhale bitince kazanana otomatik ödeme linki gönderilir.",
  },
];

export default function Home() {
  const [auctions, setAuctions] = useState<Auction[]>([]);

  useEffect(() => {
    api.get<Auction[]>("/auctions/?limit=6").then(setAuctions).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-4">
      {/* Hero */}
      <section className="py-24 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl font-extrabold leading-tight tracking-tight md:text-6xl"
        >
          Güvercin Satışında
          <span className="block bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Yeni Dönem
          </span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mx-auto mt-6 max-w-xl text-lg text-muted"
        >
          Sayaçlı canlı ihale sistemi ile güvenli alım-satım. Teklif ver, kazan.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-8 flex justify-center gap-4"
        >
          <Link
            to="/ihaleler"
            className="flex items-center gap-2 rounded-xl bg-primary px-6 py-3 font-semibold text-white shadow-lg shadow-primary/25 transition hover:bg-primary-hover"
          >
            Aktif İhaleleri Gör <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            to="/kayit"
            className="rounded-xl border border-border px-6 py-3 font-semibold text-text transition hover:border-primary hover:text-primary"
          >
            Hemen Başla
          </Link>
        </motion.div>
      </section>

      {/* Features */}
      <section className="grid gap-6 pb-16 md:grid-cols-3">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i + 0.3 }}
            className="rounded-2xl border border-border bg-surface p-8 text-center transition hover:border-primary/30"
          >
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <f.icon className="h-7 w-7" />
            </div>
            <h3 className="mb-2 text-lg font-semibold">{f.title}</h3>
            <p className="text-sm text-muted">{f.desc}</p>
          </motion.div>
        ))}
      </section>

      {/* Active Auctions */}
      {auctions.length > 0 && (
        <section className="pb-20">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-bold">Aktif İhaleler</h2>
            <Link
              to="/ihaleler"
              className="text-sm text-primary transition hover:text-primary-hover"
            >
              Tümünü gör →
            </Link>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {auctions.map((a) => (
              <Link
                key={a.id}
                to={`/ihale/${a.id}`}
                className="group rounded-2xl border border-border bg-surface p-6 transition hover:border-accent/50 hover:-translate-y-1"
              >
                <span className="inline-block rounded-full bg-accent/10 px-3 py-1 text-xs font-bold uppercase text-accent">
                  Aktif
                </span>
                <div className="mt-4">
                  <p className="text-xl font-bold">İhale #{a.id}</p>
                  <p className="text-sm text-muted">
                    Güvercin #{a.pigeon_id}
                  </p>
                  <p className="mt-2 text-sm text-muted">
                    Başlangıç: {a.starting_price} ₺
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
