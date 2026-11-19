import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', {
  state: () => ({
    toasts: [],
    sidebarOpen: false,
  }),
  actions: {
    toast(message, tone = 'success') {
      const id = Date.now() + Math.random()
      this.toasts.push({ id, message, tone })
      setTimeout(() => this.dismiss(id), 3800)
    },
    dismiss(id) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },
  },
})
