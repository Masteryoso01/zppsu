<script setup>
import { computed } from 'vue'
import { Star, Hourglass } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import ProgressBar from '../../components/ui/ProgressBar.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const intern = computed(() => data.currentIntern)
const evaluations = computed(() => data.internEvaluations(intern.value.id).filter((e) => e.status === 'Released'))
</script>

<template>
  <div>
    <PageHeader title="Evaluation" subtitle="Performance evaluations released by your organization." />

    <EmptyState v-if="!evaluations.length" :icon="Hourglass" title="No evaluations released yet" description="Your supervisor's evaluation will appear here once released." />

    <div v-else class="space-y-6">
      <BaseCard v-for="ev in evaluations" :key="ev.id">
        <div class="flex items-start justify-between mb-5">
          <div>
            <h3 class="font-headline font-semibold text-lg text-neutral-900">{{ ev.period }} Evaluation</h3>
            <p class="text-sm text-neutral-500 mt-0.5">By {{ ev.evaluatorName }} · {{ ev.createdAt }}</p>
          </div>
          <div class="flex items-center gap-1 bg-secondary-50 text-secondary-700 rounded-lg px-3 py-1.5">
            <Star class="w-4 h-4 fill-current" />
            <span class="font-headline font-semibold">{{ ev.rating.toFixed(1) }}</span>
          </div>
        </div>

        <div class="space-y-4">
          <div v-for="c in ev.criteria" :key="c.label">
            <div class="flex items-center justify-between text-sm mb-1.5">
              <span class="text-neutral-600">{{ c.label }}</span>
              <span class="font-medium text-neutral-800">{{ c.score.toFixed(1) }} / 5.0</span>
            </div>
            <ProgressBar :value="(c.score / 5) * 100" tone="secondary" size="sm" />
          </div>
        </div>

        <div class="mt-5 pt-5 border-t border-neutral-100">
          <p class="text-xs text-neutral-400 mb-1.5">Comments</p>
          <p class="text-sm text-neutral-700 leading-relaxed">{{ ev.comments }}</p>
        </div>
      </BaseCard>
    </div>
  </div>
</template>
