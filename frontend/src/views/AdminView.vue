<template>
  <v-container class="py-8">
    <v-row>
      <v-col cols="12" lg="5">
        <v-card rounded="xl" elevation="4">
          <v-card-item>
            <v-card-title>{{ isAuthenticated ? (editingId ? 'Edit demo' : 'Create demo') : 'Admin sign in' }}</v-card-title>
            <v-card-subtitle>
              {{ isAuthenticated ? 'Secure catalog management' : 'Sign in to manage demos' }}
            </v-card-subtitle>
          </v-card-item>
          <v-divider />
          <v-card-text>
            <v-alert v-if="formMessage" :type="formMessageType" variant="tonal" class="mb-4">
              {{ formMessage }}
            </v-alert>

            <v-form v-if="!isAuthenticated" @submit.prevent="handleLogin">
              <v-text-field v-model="credentials.username" label="Username" variant="outlined" class="mb-2" />
              <v-text-field v-model="credentials.password" label="Password" type="password" variant="outlined" class="mb-4" />
              <v-btn color="primary" type="submit" :loading="loggingIn">Sign in</v-btn>
            </v-form>

            <template v-else>
              <div class="d-flex justify-space-between align-center mb-4 flex-wrap ga-2">
                <v-chip color="success" variant="tonal" prepend-icon="mdi-shield-check-outline">Signed in</v-chip>
                <v-btn variant="text" color="error" @click="logout">Sign out</v-btn>
              </div>

              <DemoForm
                :model-value="currentDemo"
                :loading="saving"
                :submit-label="editingId ? 'Update demo' : 'Create demo'"
                @submit="handleSubmit"
                @reset="resetEditor"
                @error="showError"
              />
            </template>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="7">
        <v-card rounded="xl" elevation="4">
          <v-card-item>
            <v-card-title>Existing demos</v-card-title>
            <v-card-subtitle>{{ demos.length }} item(s)</v-card-subtitle>
          </v-card-item>
          <v-divider />
          <v-card-text>
            <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4">{{ loadError }}</v-alert>
            <v-list lines="two">
              <v-list-item v-for="demo in demos" :key="demo.id" :title="demo.title" :subtitle="buildSubtitle(demo)">
                <template #prepend>
                  <v-avatar rounded="lg" size="56" v-if="demo.image_path">
                    <v-img :src="imageUrl(demo.image_path)" cover />
                  </v-avatar>
                </template>
                <template #append>
                  <div class="d-flex ga-2 align-center flex-wrap justify-end">
                    <v-chip
                      v-if="isAuthenticated"
                      :color="demo.is_visible ? 'success' : 'grey'"
                      size="small"
                      variant="tonal"
                    >
                      {{ demo.is_visible ? 'Visible' : 'Hidden' }}
                    </v-chip>
                    <v-btn
                      v-if="isAuthenticated"
                      :icon="demo.is_visible ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
                      variant="text"
                      color="primary"
                      @click="toggleVisibility(demo)"
                    />
                    <v-btn v-if="isAuthenticated" icon="mdi-pencil-outline" variant="text" color="primary" @click="startEdit(demo)" />
                    <v-btn v-if="isAuthenticated" icon="mdi-delete-outline" variant="text" color="error" @click="removeDemo(demo)" />
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import DemoForm from '../components/DemoForm.vue'
import { api } from '../services/api'

const demos = ref([])
const saving = ref(false)
const loggingIn = ref(false)
const loadError = ref('')
const formMessage = ref('')
const formMessageType = ref('success')
const editingId = ref(null)
const isAuthenticated = ref(api.isAuthenticated())
const credentials = ref({ username: 'admin', password: 'admin123!' })
const currentDemo = ref({ title: '', description: '', links: [{ label: '', url: '' }], tags: [], image_path: null, is_visible: true })

async function loadDemos() {
  loadError.value = ''
  try {
    demos.value = isAuthenticated.value ? await api.listAdminDemos() : await api.listDemos()
  } catch (err) {
    loadError.value = err.message
  }
}

function resetEditor() {
  editingId.value = null
  currentDemo.value = { title: '', description: '', links: [{ label: '', url: '' }], tags: [], image_path: null, is_visible: true }
}

function showError(message) {
  formMessage.value = message
  formMessageType.value = 'error'
}

function startEdit(demo) {
  editingId.value = demo.id
  currentDemo.value = {
    title: demo.title,
    description: demo.description,
    image_path: demo.image_path || null,
    is_visible: demo.is_visible ?? true,
    tags: Array.isArray(demo.tags) ? [...demo.tags] : [],
    links: demo.links.length ? demo.links.map((item) => ({ ...item })) : [{ label: '', url: '' }]
  }
  formMessage.value = ''
}

function buildSubtitle(demo) {
  const parts = [`${demo.links.length} link(s)`]
  if (demo.tags?.length) parts.push(demo.tags.join(', '))
  return parts.join(' • ')
}

function imageUrl(path) {
  return path?.startsWith('http') ? path : `${api.getApiBase()}${path}`
}

async function handleLogin() {
  loggingIn.value = true
  formMessage.value = ''
  try {
    await api.login(credentials.value.username, credentials.value.password)
    isAuthenticated.value = true
    formMessage.value = 'Signed in successfully.'
    formMessageType.value = 'success'
    await loadDemos()
  } catch (err) {
    showError(err.message)
  } finally {
    loggingIn.value = false
  }
}

async function logout() {
  api.logout()
  isAuthenticated.value = false
  resetEditor()
  formMessage.value = 'Signed out.'
  formMessageType.value = 'success'
  await loadDemos()
}

async function handleSubmit(payload) {
  saving.value = true
  formMessage.value = ''
  try {
    if (editingId.value) {
      await api.updateDemo(editingId.value, payload)
      formMessage.value = 'Demo updated successfully.'
    } else {
      await api.createDemo(payload)
      formMessage.value = 'Demo created successfully.'
    }
    formMessageType.value = 'success'
    resetEditor()
    await loadDemos()
  } catch (err) {
    showError(err.message)
    if (err.message.toLowerCase().includes('auth') || err.message.toLowerCase().includes('token')) {
      isAuthenticated.value = false
    }
  } finally {
    saving.value = false
  }
}

async function toggleVisibility(demo) {
  try {
    await api.updateDemoVisibility(demo.id, !demo.is_visible)
    if (editingId.value === demo.id) {
      currentDemo.value.is_visible = !demo.is_visible
    }
    formMessage.value = demo.is_visible ? 'Demo hidden.' : 'Demo shown.'
    formMessageType.value = 'success'
    await loadDemos()
  } catch (err) {
    showError(err.message)
  }
}

async function removeDemo(demo) {
  const confirmed = window.confirm(`Delete the demo \"${demo.title}\"?`)
  if (!confirmed) return

  try {
    await api.deleteDemo(demo.id)
    if (editingId.value === demo.id) {
      resetEditor()
    }
    formMessage.value = 'Demo deleted.'
    formMessageType.value = 'success'
    await loadDemos()
  } catch (err) {
    showError(err.message)
  }
}

onMounted(loadDemos)
</script>
