import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // Default Vite port
    proxy: {
      // Proxy API requests to backend
      '/api': {
        target: 'http://localhost:8000', // Your backend server address
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // Uncomment if backend doesn't expect /api prefix
      },
      // Proxy audio file requests
      '/audio': {
        target: 'http://localhost:8000', // Your backend server address for audio files
        changeOrigin: true,
      }
    }
  }
})
