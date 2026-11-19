<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Mail, Lock, User, IdCard, Phone, School, UserPlus, Loader2, ArrowLeft, ArrowRight, Check, Fingerprint, ScanFace, ShieldCheck } from '@lucide/vue'
import { useUiStore } from '../../stores/ui'
import { api } from '../../lib/api'
import { biometricLabel, isBiometricSupported, moveCredential, registerBiometric } from '../../lib/biometric'
import BaseInput from '../../components/ui/BaseInput.vue'
import BaseSelect from '../../components/ui/BaseSelect.vue'
import BaseButton from '../../components/ui/BaseButton.vue'

const router = useRouter()
const ui = useUiStore()

const bioLabel = biometricLabel()
const isIos = bioLabel === 'Face ID'
const bioSupported = ref(true)
const bioRegistered = ref(false)
const bioBusy = ref(false)
onMounted(async () => { bioSupported.value = await isBiometricSupported() })

const form = reactive({
  fullName: '', studentId: '', email: '', contact: '',
  school: '', course: '', yearLevel: '',
  password: '', confirmPassword: '',
})
const loading = ref(false)
const error = ref('')

const yearLevels = [
  { label: '1st Year', value: '1st Year' },
  { label: '2nd Year', value: '2nd Year' },
  { label: '3rd Year', value: '3rd Year' },
  { label: '4th Year', value: '4th Year' },
]

const steps = [
  { title: 'Personal', fields: ['fullName', 'studentId', 'contact'] },
  { title: 'Academic', fields: ['school', 'course', 'yearLevel'] },
  { title: 'Account', fields: ['email', 'password', 'confirmPassword'] },
  { title: 'Biometric', fields: [] },
]
const step = ref(0)
const isLast = computed(() => step.value === steps.length - 1)

function stepValid() {
  if (steps[step.value].fields.some((f) => !form[f])) {
    error.value = 'Please fill in all required fields.'
    return false
  }
  if (step.value === 2 && form.password !== form.confirmPassword) {
    error.value = 'Passwords do not match.'
    return false
  }
  return true
}

async function setupBiometric() {
  bioBusy.value = true
  error.value = ''
  try {
    await registerBiometric({ id: form.email.trim().toLowerCase(), name: form.fullName, email: form.email })
    bioRegistered.value = true
    ui.toast(`${bioLabel} registered on this device.`)
  } catch {
    error.value = `Could not set up ${bioLabel}. Make sure a screen lock and biometric are enabled on your phone.`
  } finally {
    bioBusy.value = false
  }
}

function back() {
  error.value = ''
  step.value--
}

async function submit() {
  error.value = ''
  if (!stepValid()) return
  if (isLast.value && bioSupported.value && !bioRegistered.value) {
    error.value = `Register your ${bioLabel} to finish creating your account.`
    return
  }
  if (!isLast.value) {
    step.value++
    return
  }
  loading.value = true
  try {
    const created = await api.post('/api/auth/register', {
      fullName: form.fullName, studentId: form.studentId, email: form.email, contact: form.contact,
      school: form.school, course: form.course, yearLevel: form.yearLevel, password: form.password,
      biometricRegistered: bioRegistered.value,
    })
    // The phone credential was saved under the email; re-key it to the new account id for Attendance.
    if (bioRegistered.value) moveCredential(form.email.trim().toLowerCase(), created.id)
    ui.toast('Application submitted. A Super Admin will review it and deploy you to an organization.')
    router.push('/login')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="font-headline text-2xl font-semibold text-neutral-900">Create your OJT trainee account</h2>
    <p class="text-sm text-neutral-500 mt-1.5">Your application will be reviewed, then you'll be deployed to an organization once approved.</p>

    <ol class="flex items-center mt-6">
      <li v-for="(s, i) in steps" :key="s.title" class="flex items-center" :class="i < steps.length - 1 ? 'flex-1' : ''">
        <div class="flex items-center gap-2 shrink-0">
          <span
            class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold font-label transition-colors"
            :class="i < step ? 'bg-primary-600 text-white' : i === step ? 'bg-primary-600 text-white ring-4 ring-primary-500/15' : 'bg-neutral-200 text-neutral-500'"
          >
            <Check v-if="i < step" class="w-3.5 h-3.5" />
            <template v-else>{{ i + 1 }}</template>
          </span>
          <span class="text-sm font-medium hidden sm:inline" :class="i <= step ? 'text-neutral-800' : 'text-neutral-400'">{{ s.title }}</span>
        </div>
        <div v-if="i < steps.length - 1" class="flex-1 h-0.5 mx-3 rounded-full transition-colors" :class="i < step ? 'bg-primary-600' : 'bg-neutral-200'" />
      </li>
    </ol>
    <p class="sm:hidden text-xs font-label uppercase tracking-wide text-neutral-400 mt-3">Step {{ step + 1 }} of {{ steps.length }} · {{ steps[step].title }}</p>

    <form class="mt-6" novalidate @submit.prevent="submit">
      <div v-show="step === 0" class="space-y-4">
        <BaseInput v-model="form.fullName" label="Full name" placeholder="Juan Dela Cruz" :icon="User" required />
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <BaseInput v-model="form.studentId" label="Student ID number" placeholder="2021-00214-NT" :icon="IdCard" required />
          <BaseInput v-model="form.contact" label="Contact number" placeholder="0917 234 5678" :icon="Phone" required />
        </div>
      </div>

      <div v-show="step === 1" class="space-y-4">
        <BaseInput v-model="form.school" label="School" placeholder="Northbridge Institute of Technology" :icon="School" required />
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <BaseInput v-model="form.course" label="Course / Program" placeholder="BS Information Technology" required />
          <BaseSelect v-model="form.yearLevel" label="Year level" :options="yearLevels" required />
        </div>
      </div>

      <div v-show="step === 2" class="space-y-4">
        <BaseInput v-model="form.email" type="email" label="Email address" placeholder="you@example.com" :icon="Mail" required />
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <BaseInput v-model="form.password" type="password" label="Password" placeholder="••••••••" :icon="Lock" required />
          <BaseInput v-model="form.confirmPassword" type="password" label="Confirm password" placeholder="••••••••" :icon="Lock" required />
        </div>
      </div>

      <div v-show="step === 3" class="space-y-4">
        <div class="rounded-xl border border-neutral-200 bg-neutral-50 p-5 text-center">
          <div class="w-14 h-14 rounded-full mx-auto mb-3 flex items-center justify-center" :class="bioRegistered ? 'bg-success-500/15' : 'bg-primary-50'">
            <Check v-if="bioRegistered" class="w-7 h-7 text-success-600" />
            <ScanFace v-else-if="isIos" class="w-7 h-7 text-primary-600" />
            <Fingerprint v-else class="w-7 h-7 text-primary-600" />
          </div>
          <p class="font-medium text-neutral-800">{{ bioRegistered ? `${bioLabel} registered` : `Register your ${bioLabel}` }}</p>
          <p class="text-sm text-neutral-500 mt-1">
            This is how you'll verify Time In / Time Out. Your biometric stays on your phone; GeoTrack never stores it.
          </p>
          <BaseButton v-if="bioSupported && !bioRegistered" type="button" class="mt-4" :disabled="bioBusy" @click="setupBiometric">
            <Loader2 v-if="bioBusy" class="w-4 h-4 animate-spin" />
            <ShieldCheck v-else class="w-4 h-4" />
            {{ bioBusy ? 'Waiting for your phone…' : `Set up ${bioLabel}` }}
          </BaseButton>
          <p v-if="!bioSupported" class="text-sm text-warning-700 mt-3">
            This device doesn't support biometrics (or the page isn't on HTTPS). You can finish now, but you must register {{ bioLabel }} on your phone before your first Time In.
          </p>
        </div>
      </div>

      <p v-if="error" class="text-sm text-danger-600 mt-4">{{ error }}</p>

      <div class="flex items-center gap-3 mt-6">
        <BaseButton v-if="step > 0" type="button" variant="outline" @click="back"><ArrowLeft class="w-4 h-4" /> Back</BaseButton>
        <BaseButton type="submit" class="flex-1" :disabled="loading">
          <template v-if="!isLast">Next <ArrowRight class="w-4 h-4" /></template>
          <template v-else>
            <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
            <UserPlus v-else class="w-4 h-4" />
            {{ loading ? 'Creating account…' : 'Create account' }}
          </template>
        </BaseButton>
      </div>
    </form>

    <p class="text-center text-sm text-neutral-500 mt-6">
      Already have an account?
      <RouterLink to="/login" class="text-primary-600 font-medium hover:underline">Sign in</RouterLink>
    </p>
  </div>
</template>
