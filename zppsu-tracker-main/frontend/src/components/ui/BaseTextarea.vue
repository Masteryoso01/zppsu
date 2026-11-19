<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  required: { type: Boolean, default: false },
  rows: { type: Number, default: 4 },
})
defineEmits(['update:modelValue'])
</script>

<template>
  <label class="block">
    <span v-if="label" class="block text-sm font-medium text-neutral-700 mb-1.5">{{ label }}<span v-if="required" class="text-primary-600 ml-0.5">*</span></span>
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      :rows="rows"
      class="w-full rounded-lg border border-neutral-300 text-sm text-neutral-900 placeholder:text-neutral-400 px-3.5 py-2.5 outline-none transition-colors focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 resize-none"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </label>
</template>
