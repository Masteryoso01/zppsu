<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({ iconRetinaUrl: markerIcon2x, iconUrl: markerIcon, shadowUrl: markerShadow })

const props = defineProps({
  locations: { type: Array, default: () => [] }, // [{ id, name, latitude, longitude, radius }]
  editable: { type: Boolean, default: false },
  center: { type: Object, default: () => ({ lat: 14.6507, lng: 121.0494 }) },
  zoom: { type: Number, default: 15 },
})
const emit = defineEmits(['pick'])

const mapEl = ref(null)
let map = null
let layerGroup = null

function render() {
  layerGroup.clearLayers()
  props.locations.forEach((loc) => {
    L.marker([loc.latitude, loc.longitude]).addTo(layerGroup).bindPopup(`<strong>${loc.name}</strong><br/>Radius: ${loc.radius}m`)
    L.circle([loc.latitude, loc.longitude], { radius: loc.radius, color: '#990000', fillColor: '#990000', fillOpacity: 0.1, weight: 1.5 }).addTo(layerGroup)
  })
}

onMounted(() => {
  map = L.map(mapEl.value, { scrollWheelZoom: false }).setView([props.center.lat, props.center.lng], props.zoom)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map)
  layerGroup = L.layerGroup().addTo(map)
  render()

  if (props.editable) {
    map.on('click', (e) => emit('pick', { lat: +e.latlng.lat.toFixed(6), lng: +e.latlng.lng.toFixed(6) }))
  }
})

watch(() => props.locations, render, { deep: true })
watch(() => [props.center.lat, props.center.lng], () => map?.setView([props.center.lat, props.center.lng], props.zoom))

onBeforeUnmount(() => map?.remove())
</script>

<template>
  <div ref="mapEl" class="w-full h-full min-h-64 rounded-xl z-0" />
</template>
