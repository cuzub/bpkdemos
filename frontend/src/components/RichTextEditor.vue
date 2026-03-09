<template>
  <div class="rte-shell">
    <div class="rte-toolbar">
      <v-btn size="small" variant="text" icon="mdi-format-bold" @click="exec('bold')" />
      <v-btn size="small" variant="text" icon="mdi-format-italic" @click="exec('italic')" />
      <v-btn size="small" variant="text" icon="mdi-format-underline" @click="exec('underline')" />
      <v-divider vertical class="mx-1" />
      <v-btn size="small" variant="text" icon="mdi-format-list-bulleted" @click="exec('insertUnorderedList')" />
      <v-btn size="small" variant="text" icon="mdi-format-list-numbered" @click="exec('insertOrderedList')" />
      <v-divider vertical class="mx-1" />
      <v-btn size="small" variant="text" icon="mdi-link-variant" @click="insertLink" />
      <v-btn size="small" variant="text" icon="mdi-image-outline" :loading="uploading" @click="pickImage" />
      <v-btn size="small" variant="text" icon="mdi-format-clear" @click="exec('removeFormat')" />
      <input ref="fileInput" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="d-none" @change="onFileChange" />
    </div>

    <div
      ref="editorRef"
      class="rte-editor"
      contenteditable="true"
      :data-placeholder="placeholder"
      @input="emitContent"
      @blur="emitContent"
      @paste="handlePaste"
    />
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Enter text...' },
  uploadImage: { type: Function, default: null }
})

const emit = defineEmits(['update:modelValue', 'error'])

const editorRef = ref(null)
const fileInput = ref(null)
const uploading = ref(false)
let lastRange = null

function syncFromModel(value) {
  if (!editorRef.value) return
  const normalizedCurrent = normalizeHtml(editorRef.value.innerHTML)
  const normalizedIncoming = normalizeHtml(value || '')
  if (normalizedCurrent !== normalizedIncoming) {
    editorRef.value.innerHTML = value || ''
  }
}

function normalizeHtml(html) {
  return (html || '')
    .replace(/<p><br><\/p>/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function saveSelection() {
  const selection = window.getSelection()
  if (selection && selection.rangeCount > 0) {
    lastRange = selection.getRangeAt(0)
  }
}

function restoreSelection() {
  const selection = window.getSelection()
  if (selection && lastRange) {
    selection.removeAllRanges()
    selection.addRange(lastRange)
  }
}

function focusEditor() {
  editorRef.value?.focus()
  restoreSelection()
}

function exec(command, value = null) {
  focusEditor()
  document.execCommand(command, false, value)
  emitContent()
  saveSelection()
}

function insertLink() {
  const url = window.prompt('Link URL:', 'https://')
  if (!url) return
  exec('createLink', url)
}

function pickImage() {
  fileInput.value?.click()
}

async function onFileChange(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (!props.uploadImage) {
    emit('error', 'Image upload is unavailable.')
    return
  }
  uploading.value = true
  try {
    const url = await props.uploadImage(file)
    if (!url) return
    focusEditor()
    document.execCommand('insertImage', false, url)
    emitContent()
  } catch (error) {
    emit('error', error?.message || 'Unable to upload the image.')
  } finally {
    uploading.value = false
    saveSelection()
  }
}

function emitContent() {
  emit('update:modelValue', editorRef.value?.innerHTML || '')
}

function handlePaste(event) {
  const html = event.clipboardData?.getData('text/html')
  const text = event.clipboardData?.getData('text/plain')
  event.preventDefault()
  focusEditor()
  if (html) {
    document.execCommand('insertHTML', false, sanitizeIncomingHtml(html))
  } else if (text) {
    document.execCommand('insertText', false, text)
  }
  emitContent()
}

function sanitizeIncomingHtml(html) {
  return html.replace(/<(?!\/?(p|br|strong|b|em|i|u|ul|ol|li|a|img)\b)[^>]*>/gi, '')
}

watch(() => props.modelValue, (value) => syncFromModel(value))

onMounted(async () => {
  await nextTick()
  syncFromModel(props.modelValue)
  editorRef.value?.addEventListener('keyup', saveSelection)
  editorRef.value?.addEventListener('mouseup', saveSelection)
})
</script>
