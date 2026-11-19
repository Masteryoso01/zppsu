<script setup>
import { computed, reactive, ref } from 'vue'
import { Plus, Trash2, Pencil, Landmark, Crosshair } from '@lucide/vue'
import { useDataStore } from '../../stores/data'
import { useAuthStore } from '../../stores/auth'
import { useUiStore } from '../../stores/ui'
import PageHeader from '../../components/ui/PageHeader.vue'
import BaseCard from '../../components/ui/BaseCard.vue'
import BaseButton from '../../components/ui/BaseButton.vue'
import BaseModal from '../../components/ui/BaseModal.vue'
import BaseInput from '../../components/ui/BaseInput.vue'
import StatusBadge from '../../components/ui/StatusBadge.vue'
import LocationMap from '../../components/LocationMap.vue'

const data = useDataStore()
const auth = useAuthStore()
const ui = useUiStore()

const locations = computed(() => data.orgLocations(auth.user.orgId))
const mapCenter = computed(() => {
  const first = locations.value[0]
  return first ? { lat: first.latitude, lng: first.longitude } : { lat: 14.6507, lng: 121.0494 }
})

const modalOpen = ref(false)
const editingId = ref(null)
const form = reactive({ name: '', latitude: 14.6507, longitude: 121.0494, radius: 100 })

function openNew() {
  editingId.value = null
  form.name = ''
  form.latitude = mapCenter.value.lat
  form.longitude = mapCenter.value.lng
  form.radius = 100
  modalOpen.value = true
}
function openEdit(loc) {
  editingId.value = loc.id
  form.name = loc.name
  form.latitude = loc.latitude
  form.longitude = loc.longitude
  form.radius = loc.radius
  modalOpen.value = true
}
function onPick(coords) {
  form.latitude = coords.lat
  form.longitude = coords.lng
}
async function save() {
  if (!form.name) return
  const payload = { name: form.name, latitude: +form.latitude, longitude: +form.longitude, radius: +form.radius }
  try {
    if (editingId.value) {
      await data.updateLocation(editingId.value, payload)
      ui.toast('Location updated.')
    } else {
      await data.addLocation(payload)
      ui.toast('Location added.')
    }
    modalOpen.value = false
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
async function remove(loc) {
  try {
    await data.removeLocation(loc.id)
    ui.toast('Location removed.', 'danger')
  } catch (e) {
    ui.toast(e.message, 'danger')
  }
}
</script>

<template>
  <div>
    <PageHeader title="Attendance Locations" subtitle="Configure geofenced locations and allowed radius for Time In / Time Out.">
      <template #actions>
        <BaseButton @click="openNew"><Plus class="w-4 h-4" /> Add Location</BaseButton>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <BaseCard :padded="false" class="lg:col-span-3 overflow-hidden h-96">
        <LocationMap :locations="locations" :center="mapCenter" />
      </BaseCard>

      <div class="lg:col-span-2 space-y-3">
        <BaseCard v-for="loc in locations" :key="loc.id" hover>
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-start gap-2.5 min-w-0">
              <div class="w-9 h-9 rounded-lg bg-primary-50 flex items-center justify-center shrink-0">
                <Landmark class="w-4.5 h-4.5 text-primary-600" />
              </div>
              <div class="min-w-0">
                <p class="font-medium text-neutral-800 truncate">{{ loc.name }}</p>
                <p class="text-xs text-neutral-400 font-label mt-0.5">{{ loc.latitude.toFixed(4) }}, {{ loc.longitude.toFixed(4) }}</p>
                <p class="text-xs text-neutral-500 mt-1">Radius: {{ loc.radius }}m</p>
              </div>
            </div>
            <div class="flex flex-col items-end gap-2 shrink-0">
              <StatusBadge :status="loc.status" size="sm" />
              <div class="flex items-center gap-1">
                <button class="p-1.5 rounded-lg hover:bg-neutral-100 cursor-pointer" @click="openEdit(loc)"><Pencil class="w-3.5 h-3.5 text-neutral-500" /></button>
                <button class="p-1.5 rounded-lg hover:bg-danger-50 cursor-pointer" @click="remove(loc)"><Trash2 class="w-3.5 h-3.5 text-danger-500" /></button>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>

    <BaseModal v-model="modalOpen" :title="editingId ? 'Edit Location' : 'Add Location'" size="lg">
      <div class="grid sm:grid-cols-2 gap-5">
        <div class="space-y-4">
          <BaseInput v-model="form.name" label="Location name" placeholder="Main Office" required />
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <BaseInput v-model="form.latitude" type="number" label="Latitude" required />
            <BaseInput v-model="form.longitude" type="number" label="Longitude" required />
          </div>
          <BaseInput v-model="form.radius" type="number" label="Allowed radius (meters)" required />
          <p class="text-xs text-neutral-400 flex items-center gap-1.5"><Crosshair class="w-3.5 h-3.5" /> Click the map to set coordinates</p>
          <BaseButton block @click="save">{{ editingId ? 'Save Changes' : 'Add Location' }}</BaseButton>
        </div>
        <div class="h-64 sm:h-full rounded-xl overflow-hidden">
          <LocationMap
            :locations="[{ id: 'preview', name: form.name || 'New Location', latitude: +form.latitude, longitude: +form.longitude, radius: +form.radius }]"
            :center="{ lat: +form.latitude, lng: +form.longitude }"
            editable
            @pick="onPick"
          />
        </div>
      </div>
    </BaseModal>
  </div>
</template>
