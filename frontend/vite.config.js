import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Tailwind v4 ships as a Vite plugin: no tailwind.config.js or postcss config needed.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173 },
});
