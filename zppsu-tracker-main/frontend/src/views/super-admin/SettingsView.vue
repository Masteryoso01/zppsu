<script setup>
import { reactive } from 'vue'
import { Save, ShieldCheck, Lock, MapPinned, Camera } from '@lucide/vue'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseInput from '../../components/ui/BaseInput.vue'

const ui = useUiStore()

const settings = reactive({
  requireLiveness: true,
  strictGpsAccuracy: true,
  rateLimitAttempts: 5,
  biometricRetentionDays: 365,
  documentRetentionDays: 730,
  auditLogRetentionDays: 1095,
  continuousTracking: false,
})

function save() {
  ui.toast('System settings saved.')
}
</script>

<template>
  <div>
    <PageHeader title="System Settings" subtitle="Platform-wide security and privacy configuration.">
      <template #actions>
        <BaseButton @click="save"><Save class="w-4 h-4" /> Save Settings</BaseButton>
      </template>
    </PageHeader>

    <div class="grid lg:grid-cols-2 gap-6">
      <BaseCard>
        <h3 class="font-headline font-semibold text-neutral-900 mb-1 flex items-center gap-2"><Camera class="w-4 h-4 text-primary-600" /> Verification Rules</h3>
        <p class="text-sm text-neutral-500 mb-4">Controls applied to every Time In / Time Out attempt.</p>
        <div class="space-y-4">
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-sm text-neutral-700">Require liveness detection</span>
            <input v-model="settings.requireLiveness" type="checkbox" class="w-9 h-5 rounded-full appearance-none bg-neutral-200 checked:bg-primary-600 relative transition-colors cursor-pointer before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-0.5 before:left-0.5 checked:before:translate-x-4 before:transition-transform" />
          </label>
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-sm text-neutral-700">Enforce strict GPS accuracy threshold</span>
            <input v-model="settings.strictGpsAccuracy" type="checkbox" class="w-9 h-5 rounded-full appearance-none bg-neutral-200 checked:bg-primary-600 relative transition-colors cursor-pointer before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-0.5 before:left-0.5 checked:before:translate-x-4 before:transition-transform" />
          </label>
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-sm text-neutral-700">Allow continuous location tracking</span>
            <input v-model="settings.continuousTracking" type="checkbox" class="w-9 h-5 rounded-full appearance-none bg-neutral-200 checked:bg-primary-600 relative transition-colors cursor-pointer before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-0.5 before:left-0.5 checked:before:translate-x-4 before:transition-transform" />
          </label>
          <BaseInput v-model="settings.rateLimitAttempts" type="number" label="Max verification attempts per hour" />
        </div>
      </BaseCard>

      <BaseCard>
        <h3 class="font-headline font-semibold text-neutral-900 mb-1 flex items-center gap-2"><Lock class="w-4 h-4 text-primary-600" /> Data Retention</h3>
        <p class="text-sm text-neutral-500 mb-4">Days before sensitive data is eligible for deletion.</p>
        <div class="space-y-4">
          <BaseInput v-model="settings.biometricRetentionDays" type="number" label="Biometric template retention (days)" />
          <BaseInput v-model="settings.documentRetentionDays" type="number" label="Document retention (days)" />
          <BaseInput v-model="settings.auditLogRetentionDays" type="number" label="Audit log retention (days)" />
        </div>
      </BaseCard>
    </div>

    <BaseCard class="mt-6">
      <div class="flex items-start gap-3">
        <ShieldCheck class="w-5 h-5 text-primary-600 shrink-0 mt-0.5" />
        <div>
          <p class="text-sm font-medium text-neutral-800">Privacy Notice</p>
          <p class="text-sm text-neutral-500 mt-1 leading-relaxed">
            Biometric templates and precise location are treated as sensitive data. Access is restricted to authorized
            roles, and all reads/writes to these records are captured in the audit log per the platform's security and
            privacy policy.
          </p>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
