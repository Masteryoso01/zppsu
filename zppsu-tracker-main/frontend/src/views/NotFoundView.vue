<script setup>
import { useRouter } from 'vue-router'
import { MapPinOff, ArrowLeft } from '@lucide/vue'
import { useAuthStore } from '../stores/auth'
import BaseButton from '../components/ui/BaseButton.vue'

const router = useRouter()
const auth = useAuthStore()

function goHome() {
  router.push(auth.isAuthenticated ? auth.homePath : '/login')
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-neutral-50 px-4 text-center">
    <div class="w-16 h-16 rounded-2xl bg-primary-50 flex items-center justify-center mb-4">
      <MapPinOff class="w-8 h-8 text-primary-600" />
    </div>
    <h1 class="font-headline text-3xl font-semibold text-neutral-900">404 — Off the map</h1>
    <p class="text-neutral-500 mt-2 max-w-sm">This page doesn't exist or you don't have access to it.</p>
    <BaseButton class="mt-6" @click="goHome">
      <ArrowLeft class="w-4 h-4" /> Back to safety
    </BaseButton>
  </div>
</template>
