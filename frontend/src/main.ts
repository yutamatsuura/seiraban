import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './styles/globals.scss'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// フォント読み込み検出
if (document.fonts && document.fonts.ready) {
  document.fonts.ready.then(() => {
    document.documentElement.classList.add('fonts-loaded')
  })
} else {
  // フォールバック: 一定時間後にフォント読み込み完了と見なす
  setTimeout(() => {
    document.documentElement.classList.add('fonts-loaded')
  }, 1000)
}

app.mount('#app')