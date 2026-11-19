<script setup>
import { computed, ref } from 'vue'
import { Search, MapPinned, AlertTriangle } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const auth = useAuthStore()
const q = ref('')

const orgInternIds = computed(() => data.orgInterns(auth.user.orgId).map((i) => i.id))
function internName(id) { return data.interns.find((i) => i.id === id)?.name || id }

const records = computed(() => {
  let list = data.attendanceRecords.filter((a) => orgInternIds.value.includes(a.internId))
  if (q.value) {
    const s = q.value.toLowerCase()
    list = list.filter((a) => internName(a.internId).toLowerCase().includes(s))
  }
  return list
})

const failedAttempts = computed(() => data.failedAttempts.filter((f) => orgInternIds.value.includes(f.internId)))
</script>

<template>
  <div>
    <PageHeader title="Attendance" subtitle="Review Time In / Time Out records across your organization." />

    <div v-if="failedAttempts.length" class="mb-6 rounded-xl border border-danger-500/20 bg-danger-50 px-4 py-3">
      <p class="text-sm font-medium text-danger-700 flex items-center gap-2 mb-2"><AlertTriangle class="w-4 h-4" /> Recent Failed Verification Attempts</p>
      <div class="space-y-1.5">
        <div v-for="f in failedAttempts" :key="f.id" class="text-xs text-danger-600 flex items-center justify-between gap-3">
          <span>{{ internName(f.internId) }} — {{ f.reason }}</span>
          <span class="font-label shrink-0">{{ f.timestamp }}</span>
        </div>
      </div>
    </div>

    <BaseInput v-model="q" placeholder="Search by trainee name..." :icon="Search" class="mb-5 max-w-md" />

    <EmptyState v-if="!records.length" :icon="MapPinned" title="No attendance records" />
    <BaseCard v-else :padded="false" class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-neutral-50 text-neutral-500 text-xs uppercase tracking-wide"><tr>
            <th class="text-left font-medium px-5 py-3">OJT Trainee</th>
            <th class="text-left font-medium px-5 py-3">Type</th>
            <th class="text-left font-medium px-5 py-3">Timestamp</th>
            <th class="text-left font-medium px-5 py-3">Distance</th>
            <th class="text-left font-medium px-5 py-3">Verification</th>
            <th class="text-left font-medium px-5 py-3">Status</th>
          </tr></thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="a in records" :key="a.id" class="hover:bg-neutral-50">
              <td class="px-5 py-3 font-medium text-neutral-800">{{ internName(a.internId) }}</td>
              <td class="px-5 py-3">{{ a.type }}</td>
              <td class="px-5 py-3 font-label text-neutral-500">{{ a.timestamp }}</td>
              <td class="px-5 py-3">{{ a.distance }}m</td>
              <td class="px-5 py-3">
                <div class="flex gap-1">
                  <span class="w-2 h-2 rounded-full" :class="a.faceVerified ? 'bg-success-500' : 'bg-danger-500'" title="Face" />
                  <span class="w-2 h-2 rounded-full" :class="a.livenessVerified ? 'bg-success-500' : 'bg-danger-500'" title="Liveness" />
                  <span class="w-2 h-2 rounded-full" :class="a.gpsVerified ? 'bg-success-500' : 'bg-danger-500'" title="GPS" />
                </div>
              </td>
              <td class="px-5 py-3"><StatusBadge :status="a.status" size="sm" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>
  </div>
</template>
