import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    proxy: {
      "/auth": "http://localhost:8000",
      "/pigeons": "http://localhost:8000",
      "/auctions": "http://localhost:8000",
      "/payments": "http://localhost:8000",
    },
  },
});
