<script setup>
defineProps({
  padded: { type: Boolean, default: true },
  hover: { type: Boolean, default: false },
})
</script>

<template>
  <div
    class="bg-white rounded-2xl border border-neutral-200/80 shadow-sm"
    :class="[padded ? 'p-5' : '', hover ? 'transition-shadow hover:shadow-md' : '']"
  >
    <slot />
  </div>
</template>
