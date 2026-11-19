<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Clock, TrendingUp, FileText, MapPinned, ArrowRight, AlertCircle } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import PageHeader from '../../components/ui/PageHeader.vue'
import StatCard from '../../components/ui/StatCard.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import ProgressBar from '../../components/ui/ProgressBar.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const auth = useAuthStore()
const router = useRouter()

const intern = computed(() => data.currentIntern)
const progressPct = computed(() => Math.round((intern.value.renderedHours / intern.value.requiredHours) * 100))
const remainingHours = computed(() => Math.max(0, intern.value.requiredHours - intern.value.renderedHours))
const recentLogs = computed(() => data.internLogs(intern.value.id).slice(0, 3))
const recentAttendance = computed(() => data.internAttendance(intern.value.id).slice(0, 5))

const todayStr = new Date().toISOString().slice(0, 10)
const todayIn = computed(() => data.attendanceRecords.find((a) => a.internId === intern.value.id && a.date === todayStr && a.type === 'Time In'))
const todayOut = computed(() => data.attendanceRecords.find((a) => a.internId === intern.value.id && a.date === todayStr && a.type === 'Time Out'))
</script>

<template>
  <div>
    <PageHeader :title="`Welcome back, ${intern.name.split(' ')[0]}`" subtitle="Here's your OJT snapshot for today.">
      <template #actions>
        <BaseButton @click="router.push('/intern/attendance')">
          <MapPinned class="w-4 h-4" /> Go to Attendance
        </BaseButton>
      </template>
    </PageHeader>

    <div v-if="intern.applicationStatus !== 'Approved'" class="mb-6 rounded-xl border border-warning-500/30 bg-warning-50 px-4 py-3 flex items-center gap-3">
      <AlertCircle class="w-5 h-5 text-warning-600 shrink-0" />
      <p class="text-sm text-warning-700">
        Your application status is <strong>{{ intern.applicationStatus }}</strong>. Attendance and daily logs unlock once your application is approved.
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="Rendered Hours" :value="`${intern.renderedHours}h`" :icon="Clock" tone="primary" :trend="`of ${intern.requiredHours}h required`" />
      <StatCard label="Progress" :value="`${progressPct}%`" :icon="TrendingUp" tone="secondary" :trend="`${remainingHours}h remaining`" />
      <StatCard label="Today's Status" :value="todayOut ? 'Completed' : todayIn ? 'Timed In' : 'Not yet'" :icon="MapPinned" :tone="todayOut ? 'success' : todayIn ? 'primary' : 'neutral'" />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      <BaseCard class="lg:col-span-1">
        <h3 class="font-headline font-semibold text-neutral-900">OJT Progress</h3>
        <p class="text-sm text-neutral-500 mt-1">{{ intern.internshipStatus }} · {{ intern.startDate || 'TBD' }} → {{ intern.endDate || 'TBD' }}</p>
        <div class="mt-5">
          <div class="flex items-baseline justify-between mb-2">
            <span class="font-headline text-3xl font-semibold text-neutral-900">{{ progressPct }}%</span>
            <span class="text-sm text-neutral-500">{{ intern.renderedHours }}h / {{ intern.requiredHours }}h</span>
          </div>
          <ProgressBar :value="progressPct" />
        </div>
        <BaseButton variant="outline" size="sm" block class="mt-5" @click="router.push('/intern/progress')">
          View full breakdown <ArrowRight class="w-3.5 h-3.5" />
        </BaseButton>
      </BaseCard>

      <BaseCard class="lg:col-span-2">
        <div class="flex items-center justify-between mb-1">
          <h3 class="font-headline font-semibold text-neutral-900">Recent Attendance</h3>
          <RouterLink to="/intern/attendance" class="text-sm text-primary-600 font-medium hover:underline">View all</RouterLink>
        </div>
        <EmptyState v-if="!recentAttendance.length" :icon="MapPinned" title="No attendance records yet" description="Your Time In / Time Out events will appear here." />
        <div v-else class="divide-y divide-neutral-100 mt-2">
          <div v-for="a in recentAttendance" :key="a.id" class="py-3 flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-neutral-800">{{ a.type }} <span class="text-neutral-400 font-normal">· {{ a.timestamp }}</span></p>
              <p class="text-xs text-neutral-500 mt-0.5">{{ a.distance }}m from location · biometric + GPS verified</p>
            </div>
            <StatusBadge :status="a.status" size="sm" />
          </div>
        </div>
      </BaseCard>
    </div>

    <BaseCard class="mt-6">
      <div class="flex items-center justify-between mb-1">
        <h3 class="font-headline font-semibold text-neutral-900">Recent Daily Logs</h3>
        <RouterLink to="/intern/daily-logs" class="text-sm text-primary-600 font-medium hover:underline">View all</RouterLink>
      </div>
      <EmptyState v-if="!recentLogs.length" :icon="FileText" title="No daily logs yet" />
      <div v-else class="divide-y divide-neutral-100 mt-2">
        <div v-for="log in recentLogs" :key="log.id" class="py-3 flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm font-medium text-neutral-800">{{ log.date }}</p>
            <p class="text-sm text-neutral-500 mt-0.5 line-clamp-1">{{ log.activities }}</p>
          </div>
          <StatusBadge :status="log.status" size="sm" />
        </div>
      </div>
    </BaseCard>
  </div>
</template>
