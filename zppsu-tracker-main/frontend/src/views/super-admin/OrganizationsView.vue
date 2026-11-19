<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Building2, MapPin, Users, ShieldCheck, Ban, CheckCircle2 } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseModal from '../../components/ui/BaseModal.vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const data = useDataStore()
const ui = useUiStore()
const router = useRouter()

const modalOpen = ref(false)
const form = reactive({ name: '', address: '' })

function openNew() {
  form.name = ''
  form.address = ''
  modalOpen.value = true
}
async function save() {
  if (!form.name) return
  try {
    await data.addOrganization({ name: form.name, address: form.address })
    ui.toast('Organization created.')
    modalOpen.value = false
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
async function toggleStatus(org) {
  const next = org.status === 'Active' ? 'Suspended' : 'Active'
  try {
    await data.updateOrganization(org.id, { status: next })
    ui.toast(`${org.name} ${next === 'Active' ? 'reactivated' : 'suspended'}.`, next === 'Active' ? 'success' : 'danger')
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
</script>

<template>
  <div>
    <PageHeader title="Organizations" subtitle="Manage organizations on the GeoTrack platform.">
      <template #actions>
        <BaseButton @click="openNew"><Plus class="w-4 h-4" /> Add Organization</BaseButton>
      </template>
    </PageHeader>

    <div class="grid gap-4">
      <BaseCard v-for="org in data.organizations" :key="org.id" hover class="cursor-pointer" @click="router.push(`/super-admin/organizations/${org.id}`)">
        <div class="flex items-start justify-between gap-4 flex-col sm:flex-row">
          <div class="flex items-start gap-3 min-w-0">
            <div class="w-11 h-11 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
              <Building2 class="w-5 h-5 text-primary-600" />
            </div>
            <div class="min-w-0">
              <p class="font-medium text-neutral-800">{{ org.name }}</p>
              <p class="text-sm text-neutral-500 flex items-center gap-1.5 mt-0.5"><MapPin class="w-3.5 h-3.5" /> {{ org.address }}</p>
              <div class="flex items-center gap-4 mt-2 text-xs text-neutral-500">
                <span class="flex items-center gap-1"><Users class="w-3.5 h-3.5" /> {{ org.interns }} OJT {{ org.interns === 1 ? 'trainee' : 'trainees' }}</span>
                <span class="flex items-center gap-1"><ShieldCheck class="w-3.5 h-3.5" /> {{ org.admins }} {{ org.admins === 1 ? 'admin' : 'admins' }}</span>
                <span class="font-label">Since {{ org.createdAt }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0 self-end sm:self-auto">
            <StatusBadge :status="org.status" />
            <BaseButton size="sm" variant="outline" @click.stop="router.push(`/super-admin/organizations/${org.id}`)"><Users class="w-3.5 h-3.5" /> View trainees</BaseButton>
            <BaseButton size="sm" :variant="org.status === 'Active' ? 'danger' : 'secondary'" @click.stop="toggleStatus(org)">
              <Ban v-if="org.status === 'Active'" class="w-3.5 h-3.5" />
              <CheckCircle2 v-else class="w-3.5 h-3.5" />
              {{ org.status === 'Active' ? 'Suspend' : 'Reactivate' }}
            </BaseButton>
          </div>
        </div>
      </BaseCard>
    </div>

    <BaseModal v-model="modalOpen" title="Add Organization" size="sm">
      <form class="space-y-4" @submit.prevent="save">
        <BaseInput v-model="form.name" label="Organization name" placeholder="Northbridge Institute of Technology" required />
        <BaseInput v-model="form.address" label="Address" placeholder="Quezon City, Metro Manila" required />
        <BaseButton type="submit" block>Create Organization</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>
