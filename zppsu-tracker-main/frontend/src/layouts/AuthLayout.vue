<script setup>
import { MapPin, ScanFace, MapPinned, ShieldCheck } from '@lucide/vue'

const features = [
  { icon: ScanFace, text: 'Fingerprint / Face ID verification on your phone' },
  { icon: MapPinned, text: 'Geofenced Time In / Time Out' },
  { icon: ShieldCheck, text: 'Role-based access & full audit trail' },
]
</script>

<template>
  <div class="min-h-screen grid lg:grid-cols-2 bg-neutral-50">
    <div class="relative hidden lg:flex flex-col justify-between bg-tertiary-950 text-white p-12 overflow-hidden">
      <div class="absolute inset-0 opacity-[0.07]" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 28px 28px;" />
      <div class="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-primary-600/30 blur-3xl" />
      <div class="absolute -bottom-32 -left-16 w-96 h-96 rounded-full bg-secondary-500/20 blur-3xl" />

      <div class="relative flex items-center gap-2.5">
        <div class="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center">
          <MapPin class="w-5 h-5 text-white" />
        </div>
        <span class="font-headline font-semibold text-xl">GeoTrack</span>
      </div>

      <div class="relative max-w-md">
        <h1 class="font-headline text-4xl font-semibold leading-tight tracking-tight">
          Geolocation-based OJT monitoring, done right.
        </h1>
        <p class="text-tertiary-300 mt-4 text-sm leading-relaxed">
          Onboard OJT trainees, verify attendance with your phone's biometrics + GPS, and track rendered hours — all in one platform.
        </p>
        <ul class="mt-8 space-y-4">
          <li v-for="f in features" :key="f.text" class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center shrink-0">
              <component :is="f.icon" class="w-4.5 h-4.5 text-secondary-400" />
            </div>
            <span class="text-sm text-tertiary-100">{{ f.text }}</span>
          </li>
        </ul>
      </div>

      <p class="relative text-xs text-tertiary-400 font-label">© 2026 GeoTrack. All rights reserved.</p>
    </div>

    <div class="flex items-start sm:items-center justify-center p-6 sm:p-10 lg:overflow-y-auto lg:max-h-screen">
      <div class="w-full my-auto" :class="$route.meta.wide ? 'max-w-lg' : 'max-w-sm'">
        <div class="lg:hidden flex items-center gap-2.5 mb-8 justify-center">
          <div class="w-9 h-9 rounded-lg bg-primary-600 flex items-center justify-center">
            <MapPin class="w-4.5 h-4.5 text-white" />
          </div>
          <span class="font-headline font-semibold text-lg text-neutral-900">GeoTrack</span>
        </div>
        <RouterView />
      </div>
    </div>
  </div>
</template>
