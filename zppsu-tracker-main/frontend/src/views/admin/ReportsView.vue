<script setup>
import { computed } from 'vue'
import { Download, Users, Clock, CheckCircle2, AlertTriangle } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import StatCard from '../../components/ui/StatCard.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import ProgressBar from '../../components/ui/ProgressBar.vue'

const data = useDataStore()
const auth = useAuthStore()
const ui = useUiStore()

const interns = computed(() => data.orgInterns(auth.user.orgId))
const completed = computed(() => interns.value.filter((i) => i.internshipStatus === 'Completed').length)
const avgProgress = computed(() => Math.round(interns.value.reduce((s, i) => s + i.renderedHours / i.requiredHours, 0) / interns.value.length * 100) || 0)
const lateCount = computed(() => data.attendanceRecords.filter((a) => a.status === 'Late' && interns.value.some((i) => i.id === a.internId)).length)
const totalHours = computed(() => interns.value.reduce((s, i) => s + i.renderedHours, 0))

const statusBreakdown = computed(() => {
  const map = {}
  interns.value.forEach((i) => { map[i.internshipStatus] = (map[i.internshipStatus] || 0) + 1 })
  return Object.entries(map).map(([label, count]) => ({ label, count }))
})

function exportReport() {
  ui.toast('Report export started — you will be notified when it is ready.')
}
</script>

<template>
  <div>
    <PageHeader title="Reports" subtitle="Attendance, progress, and completion reports for your organization.">
      <template #actions>
        <BaseButton variant="outline" @click="exportReport"><Download class="w-4 h-4" /> Export CSV</BaseButton>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard label="Total OJT Trainees" :value="interns.length" :icon="Users" tone="primary" />
      <StatCard label="Avg. Progress" :value="`${avgProgress}%`" :icon="Clock" tone="secondary" />
      <StatCard label="Completed" :value="completed" :icon="CheckCircle2" tone="success" />
      <StatCard label="Late Time-Ins" :value="lateCount" :icon="AlertTriangle" tone="warning" />
    </div>

    <div class="grid lg:grid-cols-2 gap-6 mb-6">
      <BaseCard>
        <h3 class="font-headline font-semibold text-neutral-900 mb-4">OJT Status Breakdown</h3>
        <div class="space-y-4">
          <div v-for="s in statusBreakdown" :key="s.label">
            <div class="flex items-center justify-between text-sm mb-1.5">
              <span class="text-neutral-600">{{ s.label }}</span>
              <span class="font-medium text-neutral-800">{{ s.count }}</span>
            </div>
            <ProgressBar :value="(s.count / interns.length) * 100" />
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <h3 class="font-headline font-semibold text-neutral-900 mb-1">Total Hours Rendered</h3>
        <p class="text-sm text-neutral-500 mb-4">Across all OJT trainees this term</p>
        <p class="font-headline text-4xl font-bold text-neutral-900">{{ totalHours.toLocaleString() }}h</p>
        <p class="text-sm text-neutral-500 mt-2">≈ {{ Math.round(totalHours / (interns.length || 1)) }}h average per trainee</p>
      </BaseCard>
    </div>

    <BaseCard :padded="false" class="overflow-hidden">
      <div class="px-5 py-4 border-b border-neutral-100">
        <h3 class="font-headline font-semibold text-neutral-900">OJT Trainee Progress Detail</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-neutral-50 text-neutral-500 text-xs uppercase"><tr>
            <th class="text-left font-medium px-5 py-3">OJT Trainee</th>
            <th class="text-left font-medium px-5 py-3">Status</th>
            <th class="text-left font-medium px-5 py-3">Rendered / Required</th>
            <th class="text-left font-medium px-5 py-3 w-40">Progress</th>
          </tr></thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="i in interns" :key="i.id">
              <td class="px-5 py-3 font-medium text-neutral-800">{{ i.name }}</td>
              <td class="px-5 py-3"><StatusBadge :status="i.internshipStatus" size="sm" /></td>
              <td class="px-5 py-3 text-neutral-600">{{ i.renderedHours }}h / {{ i.requiredHours }}h</td>
              <td class="px-5 py-3"><ProgressBar :value="Math.round((i.renderedHours / i.requiredHours) * 100)" size="sm" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>
  </div>
</template>
