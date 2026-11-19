<script setup>
defineProps({
  icon: { type: [Object, Function], default: null },
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="flex flex-col items-center justify-center text-center py-12 px-4">
    <div v-if="icon" class="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center mb-3">
      <component :is="icon" class="w-6 h-6 text-neutral-400" />
    </div>
    <p class="font-medium text-neutral-700">{{ title }}</p>
    <p v-if="description" class="text-sm text-neutral-500 mt-1 max-w-sm">{{ description }}</p>
    <div class="mt-4">
      <slot name="action" />
    </div>
  </div>
</template>
