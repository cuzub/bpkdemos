<template>
  <v-container class="py-8">
    <v-row class="mb-2" align="center">
      <!-- <v-col cols="12" md="12">
        <div class="text-h4 font-weight-bold mb-2">Available demos</div>
        <div class="text-body-1 text-medium-emphasis">
          An elegant showcase to launch your demos, proofs of concept, and test environments.
        </div>
      </v-col> -->
    </v-row>

    <div class="d-flex flex-wrap tag-filter-group mb-6">
      <v-chip class="tag-filter-chip" :variant="selectedTag ? 'outlined' : 'flat'" :color="selectedTag ? undefined : 'primary'" @click="selectedTag = ''">All</v-chip>
      <v-chip
        v-for="tag in tags"
        :key="tag"
        class="tag-filter-chip"
        :variant="selectedTag === tag ? 'flat' : 'outlined'"
        :color="selectedTag === tag ? 'primary' : undefined"
        @click="selectedTag = selectedTag === tag ? '' : tag"
      >
        {{ tag }}
      </v-chip>
    </div>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-6">{{ error }}</v-alert>

    <v-row v-if="loading">
      <v-col v-for="n in 6" :key="n" cols="12" md="6" lg="4">
        <v-skeleton-loader type="card" />
      </v-col>
    </v-row>

    <v-row v-else-if="filteredDemos.length">
      <v-col v-for="demo in filteredDemos" :key="demo.id" cols="12" md="6" lg="4">
        <DemoCard :demo="demo" />
      </v-col>
    </v-row>

    <v-empty-state
      v-else
      headline="No demos found"
      text="Add a new demo in the admin area or adjust your search."
      icon="mdi-folder-search-outline"
    />
  </v-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import DemoCard from '../components/DemoCard.vue'
import { api } from '../services/api'
import { globalSearch } from '../stores/search'

const demos = ref([])
const tags = ref([])
const loading = ref(true)
const error = ref('')
const selectedTag = ref('')

const filteredDemos = computed(() => {
  const term = globalSearch.value.trim().toLowerCase()

  return demos.value.filter((demo) => {
    const tagMatch = !selectedTag.value || demo.tags?.some((tag) => tag.toLowerCase() === selectedTag.value.toLowerCase())
    if (!tagMatch) return false

    if (!term) return true
    const haystack = `${demo.title} ${demo.description} ${(demo.tags || []).join(' ')} ${(demo.links || []).map((link) => `${link.label} ${link.url}`).join(' ')}`.toLowerCase()
    return haystack.includes(term)
  })
})

async function loadDemos() {
  loading.value = true
  error.value = ''
  try {
    const [demoData, tagData] = await Promise.all([api.listDemos(), api.listTags()])
    demos.value = demoData
    tags.value = tagData
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadDemos)
</script>
