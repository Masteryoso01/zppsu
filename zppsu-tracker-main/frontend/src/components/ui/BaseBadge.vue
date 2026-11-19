<script setup>
const props = defineProps({
  tone: { type: String, default: 'neutral' }, // primary | secondary | success | warning | danger | neutral | tertiary
  size: { type: String, default: 'md' },
})

const tones = {
  primary: 'bg-primary-50 text-primary-700 ring-primary-600/20',
  secondary: 'bg-secondary-50 text-secondary-700 ring-secondary-500/25',
  tertiary: 'bg-tertiary-100 text-tertiary-700 ring-tertiary-500/20',
  success: 'bg-success-50 text-success-600 ring-success-500/25',
  warning: 'bg-warning-50 text-warning-600 ring-warning-500/25',
  danger: 'bg-danger-50 text-danger-600 ring-danger-500/25',
  neutral: 'bg-neutral-100 text-neutral-600 ring-neutral-400/20',
}
</script>

<template>
  <span
    class="inline-flex items-center gap-1 rounded-full ring-1 ring-inset font-medium whitespace-nowrap"
    :class="[tones[props.tone] || tones.neutral, props.size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs']"
  >
    <slot />
  </span>
</template>
