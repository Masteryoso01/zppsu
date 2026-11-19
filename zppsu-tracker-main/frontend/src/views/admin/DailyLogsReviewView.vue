<script setup>
import { computed, ref } from 'vue'
import { Check, X, ClipboardList, MessageSquare } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseModal from '../../components/ui/BaseModal.vue'
import BaseTextarea from '../../components/ui/BaseTextarea.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const auth = useAuthStore()
const ui = useUiStore()

const filter = ref('Pending')
const filters = ['Pending', 'Approved', 'Rejected', 'All']

const orgInternIds = computed(() => data.orgInterns(auth.user.orgId).map((i) => i.id))
function internName(id) { return data.interns.find((i) => i.id === id)?.name || id }

const logs = computed(() => {
  let list = data.dailyLogs.filter((l) => orgInternIds.value.includes(l.internId))
  if (filter.value !== 'All') list = list.filter((l) => l.status === filter.value)
  return list
})

const rejectModal = ref(false)
const activeLog = ref(null)
const comment = ref('')

async function approve(log) {
  try {
    await data.reviewDailyLog(log.id, 'Approved', '')
    ui.toast('Daily log approved.')
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
function openReject(log) {
  activeLog.value = log
  comment.value = ''
  rejectModal.value = true
}
async function confirmReject() {
  try {
    await data.reviewDailyLog(activeLog.value.id, 'Rejected', comment.value)
    ui.toast('Daily log rejected with comment.', 'danger')
    rejectModal.value = false
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
</script>

<template>
  <div>
    <PageHeader title="Daily Logs" subtitle="Review, approve, or reject trainee daily logs." />

    <div class="flex items-center gap-2 mb-5">
      <button
        v-for="f in filters" :key="f"
        class="px-3.5 py-1.5 rounded-lg text-sm font-medium cursor-pointer transition-colors"
        :class="filter === f ? 'bg-primary-600 text-white' : 'bg-white border border-neutral-200 text-neutral-600 hover:bg-neutral-50'"
        @click="filter = f"
      >{{ f }}</button>
    </div>

    <EmptyState v-if="!logs.length" :icon="ClipboardList" title="No logs in this filter" />

    <div v-else class="space-y-4">
      <BaseCard v-for="log in logs" :key="log.id">
        <div class="flex items-start justify-between gap-3 mb-3">
          <div>
            <p class="font-medium text-neutral-800">{{ internName(log.internId) }}</p>
            <p class="text-xs text-neutral-500">{{ log.date }}</p>
          </div>
          <StatusBadge :status="log.status" size="sm" />
        </div>
        <div class="grid sm:grid-cols-3 gap-4 text-sm mb-3">
          <div><p class="text-xs text-neutral-400 mb-1">Activities</p><p class="text-neutral-700">{{ log.activities }}</p></div>
          <div><p class="text-xs text-neutral-400 mb-1">Learnings</p><p class="text-neutral-700">{{ log.learnings }}</p></div>
          <div><p class="text-xs text-neutral-400 mb-1">Challenges</p><p class="text-neutral-700">{{ log.challenges }}</p></div>
        </div>
        <div v-if="log.reviewerComment" class="flex items-start gap-2 bg-neutral-50 rounded-lg px-3 py-2 mb-3">
          <MessageSquare class="w-3.5 h-3.5 text-neutral-400 shrink-0 mt-0.5" />
          <p class="text-xs text-neutral-500">{{ log.reviewerComment }}</p>
        </div>
        <div v-if="log.status === 'Pending'" class="flex items-center gap-2">
          <BaseButton size="sm" variant="danger" @click="openReject(log)"><X class="w-3.5 h-3.5" /> Reject</BaseButton>
          <BaseButton size="sm" @click="approve(log)"><Check class="w-3.5 h-3.5" /> Approve</BaseButton>
        </div>
      </BaseCard>
    </div>

    <BaseModal v-model="rejectModal" title="Reject Daily Log" size="sm">
      <div class="space-y-4">
        <BaseTextarea v-model="comment" label="Reason for rejection" placeholder="Explain what needs to be revised..." required />
        <BaseButton block variant="danger" @click="confirmReject">Confirm Rejection</BaseButton>
      </div>
    </BaseModal>
  </div>
</template>
