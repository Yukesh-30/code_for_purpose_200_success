import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      '/auth':      { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/business':  { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/upload':    { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/chat':      { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/forecast':  { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/anomaly':   { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/alerts':    { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/bank':      { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/stats':     { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
      '/health':    { target: 'http://127.0.0.1:5000', changeOrigin: true, secure: false },
    },
  },
})
