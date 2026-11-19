<script setup>
import { computed, reactive, ref } from 'vue'
import { Star, Plus, Send } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseModal from '../../components/ui/BaseModal.vue'
import BaseSelect from '../../components/ui/BaseSelect.vue'
import BaseTextarea from '../../components/ui/BaseTextarea.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const auth = useAuthStore()
const ui = useUiStore()

const orgInterns = computed(() => data.orgInterns(auth.user.orgId).filter((i) => i.internshipStatus !== 'Not Started'))
function internName(id) { return data.interns.find((i) => i.id === id)?.name || id }

const evaluations = computed(() => data.evaluations.filter((e) => orgInterns.value.some((i) => i.id === e.internId)))

const modalOpen = ref(false)
const criteriaLabels = ['Technical Skills', 'Work Attitude', 'Communication', 'Punctuality', 'Initiative']
const form = reactive({
  internId: '', period: 'Midterm', comments: '',
  scores: Object.fromEntries(criteriaLabels.map((l) => [l, 4])),
})

function openNew() {
  form.internId = ''
  form.period = 'Midterm'
  form.comments = ''
  criteriaLabels.forEach((l) => (form.scores[l] = 4))
  modalOpen.value = true
}

async function submit() {
  if (!form.internId) return
  const criteria = criteriaLabels.map((label) => ({ label, score: Number(form.scores[label]) }))
  try {
    await data.addEvaluation({ internId: form.internId, period: form.period, comments: form.comments, criteria, status: 'Released' })
    ui.toast('Evaluation released to OJT trainee.')
    modalOpen.value = false
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
</script>

<template>
  <div>
    <PageHeader title="Evaluations" subtitle="Evaluate trainee performance and release results.">
      <template #actions>
        <BaseButton @click="openNew"><Plus class="w-4 h-4" /> New Evaluation</BaseButton>
      </template>
    </PageHeader>

    <EmptyState v-if="!evaluations.length" :icon="Star" title="No evaluations yet" />

    <div v-else class="grid gap-4">
      <BaseCard v-for="ev in evaluations" :key="ev.id">
        <div class="flex items-center justify-between mb-3">
          <div>
            <p class="font-medium text-neutral-800">{{ internName(ev.internId) }}</p>
            <p class="text-xs text-neutral-500">{{ ev.period }} · {{ ev.createdAt }}</p>
          </div>
          <div class="flex items-center gap-2">
            <div class="flex items-center gap-1 bg-secondary-50 text-secondary-700 rounded-lg px-2.5 py-1">
              <Star class="w-3.5 h-3.5 fill-current" /> <span class="font-semibold text-sm">{{ ev.rating.toFixed(1) }}</span>
            </div>
            <StatusBadge :status="ev.status" size="sm" />
          </div>
        </div>
        <p class="text-sm text-neutral-600">{{ ev.comments }}</p>
      </BaseCard>
    </div>

    <BaseModal v-model="modalOpen" title="New Evaluation" size="md">
      <form class="space-y-4" @submit.prevent="submit">
        <BaseSelect v-model="form.internId" label="OJT Trainee" :options="orgInterns.map(i => ({ label: i.name, value: i.id }))" required />
        <BaseSelect v-model="form.period" label="Period" :options="[{label:'Midterm',value:'Midterm'},{label:'Final',value:'Final'}]" required />

        <div>
          <p class="text-sm font-medium text-neutral-700 mb-2">Ratings</p>
          <div class="space-y-3">
            <div v-for="label in criteriaLabels" :key="label" class="flex items-center justify-between gap-3">
              <span class="text-sm text-neutral-600">{{ label }}</span>
              <input v-model.number="form.scores[label]" type="range" min="1" max="5" step="0.5" class="w-40 accent-primary-600" />
              <span class="text-sm font-medium text-neutral-800 w-8 text-right">{{ form.scores[label] }}</span>
            </div>
          </div>
        </div>

        <BaseTextarea v-model="form.comments" label="Comments" placeholder="Overall performance feedback..." required />

        <BaseButton type="submit" block><Send class="w-4 h-4" /> Release Evaluation</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>
