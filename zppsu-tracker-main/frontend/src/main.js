import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { setUnauthorizedHandler } from './lib/api'
import { useAuthStore } from './stores/auth'
import { useDataStore } from './stores/data'

const app = createApp(App)
app.use(createPinia())
app.use(router)

setUnauthorizedHandler(() => {
  const auth = useAuthStore()
  if (!auth.user) return
  auth.logout()
  useDataStore().reset()
  router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
})
app.mount('#app')
