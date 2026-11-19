<script setup>
import { computed, ref } from 'vue'
import { Check, X, Eye, UserCheck, Building2 } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseModal from '../../components/ui/BaseModal.vue'
import BaseSelect from '../../components/ui/BaseSelect.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import EmptyState from '../../components/ui/EmptyState.vue'

const data = useDataStore()
const auth = useAuthStore()
const ui = useUiStore()

const filter = ref('Pending')
const filters = ['Pending', 'Approved', 'Rejected', 'All']

const filtered = computed(() => data.interns.filter((i) => filter.value === 'All' || i.applicationStatus === filter.value))
const orgOptions = computed(() => data.organizations.filter((o) => o.status === 'Active').map((o) => ({ label: o.name, value: o.id })))
const orgName = (id) => data.organizations.find((o) => o.id === id)?.name || 'Unassigned'

const detailOpen = ref(false)
const activeIntern = ref(null)
const targetOrg = ref('')
function viewDetail(i) {
  activeIntern.value = i
  targetOrg.value = i.orgId || ''
  detailOpen.value = true
}

async function run(task, successMessage, tone = 'success') {
  try {
    await task()
    ui.toast(successMessage, tone)
    detailOpen.value = false
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}

function approve(i) {
  if (!targetOrg.value) return ui.toast('Select an organization to deploy to first.', 'danger')
  return run(() => data.approveApplication(i.id, targetOrg.value), `${i.name} approved and deployed to ${orgName(targetOrg.value)}.`)
}
function reassign(i) {
  if (!targetOrg.value || targetOrg.value === i.orgId) return
  return run(() => data.deployIntern(i.id, targetOrg.value), `${i.name} redeployed to ${orgName(targetOrg.value)}.`)
}
function reject(i) {
  return run(() => data.rejectApplication(i.id), `${i.name}'s application rejected.`, 'danger')
}
</script>

<template>
  <div>
    <PageHeader title="Applications" subtitle="Approve OJT applicants and deploy them to their designated organization." />

    <div class="flex items-center gap-2 mb-5">
      <button
        v-for="f in filters" :key="f"
        class="px-3.5 py-1.5 rounded-lg text-sm font-medium cursor-pointer transition-colors"
        :class="filter === f ? 'bg-primary-600 text-white' : 'bg-white border border-neutral-200 text-neutral-600 hover:bg-neutral-50'"
        @click="filter = f"
      >{{ f }}</button>
    </div>

    <EmptyState v-if="!filtered.length" :icon="UserCheck" title="No applications in this filter" />

    <div v-else class="grid gap-4">
      <BaseCard v-for="i in filtered" :key="i.id" hover>
        <div class="flex items-center justify-between gap-4 flex-col sm:flex-row">
          <div class="flex items-center gap-3 min-w-0 w-full sm:w-auto">
            <div class="w-11 h-11 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold shrink-0">
              {{ i.name.split(' ').map(n => n[0]).slice(0,2).join('') }}
            </div>
            <div class="min-w-0">
              <p class="font-medium text-neutral-800 truncate">{{ i.name }}</p>
              <p class="text-sm text-neutral-500 truncate">{{ i.course }} · {{ i.yearLevel }} · {{ i.studentId }}</p>
              <p class="text-xs text-neutral-400 truncate flex items-center gap-1 mt-0.5"><Building2 class="w-3 h-3 shrink-0" /> {{ orgName(i.orgId) }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0 self-end sm:self-auto">
            <StatusBadge :status="i.applicationStatus" />
            <BaseButton size="sm" variant="ghost" @click="viewDetail(i)"><Eye class="w-3.5 h-3.5" /> View</BaseButton>
            <template v-if="i.applicationStatus === 'Pending'">
              <BaseButton size="sm" variant="danger" @click="reject(i)"><X class="w-3.5 h-3.5" /></BaseButton>
              <BaseButton size="sm" @click="viewDetail(i)"><Check class="w-3.5 h-3.5" /> Approve &amp; Deploy</BaseButton>
            </template>
          </div>
        </div>
      </BaseCard>
    </div>

    <BaseModal v-model="detailOpen" :title="activeIntern?.name" size="md">
      <div v-if="activeIntern" class="space-y-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div><p class="text-xs text-neutral-400">Email</p><p class="text-neutral-800 mt-0.5 truncate">{{ activeIntern.email }}</p></div>
          <div><p class="text-xs text-neutral-400">Student ID</p><p class="text-neutral-800 mt-0.5">{{ activeIntern.studentId }}</p></div>
          <div><p class="text-xs text-neutral-400">School</p><p class="text-neutral-800 mt-0.5">{{ activeIntern.school }}</p></div>
          <div><p class="text-xs text-neutral-400">Course</p><p class="text-neutral-800 mt-0.5">{{ activeIntern.course }}</p></div>
          <div><p class="text-xs text-neutral-400">Year Level</p><p class="text-neutral-800 mt-0.5">{{ activeIntern.yearLevel }}</p></div>
          <div><p class="text-xs text-neutral-400">Contact</p><p class="text-neutral-800 mt-0.5">{{ activeIntern.contact }}</p></div>
        </div>

        <div v-if="activeIntern.applicationStatus !== 'Rejected'" class="pt-3 border-t border-neutral-100 space-y-3">
          <BaseSelect v-model="targetOrg" label="Deploy to organization" :options="orgOptions" required />
          <div v-if="activeIntern.applicationStatus === 'Pending'" class="flex items-center gap-2">
            <BaseButton block variant="danger" @click="reject(activeIntern)"><X class="w-4 h-4" /> Reject</BaseButton>
            <BaseButton block @click="approve(activeIntern)"><Check class="w-4 h-4" /> Approve &amp; Deploy</BaseButton>
          </div>
          <BaseButton v-else block :disabled="!targetOrg || targetOrg === activeIntern.orgId" @click="reassign(activeIntern)"><Building2 class="w-4 h-4" /> Redeploy</BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>
