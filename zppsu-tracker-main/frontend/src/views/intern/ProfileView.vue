<script setup>
import { computed, reactive, ref } from 'vue'
import { Pencil, Save, X, Mail, Phone, IdCard, School, BookOpen, MapPin, CalendarClock } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'

const data = useDataStore()
const ui = useUiStore()
const intern = computed(() => data.currentIntern)

const editing = ref(false)
const form = reactive({ contact: '', address: '', course: '', yearLevel: '' })

function startEdit() {
  form.contact = intern.value.contact
  form.address = intern.value.address
  form.course = intern.value.course
  form.yearLevel = intern.value.yearLevel
  editing.value = true
}
function save() {
  Object.assign(intern.value, form)
  editing.value = false
  ui.toast('Profile updated successfully.')
}

const readonlyFields = computed(() => [
  { icon: Mail, label: 'Email', value: intern.value.email },
  { icon: IdCard, label: 'Student ID', value: intern.value.studentId },
  { icon: School, label: 'School', value: intern.value.school },
])
</script>

<template>
  <div>
    <PageHeader title="My Profile" subtitle="Keep your personal and academic information up to date.">
      <template #actions>
        <BaseButton v-if="!editing" variant="outline" size="sm" @click="startEdit">
          <Pencil class="w-4 h-4" /> Edit Profile
        </BaseButton>
        <template v-else>
          <BaseButton variant="ghost" size="sm" @click="editing = false"><X class="w-4 h-4" /> Cancel</BaseButton>
          <BaseButton size="sm" @click="save"><Save class="w-4 h-4" /> Save Changes</BaseButton>
        </template>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <BaseCard class="lg:col-span-1 flex flex-col items-center text-center">
        <div class="w-24 h-24 rounded-full bg-primary-600 text-white flex items-center justify-center text-2xl font-semibold font-label">
          {{ intern.name.split(' ').map(n => n[0]).slice(0,2).join('') }}
        </div>
        <h3 class="font-headline font-semibold text-lg text-neutral-900 mt-4">{{ intern.name }}</h3>
        <p class="text-sm text-neutral-500">{{ intern.course }}</p>
        <div class="flex items-center gap-2 mt-3">
          <StatusBadge :status="intern.applicationStatus" size="sm" />
          <StatusBadge :status="intern.internshipStatus" size="sm" />
        </div>
        <div class="w-full mt-5 pt-5 border-t border-neutral-100 space-y-3 text-left">
          <div v-for="f in readonlyFields" :key="f.label" class="flex items-center gap-2.5 text-sm">
            <component :is="f.icon" class="w-4 h-4 text-neutral-400 shrink-0" />
            <span class="text-neutral-600 truncate">{{ f.value }}</span>
          </div>
        </div>
      </BaseCard>

      <BaseCard class="lg:col-span-2">
        <h3 class="font-headline font-semibold text-neutral-900 mb-4">Contact & Academic Details</h3>

        <div v-if="!editing" class="grid sm:grid-cols-2 gap-5">
          <div>
            <p class="text-xs text-neutral-400 flex items-center gap-1.5"><Phone class="w-3.5 h-3.5" /> Contact Number</p>
            <p class="text-sm font-medium text-neutral-800 mt-1">{{ intern.contact }}</p>
          </div>
          <div>
            <p class="text-xs text-neutral-400 flex items-center gap-1.5"><CalendarClock class="w-3.5 h-3.5" /> Year Level</p>
            <p class="text-sm font-medium text-neutral-800 mt-1">{{ intern.yearLevel }}</p>
          </div>
          <div>
            <p class="text-xs text-neutral-400 flex items-center gap-1.5"><BookOpen class="w-3.5 h-3.5" /> Course / Program</p>
            <p class="text-sm font-medium text-neutral-800 mt-1">{{ intern.course }}</p>
          </div>
          <div class="sm:col-span-2">
            <p class="text-xs text-neutral-400 flex items-center gap-1.5"><MapPin class="w-3.5 h-3.5" /> Address</p>
            <p class="text-sm font-medium text-neutral-800 mt-1">{{ intern.address }}</p>
          </div>
        </div>

        <form v-else class="grid sm:grid-cols-2 gap-5" @submit.prevent="save">
          <BaseInput v-model="form.contact" label="Contact Number" :icon="Phone" />
          <BaseInput v-model="form.yearLevel" label="Year Level" :icon="CalendarClock" />
          <BaseInput v-model="form.course" label="Course / Program" :icon="BookOpen" />
          <BaseInput v-model="form.address" label="Address" :icon="MapPin" class="sm:col-span-2" />
        </form>

        <div class="mt-6 pt-5 border-t border-neutral-100">
          <h4 class="font-medium text-neutral-800 text-sm mb-3">OJT Assignment</h4>
          <div class="grid sm:grid-cols-3 gap-4 text-sm">
            <div>
              <p class="text-xs text-neutral-400">Required Hours</p>
              <p class="font-medium text-neutral-800 mt-0.5">{{ intern.requiredHours }}h</p>
            </div>
            <div>
              <p class="text-xs text-neutral-400">Start Date</p>
              <p class="font-medium text-neutral-800 mt-0.5">{{ intern.startDate || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-neutral-400">End Date</p>
              <p class="font-medium text-neutral-800 mt-0.5">{{ intern.endDate || '—' }}</p>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>
