<script setup>
import { ref } from 'vue'
import { Mail, Send, Loader2, CheckCircle2, ArrowLeft } from '@lucide/vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import BaseButton from '../../components/ui/BaseButton.vue'

const email = ref('')
const loading = ref(false)
const sent = ref(false)

function submit() {
  if (!email.value) return
  loading.value = true
  setTimeout(() => {
    loading.value = false
    sent.value = true
  }, 600)
}
</script>

<template>
  <div>
    <template v-if="!sent">
      <h2 class="font-headline text-2xl font-semibold text-neutral-900">Reset your password</h2>
      <p class="text-sm text-neutral-500 mt-1.5">Enter your email and we'll send you a reset link.</p>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <BaseInput v-model="email" type="email" label="Email address" placeholder="you@example.com" :icon="Mail" required />
        <BaseButton type="submit" block :disabled="loading">
          <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
          <Send v-else class="w-4 h-4" />
          {{ loading ? 'Sending…' : 'Send reset link' }}
        </BaseButton>
      </form>
    </template>

    <template v-else>
      <div class="w-12 h-12 rounded-full bg-success-50 flex items-center justify-center mb-4">
        <CheckCircle2 class="w-6 h-6 text-success-600" />
      </div>
      <h2 class="font-headline text-2xl font-semibold text-neutral-900">Check your email</h2>
      <p class="text-sm text-neutral-500 mt-1.5">We've sent a password reset link to <span class="font-medium text-neutral-700">{{ email }}</span>.</p>
    </template>

    <RouterLink to="/login" class="inline-flex items-center gap-1.5 text-sm text-primary-600 font-medium hover:underline mt-6">
      <ArrowLeft class="w-4 h-4" /> Back to sign in
    </RouterLink>
  </div>
</template>
