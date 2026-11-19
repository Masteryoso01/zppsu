<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Mail, Lock, LogIn, Loader2 } from '@lucide/vue'
import { useAuthStore } from '../../stores/auth'
import { useDataStore } from '../../stores/data'
import { useUiStore } from '../../stores/ui'
import BaseInput from '../../components/ui/BaseInput.vue'
import BaseButton from '../../components/ui/BaseButton.vue'

const auth = useAuthStore()
const data = useDataStore()
const ui = useUiStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Please enter your email and password.'
    return
  }
  loading.value = true
  try {
    data.reset()
    await auth.login(email.value.trim(), password.value)
    ui.toast(`Welcome back, ${auth.user.name.split(' ')[0]}.`)
    router.push(route.query.redirect || auth.homePath)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="font-headline text-2xl font-semibold text-neutral-900">Sign in to GeoTrack</h2>
    <p class="text-sm text-neutral-500 mt-1.5">Enter your credentials. Your portal is chosen automatically.</p>

    <form class="mt-6 space-y-4" @submit.prevent="submit">
      <BaseInput v-model="email" type="email" label="Email address" placeholder="you@example.com" :icon="Mail" required />
      <BaseInput v-model="password" type="password" label="Password" placeholder="••••••••" :icon="Lock" required />

      <p v-if="error" class="text-sm text-danger-600 -mt-1">{{ error }}</p>

      <div class="flex items-center justify-between text-sm">
        <label class="flex items-center gap-2 text-neutral-600 cursor-pointer">
          <input type="checkbox" class="rounded border-neutral-300 text-primary-600 focus:ring-primary-500" />
          Remember me
        </label>
        <RouterLink to="/forgot-password" class="text-primary-600 font-medium hover:underline">Forgot password?</RouterLink>
      </div>

      <BaseButton type="submit" block :disabled="loading">
        <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
        <LogIn v-else class="w-4 h-4" />
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </BaseButton>
    </form>

    <p class="text-center text-sm text-neutral-500 mt-6">
      New OJT applicant?
      <RouterLink to="/register" class="text-primary-600 font-medium hover:underline">Create an account</RouterLink>
    </p>

  </div>
</template>
