<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, Bell, LogOut, ChevronDown } from '@lucide/vue'
import { useAuthStore } from '../../stores/auth'
import { useDataStore } from '../../stores/data'
import { useUiStore } from '../../stores/ui'
import { roleLabels } from '../../lib/nav'

const auth = useAuthStore()
const data = useDataStore()
const ui = useUiStore()
const router = useRouter()

const profileOpen = ref(false)
const notifOpen = ref(false)
const root = ref(null)

function onClickOutside(e) {
  if (root.value && !root.value.contains(e.target)) {
    profileOpen.value = false
    notifOpen.value = false
  }
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))

function logout() {
  auth.logout()
  data.reset()
  router.push('/login')
}

function openNotifications() {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value) data.markNotificationsRead()
}
</script>

<template>
  <header class="h-16 shrink-0 border-b border-neutral-200 bg-white/80 backdrop-blur-sm flex items-center gap-3 px-4 sm:px-6 sticky top-0 z-20">
    <button class="lg:hidden p-2 -ml-2 rounded-lg hover:bg-neutral-100 cursor-pointer" @click="ui.sidebarOpen = true">
      <Menu class="w-5 h-5 text-neutral-600" />
    </button>

    <div class="flex-1" />

    <div ref="root" class="flex items-center gap-1.5">
      <div class="relative">
        <button class="relative p-2 rounded-lg hover:bg-neutral-100 cursor-pointer" @click.stop="openNotifications">
          <Bell class="w-5 h-5 text-neutral-600" />
          <span v-if="data.unreadNotifications" class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary-600 ring-2 ring-white" />
        </button>
        <Transition enter-active-class="transition duration-150 ease-out" leave-active-class="transition duration-100 ease-in" enter-from-class="opacity-0 scale-95" leave-to-class="opacity-0 scale-95">
          <div v-if="notifOpen" class="fixed inset-x-3 top-[4.5rem] sm:absolute sm:inset-x-auto sm:top-auto sm:right-0 sm:mt-2 sm:w-80 bg-white rounded-xl shadow-lg border border-neutral-100 overflow-hidden">
            <div class="px-4 py-3 border-b border-neutral-100">
              <p class="font-medium text-sm text-neutral-800">Notifications</p>
            </div>
            <div class="max-h-80 overflow-y-auto scrollbar-thin divide-y divide-neutral-50">
              <div v-for="n in data.notifications" :key="n.id" class="px-4 py-3 hover:bg-neutral-50">
                <p class="text-sm font-medium text-neutral-800">{{ n.title }}</p>
                <p class="text-xs text-neutral-500 mt-0.5">{{ n.body }}</p>
                <p class="text-[11px] text-neutral-400 mt-1 font-label">{{ n.time }}</p>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <div class="relative">
        <button class="flex items-center gap-2 pl-2 pr-2.5 py-1.5 rounded-lg hover:bg-neutral-100 cursor-pointer" @click.stop="profileOpen = !profileOpen">
          <div class="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-semibold font-label shrink-0">
            {{ auth.initials }}
          </div>
          <div class="hidden sm:block text-left leading-tight">
            <p class="text-sm font-medium text-neutral-800 max-w-32 truncate">{{ auth.user?.name }}</p>
            <p class="text-xs text-neutral-400">{{ roleLabels[auth.role] }}</p>
          </div>
          <ChevronDown class="w-4 h-4 text-neutral-400 hidden sm:block" />
        </button>

        <Transition enter-active-class="transition duration-150 ease-out" leave-active-class="transition duration-100 ease-in" enter-from-class="opacity-0 scale-95" leave-to-class="opacity-0 scale-95">
          <div v-if="profileOpen" class="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-neutral-100 overflow-hidden py-1.5">
            <div class="px-3.5 py-2 border-b border-neutral-100 mb-1">
              <p class="text-sm font-medium text-neutral-800 truncate">{{ auth.user?.name }}</p>
              <p class="text-xs text-neutral-400 truncate">{{ auth.user?.email }}</p>
            </div>

            <div class="pt-0.5">
              <button class="w-full flex items-center gap-2 px-3.5 py-2 text-sm text-danger-600 hover:bg-danger-50 cursor-pointer" @click="logout">
                <LogOut class="w-4 h-4" /> Log out
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>
