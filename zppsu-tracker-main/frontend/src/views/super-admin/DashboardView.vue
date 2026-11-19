<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Building2, Users, ShieldCheck, MapPinned, UserCheck, ArrowRight } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import PageHeader from '../../components/ui/PageHeader.vue'
import StatCard from '../../components/ui/StatCard.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const data = useDataStore()
const router = useRouter()

const totalInterns = computed(() => data.overview?.totalInterns ?? 0)
const totalAdmins = computed(() => data.overview?.adminAccounts ?? 0)
const activeOrgs = computed(() => data.overview?.activeOrganizations ?? 0)
const todayAttendance = computed(() => data.overview?.todayAttendance ?? 0)

const recentAudit = computed(() => data.auditLogs.slice(0, 8))
</script>

<template>
  <div>
    <PageHeader title="System Overview" subtitle="Monitor all organizations and platform-wide activity.">
      <template #actions>
        <BaseButton v-if="data.pendingApplications.length" variant="secondary" @click="router.push('/super-admin/applications')"><UserCheck class="w-4 h-4" /> {{ data.pendingApplications.length }} pending applications</BaseButton>
        <BaseButton @click="router.push('/super-admin/organizations')"><Building2 class="w-4 h-4" /> Manage Organizations</BaseButton>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="Organizations" :value="data.organizations.length" :icon="Building2" tone="primary" :trend="`${activeOrgs} active`" />
      <StatCard label="Total OJT Trainees" :value="totalInterns" :icon="Users" tone="secondary" />
      <StatCard label="Admin Accounts" :value="totalAdmins" :icon="ShieldCheck" tone="tertiary" />
      <StatCard label="Today's Attendance" :value="todayAttendance" :icon="MapPinned" tone="success" />
    </div>

    <div class="grid lg:grid-cols-3 gap-6 mt-6">
      <BaseCard class="lg:col-span-2">
        <div class="flex items-center justify-between mb-1">
          <h3 class="font-headline font-semibold text-neutral-900">Organizations</h3>
          <RouterLink to="/super-admin/organizations" class="text-sm text-primary-600 font-medium hover:underline">View all</RouterLink>
        </div>
        <div class="divide-y divide-neutral-100 mt-2">
          <div v-for="o in data.organizations" :key="o.id" class="py-3 flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-neutral-800 truncate">{{ o.name }}</p>
              <p class="text-xs text-neutral-500 truncate">{{ o.address }} · {{ o.interns }} OJT {{ o.interns === 1 ? 'trainee' : 'trainees' }} · {{ o.admins }} {{ o.admins === 1 ? 'admin' : 'admins' }}</p>
            </div>
            <StatusBadge :status="o.status" size="sm" />
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <h3 class="font-headline font-semibold text-neutral-900 mb-3">Quick Links</h3>
        <div class="space-y-2">
          <button class="w-full flex items-center justify-between text-left px-3 py-2.5 rounded-lg hover:bg-neutral-50 cursor-pointer" @click="router.push('/super-admin/admins')">
            <span class="text-sm text-neutral-700">Manage Admin Accounts</span> <ArrowRight class="w-3.5 h-3.5 text-neutral-400" />
          </button>
          <button class="w-full flex items-center justify-between text-left px-3 py-2.5 rounded-lg hover:bg-neutral-50 cursor-pointer" @click="router.push('/super-admin/audit-logs')">
            <span class="text-sm text-neutral-700">View Audit Logs</span> <ArrowRight class="w-3.5 h-3.5 text-neutral-400" />
          </button>
          <button class="w-full flex items-center justify-between text-left px-3 py-2.5 rounded-lg hover:bg-neutral-50 cursor-pointer" @click="router.push('/super-admin/reports')">
            <span class="text-sm text-neutral-700">System-wide Reports</span> <ArrowRight class="w-3.5 h-3.5 text-neutral-400" />
          </button>
        </div>
      </BaseCard>
    </div>

    <BaseCard class="mt-6">
      <h3 class="font-headline font-semibold text-neutral-900 mb-3">Recent Audit Activity</h3>
      <div class="divide-y divide-neutral-100">
        <div v-for="log in recentAudit" :key="log.id" class="py-2.5 flex items-center justify-between gap-3 text-sm">
          <div class="min-w-0">
            <span class="text-neutral-700 font-medium">{{ log.user }}</span>
            <span class="text-neutral-500"> {{ log.action.toLowerCase() }} — {{ log.resource }}</span>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <StatusBadge :status="log.result" size="sm" />
            <span class="text-xs text-neutral-400 font-label">{{ log.timestamp }}</span>
          </div>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
