<script setup>
import { CheckCircle2, XCircle, Info, X } from '@lucide/vue'
import { useUiStore } from '../../stores/ui'

const ui = useUiStore()
const icons = { success: CheckCircle2, danger: XCircle, info: Info }
const toneClasses = {
  success: 'border-success-500/30 text-success-600',
  danger: 'border-danger-500/30 text-danger-600',
  info: 'border-primary-500/30 text-primary-600',
}
</script>

<template>
  <div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-[min(360px,calc(100vw-2rem))]">
    <TransitionGroup
      enter-active-class="transition duration-200 ease-out"
      leave-active-class="transition duration-150 ease-in absolute"
      enter-from-class="opacity-0 translate-y-2"
      leave-to-class="opacity-0"
    >
      <div
        v-for="t in ui.toasts"
        :key="t.id"
        class="bg-white rounded-xl shadow-lg border-l-4 px-4 py-3 flex items-start gap-2.5"
        :class="toneClasses[t.tone] || toneClasses.info"
      >
        <component :is="icons[t.tone] || Info" class="w-5 h-5 shrink-0 mt-0.5" />
        <p class="text-sm text-neutral-700 flex-1">{{ t.message }}</p>
        <button class="text-neutral-400 hover:text-neutral-600 cursor-pointer" @click="ui.dismiss(t.id)">
          <X class="w-4 h-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
