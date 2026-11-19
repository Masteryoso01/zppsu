<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  required: { type: Boolean, default: false },
  icon: { type: [Object, Function], default: null },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
})
defineEmits(['update:modelValue'])
</script>

<template>
  <label class="block">
    <span v-if="label" class="block text-sm font-medium text-neutral-700 mb-1.5">{{ label }}<span v-if="required" class="text-primary-600 ml-0.5">*</span></span>
    <div class="relative">
      <component :is="icon" v-if="icon" class="w-4 h-4 text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2" />
      <input
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :required="required"
        class="w-full rounded-lg border text-sm text-neutral-900 placeholder:text-neutral-400 px-3.5 py-2.5 outline-none transition-colors focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10"
        :class="[icon ? 'pl-9' : '', error ? 'border-danger-400' : 'border-neutral-300']"
        @input="$emit('update:modelValue', $event.target.value)"
      />
    </div>
    <p v-if="error" class="text-xs text-danger-600 mt-1.5">{{ error }}</p>
    <p v-else-if="hint" class="text-xs text-neutral-400 mt-1.5">{{ hint }}</p>
  </label>
</template>
