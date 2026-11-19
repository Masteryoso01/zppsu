<script setup>
import { computed, ref } from 'vue'
import { Search, ScrollText } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const q = ref('')

const logs = computed(() => {
  if (!q.value) return data.auditLogs
  const s = q.value.toLowerCase()
  return data.auditLogs.filter((l) => l.user.toLowerCase().includes(s) || l.action.toLowerCase().includes(s) || l.resource.toLowerCase().includes(s))
})
</script>

<template>
  <div>
    <PageHeader title="Audit Logs" subtitle="System-wide security and administrative event log." />

    <BaseInput v-model="q" placeholder="Search by user, action, or resource..." :icon="Search" class="mb-5 max-w-md" />

    <EmptyState v-if="!logs.length" :icon="ScrollText" title="No matching audit events" />
    <BaseCard v-else :padded="false" class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-neutral-50 text-neutral-500 text-xs uppercase"><tr>
            <th class="text-left font-medium px-5 py-3">Timestamp</th>
            <th class="text-left font-medium px-5 py-3">User</th>
            <th class="text-left font-medium px-5 py-3">Action</th>
            <th class="text-left font-medium px-5 py-3">Resource</th>
            <th class="text-left font-medium px-5 py-3">Result</th>
          </tr></thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-neutral-50">
              <td class="px-5 py-3 font-label text-neutral-500 whitespace-nowrap">{{ log.timestamp }}</td>
              <td class="px-5 py-3 font-medium text-neutral-800 whitespace-nowrap">{{ log.user }}</td>
              <td class="px-5 py-3 text-neutral-600">{{ log.action }}</td>
              <td class="px-5 py-3 text-neutral-500">{{ log.resource }}</td>
              <td class="px-5 py-3"><StatusBadge :status="log.result" size="sm" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>
  </div>
</template>
