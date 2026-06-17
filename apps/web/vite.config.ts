import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Build to apps/web/dist/, served by the local Python server (apps/control-panel/server.py).
// In dev, `npm run dev` proxies /api to the running Python server on 127.0.0.1:8765.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: { outDir: "dist", emptyOutDir: true },
  server: {
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:8765" },
  },
});
