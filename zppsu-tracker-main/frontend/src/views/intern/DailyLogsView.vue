<script setup>
import { computed, reactive, ref } from 'vue'
import { Plus, MessageSquare, ClipboardList } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseModal from '../../components/ui/BaseModal.vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import BaseTextarea from '../../components/ui/BaseTextarea.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const ui = useUiStore()
const intern = computed(() => data.currentIntern)
const logs = computed(() => data.internLogs(intern.value.id))

const modalOpen = ref(false)
const form = reactive({ date: new Date().toISOString().slice(0, 10), activities: '', learnings: '', challenges: '' })

function openNew() {
  form.date = new Date().toISOString().slice(0, 10)
  form.activities = ''
  form.learnings = ''
  form.challenges = ''
  modalOpen.value = true
}

async function submit() {
  if (!form.activities) return
  try {
    await data.submitDailyLog({ ...form })
    modalOpen.value = false
    ui.toast('Daily log submitted for review.')
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
</script>

<template>
  <div>
    <PageHeader title="Daily Logs" subtitle="Record your daily activities, learnings, and challenges.">
      <template #actions>
        <BaseButton @click="openNew"><Plus class="w-4 h-4" /> New Log</BaseButton>
      </template>
    </PageHeader>

    <EmptyState v-if="!logs.length" :icon="ClipboardList" title="No daily logs yet" description="Submit your first daily log to start tracking your progress.">
      <template #action>
        <BaseButton size="sm" @click="openNew"><Plus class="w-4 h-4" /> New Log</BaseButton>
      </template>
    </EmptyState>

    <div v-else class="space-y-4">
      <BaseCard v-for="log in logs" :key="log.id">
        <div class="flex items-start justify-between gap-3 mb-3">
          <p class="font-headline font-semibold text-neutral-900">{{ log.date }}</p>
          <StatusBadge :status="log.status" size="sm" />
        </div>
        <div class="grid sm:grid-cols-3 gap-4 text-sm">
          <div>
            <p class="text-xs text-neutral-400 mb-1">Activities</p>
            <p class="text-neutral-700">{{ log.activities }}</p>
          </div>
          <div>
            <p class="text-xs text-neutral-400 mb-1">Learnings</p>
            <p class="text-neutral-700">{{ log.learnings }}</p>
          </div>
          <div>
            <p class="text-xs text-neutral-400 mb-1">Challenges</p>
            <p class="text-neutral-700">{{ log.challenges }}</p>
          </div>
        </div>
        <div v-if="log.reviewerComment" class="mt-3 pt-3 border-t border-neutral-100 flex items-start gap-2">
          <MessageSquare class="w-3.5 h-3.5 text-neutral-400 shrink-0 mt-0.5" />
          <p class="text-xs text-neutral-500"><span class="font-medium text-neutral-600">Reviewer:</span> {{ log.reviewerComment }}</p>
        </div>
      </BaseCard>
    </div>

    <BaseModal v-model="modalOpen" title="New Daily Log">
      <form class="space-y-4" @submit.prevent="submit">
        <BaseInput v-model="form.date" type="date" label="Date" required />
        <BaseTextarea v-model="form.activities" label="Activities" placeholder="What did you work on today?" required />
        <BaseTextarea v-model="form.learnings" label="Learnings" placeholder="What did you learn?" :rows="3" />
        <BaseTextarea v-model="form.challenges" label="Challenges" placeholder="Any blockers or difficulties?" :rows="3" />
        <BaseButton type="submit" block>Submit Log</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>
