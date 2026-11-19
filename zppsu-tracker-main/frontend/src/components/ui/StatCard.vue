<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  icon: { type: [Object, Function], default: null },
  tone: { type: String, default: 'primary' }, // primary | secondary | tertiary | success | warning | danger
  trend: { type: String, default: '' },
  trendUp: { type: Boolean, default: true },
})

const toneClasses = {
  primary: 'bg-primary-50 text-primary-700',
  secondary: 'bg-secondary-50 text-secondary-700',
  tertiary: 'bg-tertiary-100 text-tertiary-700',
  success: 'bg-success-50 text-success-600',
  warning: 'bg-warning-50 text-warning-600',
  danger: 'bg-danger-50 text-danger-600',
}
</script>

<template>
  <div class="bg-white rounded-2xl border border-neutral-200/80 shadow-sm p-5 flex items-start justify-between gap-3">
    <div class="min-w-0">
      <p class="text-sm text-neutral-500 truncate">{{ label }}</p>
      <p class="font-headline text-2xl font-semibold text-neutral-900 mt-1">{{ value }}</p>
      <p v-if="trend" class="text-xs mt-1.5 font-medium" :class="trendUp ? 'text-success-600' : 'text-danger-600'">{{ trend }}</p>
    </div>
    <div v-if="icon" class="shrink-0 rounded-xl p-2.5" :class="toneClasses[tone]">
      <component :is="icon" class="w-5 h-5" />
    </div>
  </div>
</template>
