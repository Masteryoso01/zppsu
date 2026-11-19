<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Mail, Phone, IdCard, School, BookOpen, MapPin as MapPinIcon } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import ProgressBar from '../../components/ui/ProgressBar.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const data = useDataStore()

const intern = computed(() => data.interns.find((i) => i.id === route.params.id))
const attendance = computed(() => data.internAttendance(intern.value.id))
const logs = computed(() => data.internLogs(intern.value.id))
const evaluations = computed(() => data.internEvaluations(intern.value.id))

const tabs = ['Overview', 'Attendance', 'Daily Logs', 'Evaluation']
const activeTab = ref('Overview')
</script>

<template>
  <div v-if="intern">
    <button class="flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-700 mb-4 cursor-pointer" @click="router.push('/admin/interns')">
      <ArrowLeft class="w-4 h-4" /> Back to OJT Trainees
    </button>

    <div class="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
      <div class="w-16 h-16 rounded-full bg-primary-600 text-white flex items-center justify-center text-xl font-semibold shrink-0">
        {{ intern.name.split(' ').map(n => n[0]).slice(0,2).join('') }}
      </div>
      <div class="min-w-0 flex-1">
        <h1 class="font-headline text-2xl font-semibold text-neutral-900">{{ intern.name }}</h1>
        <p class="text-sm text-neutral-500">{{ intern.course }} · {{ intern.school }}</p>
      </div>
      <div class="flex items-center gap-2">
        <StatusBadge :status="intern.applicationStatus" />
        <StatusBadge :status="intern.internshipStatus" />
      </div>
    </div>

    <div class="flex items-center gap-1 border-b border-neutral-200 mb-6 overflow-x-auto scrollbar-thin">
      <button
        v-for="t in tabs" :key="t"
        class="px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 -mb-px cursor-pointer transition-colors"
        :class="activeTab === t ? 'border-primary-600 text-primary-700' : 'border-transparent text-neutral-500 hover:text-neutral-700'"
        @click="activeTab = t"
      >{{ t }}</button>
    </div>

    <div v-if="activeTab === 'Overview'" class="grid lg:grid-cols-3 gap-6">
      <BaseCard class="lg:col-span-2">
        <h3 class="font-headline font-semibold text-neutral-900 mb-4">Details</h3>
        <div class="grid sm:grid-cols-2 gap-5 text-sm">
          <div class="flex items-center gap-2.5"><Mail class="w-4 h-4 text-neutral-400" /> {{ intern.email }}</div>
          <div class="flex items-center gap-2.5"><Phone class="w-4 h-4 text-neutral-400" /> {{ intern.contact }}</div>
          <div class="flex items-center gap-2.5"><IdCard class="w-4 h-4 text-neutral-400" /> {{ intern.studentId }}</div>
          <div class="flex items-center gap-2.5"><School class="w-4 h-4 text-neutral-400" /> {{ intern.school }}</div>
          <div class="flex items-center gap-2.5"><BookOpen class="w-4 h-4 text-neutral-400" /> {{ intern.course }} · {{ intern.yearLevel }}</div>
          <div class="flex items-center gap-2.5"><MapPinIcon class="w-4 h-4 text-neutral-400" /> {{ intern.address }}</div>
        </div>
      </BaseCard>
      <BaseCard>
        <h3 class="font-headline font-semibold text-neutral-900 mb-3">Progress</h3>
        <p class="font-headline text-3xl font-semibold text-neutral-900">{{ Math.round((intern.renderedHours / intern.requiredHours) * 100) }}%</p>
        <p class="text-sm text-neutral-500 mb-3">{{ intern.renderedHours }}h / {{ intern.requiredHours }}h</p>
        <ProgressBar :value="Math.round((intern.renderedHours / intern.requiredHours) * 100)" />
        <div class="mt-4 text-sm text-neutral-500">
          <p>{{ intern.startDate || 'TBD' }} → {{ intern.endDate || 'TBD' }}</p>
          <p class="mt-1">Biometric: <StatusBadge :status="intern.faceStatus" size="sm" /></p>
        </div>
      </BaseCard>
    </div>

    <div v-else-if="activeTab === 'Attendance'">
      <EmptyState v-if="!attendance.length" title="No attendance records" />
      <BaseCard v-else :padded="false" class="overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-neutral-50 text-neutral-500 text-xs uppercase"><tr>
            <th class="text-left font-medium px-5 py-3">Type</th>
            <th class="text-left font-medium px-5 py-3">Timestamp</th>
            <th class="text-left font-medium px-5 py-3">Distance</th>
            <th class="text-left font-medium px-5 py-3">Status</th>
          </tr></thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="a in attendance" :key="a.id">
              <td class="px-5 py-3">{{ a.type }}</td>
              <td class="px-5 py-3 font-label text-neutral-500">{{ a.timestamp }}</td>
              <td class="px-5 py-3">{{ a.distance }}m</td>
              <td class="px-5 py-3"><StatusBadge :status="a.status" size="sm" /></td>
            </tr>
          </tbody>
        </table>
      </BaseCard>
    </div>

    <div v-else-if="activeTab === 'Daily Logs'">
      <EmptyState v-if="!logs.length" title="No daily logs submitted" />
      <div v-else class="space-y-3">
        <BaseCard v-for="log in logs" :key="log.id">
          <div class="flex items-center justify-between mb-2">
            <p class="font-medium text-neutral-800">{{ log.date }}</p>
            <StatusBadge :status="log.status" size="sm" />
          </div>
          <p class="text-sm text-neutral-600">{{ log.activities }}</p>
        </BaseCard>
      </div>
    </div>

    <div v-else-if="activeTab === 'Evaluation'">
      <EmptyState v-if="!evaluations.length" title="No evaluations yet" />
      <BaseCard v-for="ev in evaluations" :key="ev.id">
        <div class="flex items-center justify-between mb-3">
          <p class="font-medium text-neutral-800">{{ ev.period }} Evaluation</p>
          <span class="font-headline font-semibold text-secondary-600">{{ ev.rating.toFixed(1) }} / 5.0</span>
        </div>
        <p class="text-sm text-neutral-600">{{ ev.comments }}</p>
      </BaseCard>
    </div>
  </div>
  <EmptyState v-else title="OJT trainee not found" />
</template>
