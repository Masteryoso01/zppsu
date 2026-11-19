<script setup>
import BaseBadge from './BaseBadge.vue'
import { statusTone } from '../../lib/status'

defineProps({ status: { type: String, required: true }, size: { type: String, default: 'md' } })
</script>

<template>
  <BaseBadge :tone="statusTone(status)" :size="size">
    <slot>{{ status }}</slot>
  </BaseBadge>
</template>
