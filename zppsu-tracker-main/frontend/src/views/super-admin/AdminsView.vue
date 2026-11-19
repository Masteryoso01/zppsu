<script setup>
import { computed, reactive, ref } from 'vue'
import { Plus, ShieldCheck } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseModal from '../../components/ui/BaseModal.vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import BaseSelect from '../../components/ui/BaseSelect.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const data = useDataStore()
const ui = useUiStore()

function orgName(id) { return data.organizations.find((o) => o.id === id)?.name || '—' }

const modalOpen = ref(false)
const form = reactive({ name: '', email: '', orgId: '', password: '' })

function openNew() {
  form.name = ''
  form.email = ''
  form.orgId = ''
  form.password = ''
  modalOpen.value = true
}
async function save() {
  if (!form.name || !form.orgId || !form.email || !form.password) return
  try {
    await data.addAdmin({ name: form.name, email: form.email, orgId: form.orgId, password: form.password })
    ui.toast('Admin account created.')
    modalOpen.value = false
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
</script>

<template>
  <div>
    <PageHeader title="Admin Accounts" subtitle="Manage organization admin accounts across the platform.">
      <template #actions>
        <BaseButton @click="openNew"><Plus class="w-4 h-4" /> Add Admin</BaseButton>
      </template>
    </PageHeader>

    <BaseCard :padded="false" class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-neutral-50 text-neutral-500 text-xs uppercase"><tr>
            <th class="text-left font-medium px-5 py-3">Admin</th>
            <th class="text-left font-medium px-5 py-3">Organization</th>
            <th class="text-left font-medium px-5 py-3">Status</th>
            <th class="text-left font-medium px-5 py-3">Last Login</th>
          </tr></thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="a in data.admins" :key="a.id" class="hover:bg-neutral-50">
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-full bg-tertiary-800 text-white flex items-center justify-center text-xs font-semibold shrink-0">
                    <ShieldCheck class="w-4 h-4" />
                  </div>
                  <div class="min-w-0">
                    <p class="font-medium text-neutral-800 truncate">{{ a.name }}</p>
                    <p class="text-xs text-neutral-500 truncate">{{ a.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-3.5 text-neutral-600">{{ orgName(a.orgId) }}</td>
              <td class="px-5 py-3.5"><StatusBadge :status="a.status" size="sm" /></td>
              <td class="px-5 py-3.5 text-neutral-500 font-label">{{ a.lastLogin }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <BaseModal v-model="modalOpen" title="Add Admin Account" size="sm">
      <form class="space-y-4" @submit.prevent="save">
        <BaseInput v-model="form.name" label="Full name" required />
        <BaseInput v-model="form.email" type="email" label="Email address" required />
        <BaseInput v-model="form.password" type="password" label="Temporary password" hint="At least 8 characters. Share it with the admin securely." required />
        <BaseSelect v-model="form.orgId" label="Organization" :options="data.organizations.map(o => ({ label: o.name, value: o.id }))" required />
        <BaseButton type="submit" block>Create Admin</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>
