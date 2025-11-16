import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import './styles/design-tokens.css'

const app = createApp(App)
const pinia = createPinia()

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  console.error('Error info:', info)
  console.error('Component:', instance)

  // In production, you might want to send errors to a tracking service
  // Example: Sentry.captureException(err)
}

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', event => {
  console.error('Unhandled promise rejection:', event.reason)
  event.preventDefault()
})

app.use(pinia)
app.use(router)
app.mount('#app')
