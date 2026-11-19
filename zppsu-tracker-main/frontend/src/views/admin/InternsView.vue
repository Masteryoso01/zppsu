<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Users, ChevronRight } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import ProgressBar from '../../components/ui/ProgressBar.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const auth = useAuthStore()
const router = useRouter()
const q = ref('')

const interns = computed(() => {
  const list = data.orgInterns(auth.user.orgId)
  if (!q.value) return list
  const s = q.value.toLowerCase()
  return list.filter((i) => i.name.toLowerCase().includes(s) || i.studentId.toLowerCase().includes(s) || i.course.toLowerCase().includes(s))
})
</script>

<template>
  <div>
    <PageHeader title="OJT Trainees" subtitle="All OJT trainees within your organization." />

    <BaseInput v-model="q" placeholder="Search by name, student ID, or course..." :icon="Search" class="mb-5 max-w-md" />

    <EmptyState v-if="!interns.length" :icon="Users" title="No OJT trainees found" />

    <BaseCard v-else :padded="false" class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-neutral-50 text-neutral-500 text-xs uppercase tracking-wide">
            <tr>
              <th class="text-left font-medium px-5 py-3">OJT Trainee</th>
              <th class="text-left font-medium px-5 py-3">Program</th>
              <th class="text-left font-medium px-5 py-3">Application</th>
              <th class="text-left font-medium px-5 py-3">Biometric</th>
              <th class="text-left font-medium px-5 py-3 w-48">Progress</th>
              <th class="w-10"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="i in interns" :key="i.id" class="hover:bg-neutral-50 cursor-pointer" @click="router.push(`/admin/interns/${i.id}`)">
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-semibold shrink-0">
                    {{ i.name.split(' ').map(n => n[0]).slice(0,2).join('') }}
                  </div>
                  <div class="min-w-0">
                    <p class="font-medium text-neutral-800 truncate">{{ i.name }}</p>
                    <p class="text-xs text-neutral-500 truncate">{{ i.studentId }}</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-3.5 text-neutral-600">{{ i.course }}</td>
              <td class="px-5 py-3.5"><StatusBadge :status="i.applicationStatus" size="sm" /></td>
              <td class="px-5 py-3.5"><StatusBadge :status="i.faceStatus" size="sm" /></td>
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-2">
                  <ProgressBar :value="Math.round((i.renderedHours / i.requiredHours) * 100)" size="sm" />
                  <span class="text-xs text-neutral-400 shrink-0">{{ Math.round((i.renderedHours / i.requiredHours) * 100) }}%</span>
                </div>
              </td>
              <td class="px-3"><ChevronRight class="w-4 h-4 text-neutral-300" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>
  </div>
</template>
