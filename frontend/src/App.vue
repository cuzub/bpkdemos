<template>
  <v-app>
    <v-app-bar color="surface" flat class="border-b">
      <v-container class="d-flex align-center py-0 ga-3 flex-wrap">
        <div class="d-flex align-center ga-2">
          <v-img
            :src="logo"
            width="96"
            height="96"
          />
          <div class="text-h5 font-weight-bold">Broadpeak Demos</div>
        </div>

        <v-spacer />

        <v-text-field
          v-model="globalSearch"
          prepend-inner-icon="mdi-magnify"
          label="Search demos"
          variant="solo-filled"
          density="compact"
          hide-details
          flat
          class="app-search-field"
        />

        <v-btn to="/" variant="text" prepend-icon="mdi-view-grid-outline">Catalog</v-btn>
        <v-btn to="/admin" variant="text" prepend-icon="mdi-shield-account-outline">Admin</v-btn>
        <v-btn :icon="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'" variant="text" @click="toggleTheme" />
      </v-container>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useTheme } from 'vuetify'
import { globalSearch } from './stores/search'
import logo from './assets/logo.svg'

const STORAGE_KEY = 'demo-showcase-theme'
const theme = useTheme()
const isDark = computed(() => theme.global.name.value === 'dark')

function applyTheme(name) {
  theme.global.name.value = name
  localStorage.setItem(STORAGE_KEY, name)
  document.documentElement.style.colorScheme = name
}

function toggleTheme() {
  applyTheme(isDark.value ? 'light' : 'dark')
}

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  applyTheme(saved || preferred)
})
</script>