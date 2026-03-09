<template>
  <v-card class="fill-height demo-card" rounded="xl" elevation="4">
    <v-img v-if="imageUrl" :src="imageUrl" height="220" cover />

    <v-card-item>
      <template #prepend>
        <v-avatar color="primary" variant="tonal" size="42">
          <v-icon icon="mdi-rocket-launch-outline" />
        </v-avatar>
      </template>
      <v-card-title class="text-wrap">{{ demo.title }}</v-card-title>
      <!-- <v-card-subtitle>{{ linkCountLabel }}</v-card-subtitle> -->
    </v-card-item>

    <v-divider />

    <v-card-text>
      <div class="d-flex flex-wrap ga-2 mb-4" v-if="demo.tags?.length">
        <v-chip v-for="tag in demo.tags" :key="`${demo.id}-${tag}`" size="small" variant="tonal">{{ tag }}</v-chip>
      </div>

      <div class="rich-text" v-html="safeDescription"></div>

      <div class="d-flex flex-wrap ga-2 mt-6">
        <v-chip
          v-for="link in demo.links"
          :key="`${demo.id}-${link.label}-${link.url}`"
          color="primary"
          variant="outlined"
          prepend-icon="mdi-open-in-new"
          :href="link.url"
          target="_blank"
          rel="noopener noreferrer"
          clickable
        >
          {{ link.label }}
        </v-chip>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import DOMPurify from 'dompurify'
import { computed } from 'vue'
import { api } from '../services/api'

const props = defineProps({
  demo: {
    type: Object,
    required: true
  }
})

const safeDescription = computed(() => DOMPurify.sanitize(props.demo.description || ''))
const linkCountLabel = computed(() => `${props.demo.links?.length || 0} available tab(s)`)
const imageUrl = computed(() => {
  if (!props.demo.image_path) return ''
  return props.demo.image_path.startsWith('http') ? props.demo.image_path : `${api.getApiBase()}${props.demo.image_path}`
})
</script>
