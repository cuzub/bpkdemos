import 'vuetify/styles'
import { createVuetify } from 'vuetify'

const light = {
  dark: false,
  colors: {
    background: '#f5f7fb',
    surface: '#ffffff',
    primary: '#2563eb',
    secondary: '#7c3aed'
  }
}

const dark = {
  dark: true,
  colors: {
    background: '#0f1115',
    surface: '#171923',
    primary: '#4f9cff',
    secondary: '#9b8cff'
  }
}

export default createVuetify({
  theme: {
    defaultTheme: 'dark',
    themes: { light, dark }
  }
})
