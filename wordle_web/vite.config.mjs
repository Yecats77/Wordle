import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  build: {
    minify: "terser",
    terserOptions: {
      compress: {
        // drop_console: true,
        drop_debugger: true,
      },
    },
    outDir: "dist",
  },
  server: {
    host: "localhost",
    port: 7368,
    proxy: {
      "/api": {
        target: "http://localhost:7364",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
    open: false,
  },
});
