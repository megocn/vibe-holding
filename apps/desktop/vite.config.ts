import path from 'node:path';
import { fileURLToPath } from 'node:url';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { vhFetchProxy } from './vite-plugin-vh-fetch.ts';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

export default defineConfig({
  plugins: [react(), tailwindcss(), vhFetchProxy()],
  clearScreen: false,
  server: {
    // 与 Orbitra(5173) / arena(5177) 错开；strictPort 避免 Vite 偷偷换端口而 Tauri 仍开旧地址导致白屏卡住
    port: 5280,
    strictPort: true,
    fs: { allow: [root] },
  },
});
