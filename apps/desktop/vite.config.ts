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
    fs: { allow: [root] },
  },
});
