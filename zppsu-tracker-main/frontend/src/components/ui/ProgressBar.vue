<script setup>
const props = defineProps({
  value: { type: Number, required: true }, // 0-100
  tone: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
})
const toneClasses = {
  primary: 'bg-primary-600', secondary: 'bg-secondary-500', tertiary: 'bg-tertiary-800',
  success: 'bg-success-500', warning: 'bg-warning-500', danger: 'bg-danger-500',
}
</script>

<template>
  <div class="w-full bg-neutral-100 rounded-full overflow-hidden" :class="size === 'sm' ? 'h-1.5' : 'h-2.5'">
    <div
      class="h-full rounded-full transition-all duration-500"
      :class="toneClasses[props.tone]"
      :style="{ width: `${Math.min(100, Math.max(0, props.value))}%` }"
    />
  </div>
</template>
