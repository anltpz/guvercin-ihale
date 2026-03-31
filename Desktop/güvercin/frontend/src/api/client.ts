const BASE = "";

async function request<T>(
  path: string,
  opts: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opts.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Bir hata oluştu." }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  del: (path: string) => request(path, { method: "DELETE" }),
};

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  roles: string[];
}

export interface Pigeon {
  id: number;
  seller_id: number;
  name: string;
  breed: string;
  age: number | null;
  gender: string | null;
  color: string | null;
  weight_kg: number | null;
  photo_url: string | null;
  description: string | null;
}

export interface Auction {
  id: number;
  pigeon_id: number;
  seller_id: number;
  status: "active" | "ended";
  duration_seconds: number;
  starting_price: number;
  winner_id: number | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
