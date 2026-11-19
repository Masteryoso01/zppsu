<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  MapPinned, Fingerprint, ScanFace, Navigation, CheckCircle2, XCircle,
  Loader2, History, AlertTriangle, LogIn, LogOut, Info,
} from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useUiStore } from '../../stores/ui'
import { formatDistance } from '../../lib/geo'
import { biometricLabel, hasCredential, isBiometricSupported, registerBiometric, verifyBiometric } from '../../lib/biometric'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const ui = useUiStore()
const intern = computed(() => data.currentIntern)
// The API only returns this trainee's organization's active locations.
const location = computed(() => data.locations[0])

const todayStr = new Date().toISOString().slice(0, 10)
const todayIn = computed(() => data.attendanceRecords.find((a) => a.internId === intern.value.id && a.date === todayStr && a.type === 'Time In'))
const todayOut = computed(() => data.attendanceRecords.find((a) => a.internId === intern.value.id && a.date === todayStr && a.type === 'Time Out'))
const action = computed(() => (!todayIn.value ? 'Time In' : !todayOut.value ? 'Time Out' : null))

// Simulated GPS exists for demos only; production builds always use the real device location.
const canSimulate = import.meta.env.DEV
const simulateInRange = ref(canSimulate)

const phase = ref('idle') // idle | running | success | failed
const activeStepIndex = ref(-1)
const result = ref(null) // { distance, status, reason, stage }
const verifiedAction = ref(null) // snapshot of `action` at the moment verification started

const bioLabel = biometricLabel()
const isIos = bioLabel === 'Face ID'
const supported = ref(true)
const registered = ref(false)
const registering = ref(false)

const pipeline = [
  { key: 'biometric', label: `${bioLabel} verification`, icon: isIos ? ScanFace : Fingerprint },
  { key: 'gps', label: 'GPS acquisition', icon: Navigation },
  { key: 'radius', label: 'Radius validation', icon: MapPinned },
]

onMounted(async () => {
  supported.value = await isBiometricSupported()
  registered.value = hasCredential(intern.value.id)
})

function wait(ms) { return new Promise((r) => setTimeout(r, ms)) }

async function setupBiometric() {
  registering.value = true
  try {
    await registerBiometric(intern.value)
    registered.value = true
    ui.toast(`${bioLabel} set up on this device.`)
  } catch {
    ui.toast(`Could not set up ${bioLabel}. Make sure a screen lock/biometric is enabled on your phone.`, 'danger')
  } finally {
    registering.value = false
  }
}

async function startVerification() {
  verifiedAction.value = action.value
  phase.value = 'running'
  await runPipeline()
}

async function runPipeline() {
  let coords = null
  let record = null
  for (let i = 0; i < pipeline.length; i++) {
    activeStepIndex.value = i
    const key = pipeline[i].key

    if (key === 'biometric') {
      try {
        await verifyBiometric(intern.value.id)
      } catch (e) {
        const msg = e?.name === 'NotAllowedError' ? `${bioLabel} was cancelled or not recognised.` : `${bioLabel} verification failed.`
        return fail(msg, `${bioLabel} Verification`)
      }
      continue
    }

    if (key === 'gps') {
      await wait(400)
      if (canSimulate && simulateInRange.value) {
        coords = { latitude: location.value.latitude + 0.0003, longitude: location.value.longitude + 0.0002 }
      } else {
        try {
          coords = await new Promise((resolve, reject) =>
            navigator.geolocation.getCurrentPosition((pos) => resolve(pos.coords), reject, { enableHighAccuracy: true, timeout: 8000 })
          )
        } catch {
          return fail('GPS unavailable — location permission denied or timed out.', 'GPS Acquisition')
        }
      }
      continue
    }

    if (key === 'radius') {
      // The server validates the geofence itself and records Time In / Time Out.
      try {
        record = await data.clock({
          locationId: location.value.id, latitude: coords.latitude, longitude: coords.longitude, method: bioLabel,
        })
      } catch (e) {
        return fail(e.message, 'GPS Radius Validation')
      }
      continue
    }
  }

  succeed(record)
}

function fail(reason, stage) {
  phase.value = 'failed'
  result.value = { ...result.value, reason, stage }
  ui.toast(reason, 'danger')
}

function succeed(record) {
  phase.value = 'success'
  result.value = { ...result.value, record, distance: record.distance }
  ui.toast(`${verifiedAction.value} recorded successfully.`)
}

function reset() {
  phase.value = 'idle'
  activeStepIndex.value = -1
  result.value = null
}

const recent = computed(() => data.internAttendance(intern.value.id).slice(0, 6))
</script>

<template>
  <div>
    <PageHeader title="Attendance" subtitle="Time In / Time Out with your phone's fingerprint or Face ID, plus GPS verification." />

    <EmptyState
      v-if="!location"
      :icon="MapPinned"
      title="Attendance isn't available yet"
      :description="intern?.applicationStatus === 'Approved' ? 'Your organization has not set up an attendance location yet.' : 'Attendance unlocks once a Super Admin approves your application and deploys you to an organization.'"
    />

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <BaseCard class="lg:col-span-2">
        <!-- Idle state -->
        <div v-if="phase === 'idle'">
          <div v-if="!action" class="text-center py-10">
            <CheckCircle2 class="w-12 h-12 text-success-500 mx-auto mb-3" />
            <p class="font-medium text-neutral-800">You're all set for today</p>
            <p class="text-sm text-neutral-500 mt-1">Time In and Time Out have both been recorded.</p>
          </div>
          <div v-else class="text-center py-10">
            <div class="w-16 h-16 rounded-2xl bg-primary-50 flex items-center justify-center mx-auto mb-4">
              <component :is="action === 'Time In' ? LogIn : LogOut" class="w-8 h-8 text-primary-600" />
            </div>
            <p class="font-headline text-xl font-semibold text-neutral-900">Ready to {{ action }}?</p>
            <p class="text-sm text-neutral-500 mt-1 max-w-sm mx-auto">
              We'll verify it's you with {{ bioLabel }} and confirm you're within {{ location.radius }}m of {{ location.name }}.
            </p>

            <label v-if="canSimulate" class="flex items-center justify-center gap-2 mt-5 text-xs text-neutral-500">
              <input v-model="simulateInRange" type="checkbox" class="rounded border-neutral-300 text-primary-600 focus:ring-primary-500" />
              Simulate GPS within range (demo) — uncheck to use your real device location
            </label>

            <p v-if="!supported" class="mt-5 text-sm text-warning-700 max-w-sm mx-auto">
              This device or browser doesn't support fingerprint / Face ID (needs HTTPS and a phone with screen lock biometrics set up).
            </p>
            <BaseButton v-else-if="!registered" class="mt-5" size="lg" :disabled="registering" @click="setupBiometric">
              <component :is="isIos ? ScanFace : Fingerprint" class="w-4 h-4" /> Set up {{ bioLabel }} on this phone
            </BaseButton>
            <BaseButton v-else class="mt-5" size="lg" @click="startVerification">
              <component :is="isIos ? ScanFace : Fingerprint" class="w-4 h-4" /> {{ action }} with {{ bioLabel }}
            </BaseButton>
          </div>
        </div>

        <!-- Running -->
        <div v-else-if="phase === 'running'">
          <ul class="space-y-2.5">
            <li v-for="(s, i) in pipeline" :key="s.key" class="flex items-center gap-3 text-sm">
              <div class="w-7 h-7 rounded-full flex items-center justify-center shrink-0"
                :class="i < activeStepIndex ? 'bg-success-500 text-white' : i === activeStepIndex ? 'bg-primary-600 text-white' : 'bg-neutral-100 text-neutral-400'">
                <CheckCircle2 v-if="i < activeStepIndex" class="w-4 h-4" />
                <Loader2 v-else-if="i === activeStepIndex" class="w-3.5 h-3.5 animate-spin" />
                <component :is="s.icon" v-else class="w-3.5 h-3.5" />
              </div>
              <span :class="i <= activeStepIndex ? 'text-neutral-800 font-medium' : 'text-neutral-400'">{{ s.label }}</span>
            </li>
          </ul>
        </div>

        <!-- Success -->
        <div v-else-if="phase === 'success'" class="text-center py-8">
          <div class="w-16 h-16 rounded-full bg-success-50 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 class="w-8 h-8 text-success-600" />
          </div>
          <p class="font-headline text-xl font-semibold text-neutral-900">{{ verifiedAction === 'Time In' ? 'Timed In' : 'Timed Out' }} successfully</p>
          <p class="text-sm text-neutral-500 mt-1">{{ result.record?.timestamp }} · {{ formatDistance(result.distance) }} from {{ location.name }}</p>
          <div class="flex items-center justify-center gap-2 mt-4 flex-wrap">
            <StatusBadge status="Approved" size="sm">{{ bioLabel }} Verified</StatusBadge>
            <StatusBadge status="Approved" size="sm">GPS Verified</StatusBadge>
          </div>
          <BaseButton class="mt-6" variant="outline" @click="reset">Done</BaseButton>
        </div>

        <!-- Failed -->
        <div v-else-if="phase === 'failed'" class="text-center py-8">
          <div class="w-16 h-16 rounded-full bg-danger-50 flex items-center justify-center mx-auto mb-4">
            <XCircle class="w-8 h-8 text-danger-600" />
          </div>
          <p class="font-headline text-xl font-semibold text-neutral-900">Verification failed</p>
          <p class="text-sm text-neutral-500 mt-2 max-w-sm mx-auto">{{ result.reason }}</p>
          <p class="text-xs text-neutral-400 mt-1 font-label">Failed at: {{ result.stage }}</p>
          <BaseButton class="mt-6" @click="reset">Try Again</BaseButton>
        </div>
      </BaseCard>

      <div class="space-y-6">
        <BaseCard>
          <h3 class="font-headline font-semibold text-neutral-900 mb-3">Today</h3>
          <div class="space-y-3 text-sm">
            <div class="flex items-center justify-between">
              <span class="text-neutral-500">Time In</span>
              <span class="font-medium text-neutral-800 font-label">{{ todayIn ? todayIn.timestamp.split(' ')[1] : '—' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-neutral-500">Time Out</span>
              <span class="font-medium text-neutral-800 font-label">{{ todayOut ? todayOut.timestamp.split(' ')[1] : '—' }}</span>
            </div>
          </div>
        </BaseCard>

        <BaseCard>
          <h3 class="font-headline font-semibold text-neutral-900 mb-1 flex items-center gap-2"><MapPinned class="w-4 h-4 text-primary-600" /> Configured Location</h3>
          <p class="text-sm text-neutral-800 font-medium mt-2">{{ location.name }}</p>
          <p class="text-xs text-neutral-400 font-label mt-0.5">{{ location.latitude.toFixed(4) }}, {{ location.longitude.toFixed(4) }}</p>
          <p class="text-xs text-neutral-500 mt-2">Allowed radius: {{ location.radius }}m</p>
          <div class="mt-3 flex items-start gap-2 bg-neutral-50 rounded-lg px-2.5 py-2">
            <Info class="w-3.5 h-3.5 text-neutral-400 shrink-0 mt-0.5" />
            <p class="text-[11px] text-neutral-500 leading-relaxed">Location is only collected during Time In / Time Out for verification — not tracked continuously.</p>
          </div>
        </BaseCard>

        <BaseCard>
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-headline font-semibold text-neutral-900 flex items-center gap-2"><History class="w-4 h-4 text-primary-600" /> Recent</h3>
          </div>
          <EmptyState v-if="!recent.length" :icon="History" title="No attendance yet" />
          <ul v-else class="space-y-2.5">
            <li v-for="r in recent" :key="r.id" class="flex items-center justify-between text-sm">
              <span class="text-neutral-600">{{ r.type }} · {{ r.timestamp.split(' ')[0] }}</span>
              <StatusBadge :status="r.status" size="sm" />
            </li>
          </ul>
        </BaseCard>

        <div v-if="data.failedAttempts.filter(f => f.internId === intern.id).length" class="rounded-xl border border-warning-500/30 bg-warning-50 px-4 py-3 flex items-start gap-2.5">
          <AlertTriangle class="w-4 h-4 text-warning-600 shrink-0 mt-0.5" />
          <p class="text-xs text-warning-700">You have {{ data.failedAttempts.filter(f => f.internId === intern.id).length }} recent failed verification attempts.</p>
        </div>
      </div>
    </div>
  </div>
</template>
