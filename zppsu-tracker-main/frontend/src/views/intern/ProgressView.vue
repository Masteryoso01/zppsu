<script setup>
import { computed } from 'vue'
import { Clock, TrendingUp, CalendarCheck, Flag } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import StatCard from '../../components/ui/StatCard.vue'
import ProgressBar from '../../components/ui/ProgressBar.vue'

const data = useDataStore()
const intern = computed(() => data.currentIntern)
const progressPct = computed(() => Math.min(100, Math.round((intern.value.renderedHours / intern.value.requiredHours) * 100)))
const remaining = computed(() => Math.max(0, intern.value.requiredHours - intern.value.renderedHours))

const weeks = computed(() => {
  const attendance = data.internAttendance(intern.value.id)
  const buckets = [0, 0, 0, 0, 0, 0]
  attendance.forEach((a, i) => {
    if (a.type !== 'Time Out') return
    buckets[i % 6] += 8
  })
  return buckets.map((h, i) => ({ label: `Wk ${i + 1}`, hours: h }))
})
const maxWeekHours = computed(() => Math.max(...weeks.value.map((w) => w.hours), 40))

const circumference = 2 * Math.PI * 70
const dashOffset = computed(() => circumference - (progressPct.value / 100) * circumference)
</script>

<template>
  <div>
    <PageHeader title="Progress & Hours" subtitle="Track your rendered hours toward OJT completion." />

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <BaseCard class="flex flex-col items-center justify-center py-8">
        <svg width="180" height="180" viewBox="0 0 180 180" class="-rotate-90">
          <circle cx="90" cy="90" r="70" fill="none" stroke="currentColor" stroke-width="14" class="text-neutral-100" />
          <circle
            cx="90" cy="90" r="70" fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round"
            class="text-primary-600 transition-all duration-700"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
          />
        </svg>
        <div class="-mt-[112px] text-center">
          <p class="font-headline text-4xl font-bold text-neutral-900">{{ progressPct }}%</p>
          <p class="text-xs text-neutral-500 mt-1">Complete</p>
        </div>
        <div class="mt-16 text-center">
          <p class="text-sm text-neutral-500">{{ intern.renderedHours }}h of {{ intern.requiredHours }}h required</p>
        </div>
      </BaseCard>

      <div class="lg:col-span-2 grid grid-cols-2 gap-4 content-start">
        <StatCard label="Rendered Hours" :value="`${intern.renderedHours}h`" :icon="Clock" tone="primary" />
        <StatCard label="Remaining Hours" :value="`${remaining}h`" :icon="Flag" tone="secondary" />
        <StatCard label="OJT Status" :value="intern.internshipStatus" :icon="TrendingUp" tone="tertiary" />
        <StatCard label="Target End Date" :value="intern.endDate || 'TBD'" :icon="CalendarCheck" tone="success" />
      </div>
    </div>

    <BaseCard class="mt-6">
      <h3 class="font-headline font-semibold text-neutral-900 mb-1">Hours Rendered (last 6 weeks)</h3>
      <p class="text-sm text-neutral-500 mb-6">Approximate weekly breakdown based on completed Time Out events.</p>
      <div class="flex items-end gap-4 h-48">
        <div v-for="w in weeks" :key="w.label" class="flex-1 flex flex-col items-center gap-2 h-full justify-end">
          <span class="text-xs text-neutral-500 font-label">{{ w.hours }}h</span>
          <div class="w-full bg-primary-600 rounded-t-lg transition-all duration-500" :style="{ height: `${(w.hours / maxWeekHours) * 100}%`, minHeight: w.hours ? '4px' : '2px' }" :class="w.hours ? '' : 'bg-neutral-100'" />
          <span class="text-xs text-neutral-400">{{ w.label }}</span>
        </div>
      </div>
    </BaseCard>

    <BaseCard class="mt-6">
      <h3 class="font-headline font-semibold text-neutral-900 mb-4">Milestone Timeline</h3>
      <ProgressBar :value="progressPct" size="sm" />
      <div class="flex justify-between text-xs text-neutral-400 mt-2">
        <span>{{ intern.startDate || 'Start' }}</span>
        <span>{{ Math.round(intern.requiredHours / 2) }}h — Midpoint</span>
        <span>{{ intern.endDate || 'End' }}</span>
      </div>
    </BaseCard>
  </div>
</template>
