<script setup>
import { RouterLink } from 'vue-router'
import { MapPin, X } from '@lucide/vue'
import { useUiStore } from '../../stores/ui'
import { roleLabels } from '../../lib/nav'

defineProps({
  items: { type: Array, required: true },
  role: { type: String, required: true },
  orgName: { type: String, default: '' },
})

const ui = useUiStore()
</script>

<template>
  <!-- mobile overlay -->
  <Transition enter-active-class="transition-opacity duration-200" leave-active-class="transition-opacity duration-200" enter-from-class="opacity-0" leave-to-class="opacity-0">
    <div v-if="ui.sidebarOpen" class="fixed inset-0 bg-tertiary-950/50 z-30 lg:hidden" @click="ui.sidebarOpen = false" />
  </Transition>

  <aside
    class="fixed lg:sticky lg:top-0 lg:h-screen inset-y-0 left-0 z-40 w-64 shrink-0 bg-tertiary-950 text-white flex flex-col transition-transform duration-200 lg:translate-x-0"
    :class="ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
  >
    <div class="flex items-center justify-between px-5 h-16 border-b border-white/10 shrink-0">
      <RouterLink :to="`/${role}/dashboard`" class="flex items-center gap-2.5 min-w-0">
        <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shrink-0">
          <MapPin class="w-4.5 h-4.5 text-white" />
        </div>
        <div class="min-w-0">
          <p class="font-headline font-semibold text-sm leading-tight truncate">GeoTrack</p>
          <p class="text-[11px] text-tertiary-300 truncate">{{ roleLabels[role] }} Portal</p>
        </div>
      </RouterLink>
      <button class="lg:hidden p-1.5 rounded-lg hover:bg-white/10 cursor-pointer" @click="ui.sidebarOpen = false">
        <X class="w-4 h-4" />
      </button>
    </div>

    <p v-if="orgName" class="px-5 pt-3 text-[11px] uppercase tracking-wide text-tertiary-400 font-label truncate">{{ orgName }}</p>

    <nav class="flex-1 overflow-y-auto scrollbar-thin px-3 py-4 space-y-0.5">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group"
        active-class="!bg-primary-600 !text-white"
        :class="'text-tertiary-200 hover:bg-white/5 hover:text-white'"
        @click="ui.sidebarOpen = false"
      >
        <component :is="item.icon" class="w-4.5 h-4.5 shrink-0" />
        <span class="truncate">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="px-5 py-4 border-t border-white/10 text-[11px] text-tertiary-400 font-label">
      GeoTrack v1.0
    </div>
  </aside>
</template>
