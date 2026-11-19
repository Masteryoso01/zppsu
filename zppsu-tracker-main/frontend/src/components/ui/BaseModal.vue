<script setup>
import { X } from '@lucide/vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: { type: String, default: 'md' }, // sm | md | lg
})
const emit = defineEmits(['update:modelValue'])

const sizes = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' }
function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div class="absolute inset-0 bg-tertiary-950/60 backdrop-blur-sm" @click="close" />
        <Transition
          enter-active-class="transition duration-200 ease-out"
          leave-active-class="transition duration-150 ease-in"
          enter-from-class="opacity-0 translate-y-4 sm:scale-95"
          leave-to-class="opacity-0 translate-y-4 sm:scale-95"
        >
          <div v-if="modelValue" class="relative bg-white w-full sm:rounded-2xl rounded-t-2xl shadow-xl max-h-[90vh] overflow-y-auto scrollbar-thin" :class="sizes[size]">
            <div class="flex items-center justify-between px-5 py-4 border-b border-neutral-100 sticky top-0 bg-white">
              <h3 class="font-headline font-semibold text-lg text-neutral-900">{{ title }}</h3>
              <button class="p-1.5 rounded-lg hover:bg-neutral-100 cursor-pointer" @click="close">
                <X class="w-4 h-4 text-neutral-500" />
              </button>
            </div>
            <div class="p-5">
              <slot />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
