<script setup>
import { computed } from 'vue'
import { Building2, Users, Clock, TrendingUp } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import PageHeader from '../../components/ui/PageHeader.vue'
import StatCard from '../../components/ui/StatCard.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import ProgressBar from '../../components/ui/ProgressBar.vue'

const data = useDataStore()

const totalInterns = computed(() => data.organizations.reduce((s, o) => s + o.interns, 0))
const totalHours = computed(() => data.interns.reduce((s, i) => s + i.renderedHours, 0))
const avgHours = computed(() => Math.round(totalHours.value / (data.interns.length || 1)))

const orgBreakdown = computed(() => {
  const max = Math.max(...data.organizations.map((o) => o.interns), 1)
  return data.organizations.map((o) => ({ ...o, pct: Math.round((o.interns / max) * 100) }))
})
</script>

<template>
  <div>
    <PageHeader title="System Reports" subtitle="Platform-wide statistics across all organizations." />

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard label="Organizations" :value="data.organizations.length" :icon="Building2" tone="primary" />
      <StatCard label="Total OJT Trainees" :value="totalInterns" :icon="Users" tone="secondary" />
      <StatCard label="Total Hours Logged" :value="totalHours.toLocaleString()" :icon="Clock" tone="tertiary" />
      <StatCard label="Avg Hours / Trainee" :value="avgHours" :icon="TrendingUp" tone="success" />
    </div>

    <BaseCard>
      <h3 class="font-headline font-semibold text-neutral-900 mb-4">OJT Trainees by Organization</h3>
      <div class="space-y-4">
        <div v-for="o in orgBreakdown" :key="o.id">
          <div class="flex items-center justify-between text-sm mb-1.5">
            <span class="text-neutral-600">{{ o.name }}</span>
            <span class="font-medium text-neutral-800">{{ o.interns }}</span>
          </div>
          <ProgressBar :value="o.pct" />
        </div>
      </div>
    </BaseCard>
  </div>
</template>
