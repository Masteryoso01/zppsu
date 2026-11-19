<script setup>
defineProps({
  variant: { type: String, default: 'primary' }, // primary | secondary | inverted | outline | ghost | danger
  size: { type: String, default: 'md' }, // sm | md | lg
  type: { type: String, default: 'button' },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
})
defineEmits(['click'])

const variants = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:outline-primary-600 disabled:bg-primary-300',
  secondary: 'bg-secondary-500 text-white hover:bg-secondary-600 focus-visible:outline-secondary-500 disabled:bg-secondary-200',
  inverted: 'bg-tertiary-900 text-white hover:bg-tertiary-800 focus-visible:outline-tertiary-900 disabled:bg-tertiary-300',
  outline: 'bg-transparent text-primary-700 border border-primary-600 hover:bg-primary-50 disabled:text-primary-300 disabled:border-primary-200',
  ghost: 'bg-transparent text-neutral-700 hover:bg-neutral-100 disabled:text-neutral-300',
  danger: 'bg-danger-600 text-white hover:bg-red-700 focus-visible:outline-danger-600 disabled:bg-red-200',
}
const sizes = {
  sm: 'text-sm px-3 py-1.5 gap-1.5 rounded-lg',
  md: 'text-sm px-4 py-2.5 gap-2 rounded-lg',
  lg: 'text-base px-5 py-3 gap-2 rounded-xl',
}
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    class="inline-flex items-center justify-center font-medium transition-colors duration-150 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed cursor-pointer"
    :class="[variants[variant], sizes[size], block ? 'w-full' : '']"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>
