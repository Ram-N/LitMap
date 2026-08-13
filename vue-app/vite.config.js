import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue()
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    open: true
  },
  build: {
    // Generate source maps for debugging in production
    sourcemap: false,
    // Reduce chunk size warnings threshold
    chunkSizeWarningLimit: 1000,
    // Optimize bundle
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'leaflet': ['leaflet']
        }
      }
    }
  },
  // Base path for GitHub Pages deployment
  // Use /LitMap/ for GitHub Pages, or '/' for custom domain
  base: process.env.VITE_BASE_PATH || '/'
})
