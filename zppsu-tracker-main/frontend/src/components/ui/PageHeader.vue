<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-6">
    <div>
      <h1 class="font-headline text-2xl sm:text-3xl font-semibold text-neutral-900 tracking-tight">{{ title }}</h1>
      <p v-if="subtitle" class="text-neutral-500 text-sm mt-1">{{ subtitle }}</p>
    </div>
    <div class="flex items-center gap-2 shrink-0">
      <slot name="actions" />
    </div>
  </div>
</template>
