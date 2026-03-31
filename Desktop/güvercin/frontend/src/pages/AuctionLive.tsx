import { useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Bird, Wifi, WifiOff, Clock, TrendingUp } from "lucide-react";
import { api, type Auction, type Pigeon } from "../api/client";

interface BidEntry {
  bidder: string;
  amount: number;
}

export default function AuctionLive() {
  const { id } = useParams();
  const [auction, setAuction] = useState<Auction | null>(null);
  const [pigeon, setPigeon] = useState<Pigeon | null>(null);
  const [status, setStatus] = useState<"active" | "ended">("active");
  const [remaining, setRemaining] = useState(0);
  const [maxBid, setMaxBid] = useState(0);
  const [minBid, setMinBid] = useState(50);
  const [bidAmount, setBidAmount] = useState(0);
  const [lastBidder, setLastBidder] = useState("");
  const [winner, setWinner] = useState("");
  const [bids, setBids] = useState<BidEntry[]>([]);
  const [error, setError] = useState("");
  const [extended, setExtended] = useState(false);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    api.get<Auction>(`/auctions/${id}`).then((a) => {
      setAuction(a);
      setStatus(a.status);
      if (a.starting_price > 0 && maxBid === 0) {
        setMinBid(a.starting_price);
        setBidAmount(a.starting_price);
      }
      if (a.status === "ended" && a.winner_id) {
        setWinner(`Kullanıcı #${a.winner_id}`);
      }
      api.get<Pigeon>(`/pigeons/${a.pigeon_id}`).then(setPigeon);
    });
  }, [id]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token || !id) return;

    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(
      `${proto}://${location.hostname}:8000/auctions/ws/${id}?token=${token}`
    );
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);

      if (msg.type === "bid_update") {
        setMaxBid(msg.amount);
        setMinBid(msg.amount + 50);
        setBidAmount(msg.amount + 50);
        setRemaining(msg.remaining_seconds);
        setLastBidder(msg.bidder);
        setBids((prev) => [
          { bidder: msg.bidder, amount: msg.amount },
          ...prev,
        ]);
        setExtended(msg.extended);
        if (msg.extended) setTimeout(() => setExtended(false), 3000);
        setError("");
      }

      if (msg.type === "auction_ended") {
        setStatus("ended");
        setWinner(msg.winner);
        setRemaining(0);
      }

      if (msg.type === "error") {
        setError(msg.message);
        setTimeout(() => setError(""), 4000);
      }
    };

    return () => ws.close();
  }, [id]);

  const placeBid = () => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const token = localStorage.getItem("token");
    ws.send(
      JSON.stringify({
        type: "bid",
        auction_id: Number(id),
        amount: bidAmount,
        token,
      })
    );
  };

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  };

  if (!auction) return null;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">İhale #{id}</h1>
        <div
          className={`flex items-center gap-3 rounded-2xl border px-6 py-3 ${
            status === "ended"
              ? "border-danger bg-danger/5"
              : remaining <= 10
                ? "border-warning bg-warning/5"
                : "border-border bg-surface"
          }`}
        >
          <Clock className={`h-5 w-5 ${remaining <= 10 ? "text-warning" : "text-muted"}`} />
          {status === "active" ? (
            <span className={`text-2xl font-mono font-bold tabular-nums ${remaining <= 10 ? "text-warning" : ""}`}>
              {formatTime(remaining)}
            </span>
          ) : (
            <span className="text-lg font-bold text-danger">Sona Erdi</span>
          )}
        </div>
      </div>

      {/* Pigeon Info */}
      {pigeon && (
        <Link
          to={`/ilan/${pigeon.id}`}
          className="mb-6 flex items-center gap-4 rounded-2xl border border-border bg-surface p-4 transition hover:border-primary/30"
        >
          <div
            className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-surface-2 bg-cover bg-center"
            style={pigeon.photo_url ? { backgroundImage: `url(${pigeon.photo_url})` } : {}}
          >
            {!pigeon.photo_url && <Bird className="h-7 w-7 text-border" />}
          </div>
          <div>
            <p className="font-semibold">{pigeon.name}</p>
            <p className="text-sm text-muted">
              {pigeon.breed}
              {pigeon.color && ` · ${pigeon.color}`}
              {pigeon.age && ` · ${pigeon.age} yaş`}
            </p>
          </div>
        </Link>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Bid Panel */}
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="mb-6 text-center">
            <p className="text-sm text-muted">En Yüksek Teklif</p>
            <p className="mt-1 text-4xl font-extrabold text-accent">
              {maxBid.toLocaleString()} ₺
            </p>
            {lastBidder && (
              <p className="mt-1 text-sm text-muted">{lastBidder}</p>
            )}
          </div>

          <AnimatePresence>
            {extended && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="mb-4 rounded-xl bg-warning/10 px-4 py-2 text-center text-sm font-semibold text-warning"
              >
                Süre uzatıldı!
              </motion.div>
            )}
          </AnimatePresence>

          {status === "active" ? (
            <div>
              <label className="mb-2 block text-sm text-muted">
                Teklif Miktarı (₺)
              </label>
              <input
                type="number"
                value={bidAmount}
                onChange={(e) => setBidAmount(Number(e.target.value))}
                min={minBid}
                step={50}
                className="mb-3 w-full rounded-xl border border-border bg-surface-2 px-4 py-3 text-lg font-bold text-text outline-none focus:border-accent"
              />
              <button
                onClick={placeBid}
                disabled={!connected || bidAmount < minBid}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-accent py-3.5 text-lg font-bold text-white transition hover:bg-accent-hover disabled:opacity-40"
              >
                <TrendingUp className="h-5 w-5" /> Teklif Ver
              </button>
            </div>
          ) : (
            <div className="text-center">
              {winner ? (
                <p className="text-lg">
                  Kazanan: <strong className="text-accent">{winner}</strong>
                </p>
              ) : (
                <p className="text-muted">Teklif verilmedi.</p>
              )}
            </div>
          )}

          <AnimatePresence>
            {error && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="mt-3 rounded-lg bg-danger/10 px-3 py-2 text-center text-sm text-danger"
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>
        </div>

        {/* Bid History */}
        <div className="rounded-2xl border border-border bg-surface p-6">
          <h3 className="mb-4 text-lg font-semibold">Teklif Geçmişi</h3>
          <div className="max-h-96 space-y-2 overflow-y-auto">
            {bids.length === 0 ? (
              <p className="py-8 text-center text-muted">Henüz teklif yok.</p>
            ) : (
              bids.map((b, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`flex items-center justify-between rounded-xl px-4 py-3 ${
                    i === 0
                      ? "bg-accent/10 border border-accent/20"
                      : "bg-surface-2"
                  }`}
                >
                  <span className="text-sm text-muted">{b.bidder}</span>
                  <span className="font-bold">
                    {b.amount.toLocaleString()} ₺
                  </span>
                </motion.div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* WS Status */}
      <div className="mt-4 flex justify-end">
        <span
          className={`flex items-center gap-1 text-xs ${
            connected ? "text-accent" : "text-danger"
          }`}
        >
          {connected ? (
            <Wifi className="h-3 w-3" />
          ) : (
            <WifiOff className="h-3 w-3" />
          )}
          {connected ? "Bağlı" : "Bağlantı kesildi"}
        </span>
      </div>
    </div>
  );
}
