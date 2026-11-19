<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Users, CalendarX, Percent, AlertTriangle, Loader2, UserX } from '@lucide/vue'
import { api } from '../../lib/api'
import PageHeader from '../../components/ui/PageHeader.vue'
import StatCard from '../../components/ui/StatCard.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import ProgressBar from '../../components/ui/ProgressBar.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const org = ref(null)
const trainees = ref([])
const summary = ref(null)

const filter = ref('All')
const filters = ['All', 'Frequent absences']
const shown = computed(() => (filter.value === 'All' ? trainees.value : trainees.value.filter((t) => t.stats.frequentAbsent)))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get(`/api/super-admin/organizations/${route.params.id}/trainees`)
    org.value = res.organization
    trainees.value = res.trainees
    summary.value = res.summary
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
onMounted(load)

const initials = (name) => name.split(' ').map((n) => n[0]).slice(0, 2).join('')
const shortDate = (iso) => new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
const rateTone = (rate) => (rate >= 90 ? 'success' : rate >= 75 ? 'warning' : 'danger')
</script>

<template>
  <div>
    <button class="flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-700 mb-4 cursor-pointer" @click="router.push('/super-admin/organizations')">
      <ArrowLeft class="w-4 h-4" /> Back to Organizations
    </button>

    <div v-if="loading" class="flex items-center justify-center gap-2 py-24 text-sm text-neutral-500">
      <Loader2 class="w-4 h-4 animate-spin" /> Loading trainees…
    </div>

    <div v-else-if="error" class="max-w-md mx-auto text-center py-16">
      <AlertTriangle class="w-10 h-10 text-danger-500 mx-auto mb-3" />
      <p class="font-medium text-neutral-800">Couldn't load this organization</p>
      <p class="text-sm text-neutral-500 mt-1">{{ error }}</p>
      <button class="mt-4 px-4 py-2 rounded-lg bg-primary-600 text-white text-sm font-medium cursor-pointer" @click="load">Try again</button>
    </div>

    <template v-else>
      <PageHeader :title="org.name" :subtitle="`${org.address || 'No address'} · assigned OJT trainees and their attendance`">
        <template #actions><StatusBadge :status="org.status" /></template>
      </PageHeader>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="OJT Trainees" :value="summary.totalTrainees" :icon="Users" tone="primary" />
        <StatCard label="Attendance Rate" :value="summary.averageAttendanceRate === null ? '—' : `${summary.averageAttendanceRate}%`" :icon="Percent" tone="success" />
        <StatCard label="Absences" :value="summary.totalAbsences" :icon="CalendarX" tone="secondary" />
        <StatCard label="Frequent Absentees" :value="summary.frequentAbsentees" :icon="UserX" tone="warning" />
      </div>

      <div class="flex items-center gap-2 mt-6 mb-4">
        <button
          v-for="f in filters" :key="f"
          class="px-3.5 py-1.5 rounded-lg text-sm font-medium cursor-pointer transition-colors"
          :class="filter === f ? 'bg-primary-600 text-white' : 'bg-white border border-neutral-200 text-neutral-600 hover:bg-neutral-50'"
          @click="filter = f"
        >{{ f }}</button>
      </div>

      <EmptyState v-if="!trainees.length" :icon="Users" title="No OJT trainees assigned yet" description="Approve and deploy applicants to this organization from Applications & Deployment." />
      <EmptyState v-else-if="!shown.length" :icon="UserX" title="No frequent absentees" description="Everyone here is attending regularly." />

      <BaseCard v-else :padded="false" class="overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-neutral-50 text-neutral-500 text-xs uppercase tracking-wide">
              <tr>
                <th class="text-left font-medium px-5 py-3">OJT Trainee</th>
                <th class="text-left font-medium px-5 py-3">Present</th>
                <th class="text-left font-medium px-5 py-3">Absent</th>
                <th class="text-left font-medium px-5 py-3">Late</th>
                <th class="text-left font-medium px-5 py-3 w-44">Attendance</th>
                <th class="text-left font-medium px-5 py-3">Recent absences</th>
                <th class="text-left font-medium px-5 py-3">Last seen</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neutral-100">
              <tr v-for="t in shown" :key="t.id" :class="t.stats.frequentAbsent ? 'bg-warning-50/40' : ''">
                <td class="px-5 py-3.5">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-semibold shrink-0">{{ initials(t.name) }}</div>
                    <div class="min-w-0">
                      <p class="font-medium text-neutral-800 truncate">{{ t.name }}</p>
                      <p class="text-xs text-neutral-500 truncate">{{ t.studentId }} · {{ t.course }}</p>
                      <span v-if="t.stats.frequentAbsent" class="inline-flex items-center gap-1 mt-1 text-[11px] font-medium text-warning-700 bg-warning-50 border border-warning-500/30 rounded-full px-2 py-0.5">
                        <AlertTriangle class="w-3 h-3" /> Frequent absences
                      </span>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-3.5 text-neutral-700">{{ t.stats.daysPresent }}<span class="text-neutral-400"> / {{ t.stats.workingDays }}</span></td>
                <td class="px-5 py-3.5">
                  <span class="font-semibold" :class="t.stats.daysAbsent ? (t.stats.frequentAbsent ? 'text-danger-600' : 'text-neutral-800') : 'text-neutral-400'">{{ t.stats.daysAbsent }}</span>
                  <p v-if="t.stats.absentLast30Days" class="text-[11px] text-neutral-400">{{ t.stats.absentLast30Days }} in last 30 days</p>
                </td>
                <td class="px-5 py-3.5 text-neutral-700">{{ t.stats.lateCount }}</td>
                <td class="px-5 py-3.5">
                  <div v-if="t.stats.attendanceRate !== null" class="flex items-center gap-2">
                    <ProgressBar :value="t.stats.attendanceRate" size="sm" :tone="rateTone(t.stats.attendanceRate)" />
                    <span class="text-xs text-neutral-500 shrink-0 w-9 text-right">{{ t.stats.attendanceRate }}%</span>
                  </div>
                  <span v-else class="text-xs text-neutral-400">No full day yet</span>
                </td>
                <td class="px-5 py-3.5 text-xs text-neutral-500">
                  <template v-if="t.stats.recentAbsences.length">{{ t.stats.recentAbsences.map(shortDate).join(', ') }}</template>
                  <span v-else class="text-neutral-300">—</span>
                </td>
                <td class="px-5 py-3.5 text-xs text-neutral-500 font-label">{{ t.stats.lastAttendance ? shortDate(t.stats.lastAttendance) : 'Never' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </BaseCard>

      <p class="text-xs text-neutral-400 mt-3">
        An absence is a Mon–Fri working day since the trainee's start date with no Time In. "Frequent absences" means 3 or more absences and at least 20% of working days. Today is not counted until it ends, and holidays are not excluded yet.
      </p>
    </template>
  </div>
</template>
