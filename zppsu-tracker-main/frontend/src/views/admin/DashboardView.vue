<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Users, UserCheck, MapPinned, ClipboardList, ArrowRight, AlertCircle } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import PageHeader from '../../components/ui/PageHeader.vue'
import StatCard from '../../components/ui/StatCard.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const auth = useAuthStore()
const router = useRouter()

const orgId = computed(() => auth.user.orgId)
const orgInterns = computed(() => data.orgInterns(orgId.value))
const activeCount = computed(() => orgInterns.value.filter((i) => i.internshipStatus === 'Ongoing').length)
const recentInterns = computed(() => orgInterns.value.slice(0, 5))
const pendingLogs = computed(() => data.pendingLogs.filter((l) => orgInterns.value.some((i) => i.id === l.internId)))
const todayAttendance = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return data.attendanceRecords.filter((a) => a.date === today && orgInterns.value.some((i) => i.id === a.internId))
})
const recentActivity = computed(() => data.auditLogs.slice(0, 6))
</script>

<template>
  <div>
    <PageHeader :title="`${auth.user.orgName || 'Organization'} Overview`" subtitle="Monitor your deployed OJT trainees and attendance at a glance.">
      <template #actions>
        <BaseButton @click="router.push('/admin/daily-logs')"><ClipboardList class="w-4 h-4" /> Review Daily Logs</BaseButton>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="Total OJT Trainees" :value="orgInterns.length" :icon="Users" tone="primary" />
      <StatCard label="Ongoing OJT" :value="activeCount" :icon="ClipboardList" tone="secondary" />
      <StatCard label="Pending Daily Logs" :value="pendingLogs.length" :icon="UserCheck" tone="warning" />
      <StatCard label="Today's Attendance" :value="todayAttendance.length" :icon="MapPinned" tone="success" />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      <BaseCard class="lg:col-span-2">
        <div class="flex items-center justify-between mb-1">
          <h3 class="font-headline font-semibold text-neutral-900">Deployed OJT Trainees</h3>
          <RouterLink to="/admin/interns" class="text-sm text-primary-600 font-medium hover:underline">View all</RouterLink>
        </div>
        <EmptyState v-if="!recentInterns.length" :icon="Users" title="No OJT trainees deployed yet" />
        <div v-else class="divide-y divide-neutral-100 mt-2">
          <div v-for="i in recentInterns" :key="i.id" class="py-3 flex items-center justify-between gap-3">
            <div class="min-w-0 flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-semibold shrink-0">
                {{ i.name.split(' ').map(n => n[0]).slice(0,2).join('') }}
              </div>
              <div class="min-w-0">
                <p class="text-sm font-medium text-neutral-800 truncate">{{ i.name }}</p>
                <p class="text-xs text-neutral-500 truncate">{{ i.course }} · {{ i.studentId }}</p>
              </div>
            </div>
            <StatusBadge :status="i.internshipStatus" size="sm" />
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <h3 class="font-headline font-semibold text-neutral-900 mb-3">Needs Attention</h3>
        <div class="space-y-3">
          <button class="w-full flex items-center justify-between text-left px-3 py-2.5 rounded-lg hover:bg-neutral-50 cursor-pointer" @click="router.push('/admin/daily-logs')">
            <span class="flex items-center gap-2.5 text-sm text-neutral-700"><AlertCircle class="w-4 h-4 text-warning-500" /> {{ pendingLogs.length }} daily logs awaiting review</span>
            <ArrowRight class="w-3.5 h-3.5 text-neutral-400" />
          </button>
        </div>
      </BaseCard>
    </div>

    <BaseCard class="mt-6">
      <h3 class="font-headline font-semibold text-neutral-900 mb-3">Recent Activity</h3>
      <div class="divide-y divide-neutral-100">
        <div v-for="log in recentActivity" :key="log.id" class="py-2.5 flex items-center justify-between gap-3 text-sm">
          <div class="min-w-0">
            <span class="text-neutral-700 font-medium">{{ log.user }}</span>
            <span class="text-neutral-500"> {{ log.action.toLowerCase() }} — {{ log.resource }}</span>
          </div>
          <span class="text-xs text-neutral-400 font-label shrink-0">{{ log.timestamp }}</span>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
