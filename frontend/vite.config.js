import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react(), tailwindcss(),],
  server: {
    proxy: {
      '/banca': 'http://localhost:8000',
      '/admin/bancas': 'http://localhost:8000',
    },
  },
})
