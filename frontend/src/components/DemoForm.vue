<template>
  <v-form @submit.prevent="submitForm">
    <v-text-field v-model="form.title" label="Title" variant="outlined" density="comfortable" :rules="[requiredRule]" />

    <v-text-field
      v-model="tagsInput"
      label="Tags"
      variant="outlined"
      density="comfortable"
      hint="Separate tags with commas"
      persistent-hint
      prepend-inner-icon="mdi-tag-multiple-outline"
    />

    <v-switch
      v-model="form.is_visible"
      label="Visible in the catalog"
      color="primary"
      hide-details
      class="mb-4"
    />

    <div class="mb-2 text-subtitle-2">Image</div>
    <div class="mb-6">
      <div class="d-flex ga-3 align-center flex-wrap mb-3">
        <v-file-input
          accept="image/png,image/jpeg,image/webp,image/gif"
          label="Choose an image"
          variant="outlined"
          density="comfortable"
          prepend-icon="mdi-image-outline"
          hide-details
          style="max-width: 420px"
          @update:model-value="handleImageSelected"
        />
        <v-btn v-if="form.image_path" color="error" variant="text" @click="removeImage">Remove image</v-btn>
      </div>
      <v-progress-linear v-if="uploadingImage" indeterminate class="mb-3" />
      <v-img v-if="imagePreview" :src="imagePreview" height="180" max-width="360" cover class="rounded-lg border-preview" />
    </div>

    <div class="mb-2 text-subtitle-2">Rich text description</div>
    <div class="mb-6">
      <RichTextEditor
        v-model="form.description"
        placeholder="Start typing..."
        :upload-image="uploadEditorImage"
        @error="(message) => emit('error', message)"
      />
    </div>

    <div class="d-flex align-center mb-3">
      <div class="text-subtitle-2">Chips / links</div>
      <v-spacer />
      <v-btn color="primary" variant="tonal" prepend-icon="mdi-plus" @click="addLink">Add link</v-btn>
    </div>

    <v-row v-for="(link, index) in form.links" :key="index" class="mb-1">
      <v-col cols="12" md="5">
        <v-text-field v-model="link.label" label="Chip label" variant="outlined" density="comfortable" />
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field v-model="link.url" label="URL" variant="outlined" density="comfortable" placeholder="https://..." />
      </v-col>
      <v-col cols="12" md="1" class="d-flex align-center justify-center">
        <v-btn icon="mdi-delete-outline" color="error" variant="text" @click="removeLink(index)" />
      </v-col>
    </v-row>

    <div class="d-flex ga-3 mt-6 flex-wrap">
      <v-btn color="primary" type="submit" :loading="loading || uploadingImage">{{ submitLabel }}</v-btn>
      <v-btn variant="text" @click="resetForm">Reset</v-btn>
    </div>
  </v-form>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import RichTextEditor from './RichTextEditor.vue'
import { api } from '../services/api'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      title: '',
      description: '',
      links: [],
      tags: [],
      image_path: null,
      is_visible: true
    })
  },
  loading: {
    type: Boolean,
    default: false
  },
  submitLabel: {
    type: String,
    default: 'Save'
  }
})

const emit = defineEmits(['submit', 'reset', 'error'])

const tagsInput = ref('')
const uploadingImage = ref(false)

const emptyForm = () => ({
  title: '',
  description: '',
  links: [{ label: '', url: '' }],
  tags: [],
  image_path: null,
  is_visible: true
})

const form = reactive(emptyForm())

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(form, {
      title: value?.title || '',
      description: value?.description || '',
      image_path: value?.image_path || null,
      is_visible: value?.is_visible ?? true,
      tags: Array.isArray(value?.tags) ? [...value.tags] : [],
      links: Array.isArray(value?.links) && value.links.length ? value.links.map((item) => ({ ...item })) : [{ label: '', url: '' }]
    })
    tagsInput.value = form.tags.join(', ')
  },
  { immediate: true, deep: true }
)

const imagePreview = computed(() => {
  if (!form.image_path) return ''
  return form.image_path.startsWith('http') ? form.image_path : `${api.getApiBase()}${form.image_path}`
})

const requiredRule = (value) => !!value || 'This field is required.'

function addLink() {
  form.links.push({ label: '', url: '' })
}

function removeLink(index) {
  form.links.splice(index, 1)
  if (!form.links.length) {
    form.links.push({ label: '', url: '' })
  }
}

function normalizeTags() {
  return tagsInput.value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
    .filter((item, index, array) => array.findIndex((entry) => entry.toLowerCase() === item.toLowerCase()) === index)
}

async function uploadImage(file) {
  if (!file) return null
  uploadingImage.value = true
  try {
    const result = await api.uploadImage(file)
    return result.image_path
  } catch (error) {
    emit('error', error.message)
    return null
  } finally {
    uploadingImage.value = false
  }
}

async function handleImageSelected(value) {
  const file = Array.isArray(value) ? value[0] : value
  if (!file) return
  const imagePath = await uploadImage(file)
  if (imagePath) {
    form.image_path = imagePath
  }
}

function removeImage() {
  form.image_path = null
}

async function uploadEditorImage(file) {
  const imagePath = await uploadImage(file)
  return imagePath ? `${api.getApiBase()}${imagePath}` : null
}

function submitForm() {
  emit('submit', {
    title: form.title.trim(),
    description: form.description,
    image_path: form.image_path,
    is_visible: form.is_visible,
    tags: normalizeTags(),
    links: form.links
      .map((item) => ({
        label: item.label.trim(),
        url: item.url.trim()
      }))
      .filter((item) => item.label && item.url)
  })
}

function resetForm() {
  Object.assign(form, emptyForm())
  tagsInput.value = ''
  emit('reset')
}
</script>
