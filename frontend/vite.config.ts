import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 3000,
    },
    watch: {
      usePolling: true,
    },
    // Desabilitar cache HTTP durante desenvolvimento
    headers: {
      'Cache-Control': 'no-store',
      'Pragma': 'no-cache',
    }
  },
  build: {
    rollupOptions: {
      output: {
        // Hash nos arquivos para invalidar cache em produção
        entryFileNames: `assets/[name]-[hash].js`,
        chunkFileNames: `assets/[name]-[hash].js`,
        assetFileNames: `assets/[name]-[hash].[ext]`
      }
    }
  }
})
