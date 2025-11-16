import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // Treat gmp-* tags as custom elements (Google Maps Web Components)
          isCustomElement: (tag) => tag.startsWith('gmp-')
        }
      }
    })
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
          // Separate vendor chunks for better caching
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'firebase': ['firebase/app', 'firebase/firestore'],
          'maps': ['@googlemaps/markerclusterer']
        }
      }
    }
  },
  // Base path for GitHub Pages deployment
  // Use /LitMap/ for GitHub Pages, or '/' for custom domain
  base: process.env.VITE_BASE_PATH || '/'
})
