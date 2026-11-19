<script setup>
import { computed, onMounted } from 'vue'
import { Loader2, AlertCircle } from '@lucide/vue'
import Sidebar from '../components/layout/Sidebar.vue'
import Topbar from '../components/layout/Topbar.vue'
import { useAuthStore } from '../stores/auth'
import { useDataStore } from '../stores/data'
import { internNav, adminNav, superAdminNav } from '../lib/nav'

const auth = useAuthStore()
const data = useDataStore()

onMounted(() => data.load())

const navItems = computed(() => {
  if (auth.role === 'admin') return adminNav
  if (auth.role === 'super-admin') return superAdminNav
  return internNav
})
</script>

<template>
  <div class="min-h-screen flex bg-neutral-50">
    <Sidebar :items="navItems" :role="auth.role" :org-name="auth.user?.orgName" />
    <div class="flex-1 flex flex-col min-w-0">
      <Topbar />
      <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1600px] w-full mx-auto">
        <div v-if="!data.loaded && !data.loadError" class="flex items-center justify-center gap-2 py-24 text-sm text-neutral-500">
          <Loader2 class="w-4 h-4 animate-spin" /> Loading your data…
        </div>
        <div v-else-if="data.loadError" class="max-w-md mx-auto text-center py-20">
          <AlertCircle class="w-10 h-10 text-danger-500 mx-auto mb-3" />
          <p class="font-medium text-neutral-800">Couldn't load your data</p>
          <p class="text-sm text-neutral-500 mt-1">{{ data.loadError }}</p>
          <button class="mt-4 px-4 py-2 rounded-lg bg-primary-600 text-white text-sm font-medium cursor-pointer" @click="data.load()">Try again</button>
        </div>
        <RouterView v-else />
      </main>
    </div>
  </div>
</template>
