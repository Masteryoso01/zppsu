<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  options: { type: Array, default: () => [] }, // [{ label, value }]
  required: { type: Boolean, default: false },
  placeholder: { type: String, default: 'Select...' },
})
defineEmits(['update:modelValue'])
</script>

<template>
  <label class="block">
    <span v-if="label" class="block text-sm font-medium text-neutral-700 mb-1.5">{{ label }}<span v-if="required" class="text-primary-600 ml-0.5">*</span></span>
    <select
      :value="modelValue"
      class="w-full rounded-lg border border-neutral-300 text-sm text-neutral-900 px-3.5 py-2.5 outline-none transition-colors focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 bg-white"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>{{ placeholder }}</option>
      <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
    </select>
  </label>
</template>
