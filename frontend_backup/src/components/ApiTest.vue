<template>
  <div class="api-test">
    <h2>API接続テスト</h2>

    <!-- ヘルスチェック -->
    <div class="test-section">
      <h3>ヘルスチェック</h3>
      <button @click="testHealthCheck" :disabled="loading">
        ヘルスチェック実行
      </button>
      <div v-if="healthResult" class="result">
        <pre>{{ JSON.stringify(healthResult, null, 2) }}</pre>
      </div>
    </div>

    <!-- 鑑定システムヘルスチェック -->
    <div class="test-section">
      <h3>鑑定システムヘルスチェック</h3>
      <button @click="testKanteiHealth" :disabled="loading">
        鑑定ヘルスチェック実行
      </button>
      <div v-if="kanteiHealthResult" class="result">
        <pre>{{ JSON.stringify(kanteiHealthResult, null, 2) }}</pre>
      </div>
    </div>

    <!-- 診断一覧取得テスト -->
    <div class="test-section">
      <h3>診断一覧取得テスト</h3>
      <button @click="testGetTemplates" :disabled="loading">
        診断一覧取得実行
      </button>
      <div v-if="templatesResult" class="result">
        <pre>{{ JSON.stringify(templatesResult, null, 2) }}</pre>
      </div>
    </div>

    <!-- エラー表示 -->
    <div v-if="error" class="error">
      <h3>エラー</h3>
      <pre>{{ error }}</pre>
    </div>

    <!-- ローディング表示 -->
    <div v-if="loading" class="loading">
      テスト実行中...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiClient } from '@/services/api-client'
import axios from 'axios'

const loading = ref(false)
const error = ref<string | null>(null)
const healthResult = ref<any>(null)
const kanteiHealthResult = ref<any>(null)
const templatesResult = ref<any>(null)

const clearResults = () => {
  error.value = null
  healthResult.value = null
  kanteiHealthResult.value = null
  templatesResult.value = null
}

const testHealthCheck = async () => {
  loading.value = true
  clearResults()

  try {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8502'
    const response = await axios.get(`${baseURL}/health`)
    healthResult.value = response.data
  } catch (err: any) {
    error.value = `ヘルスチェックエラー: ${err.message}`
    console.error('Health check error:', err)
  } finally {
    loading.value = false
  }
}

const testKanteiHealth = async () => {
  loading.value = true
  clearResults()

  try {
    const response = await apiClient.health()
    kanteiHealthResult.value = response
  } catch (err: any) {
    error.value = `鑑定ヘルスチェックエラー: ${err.message}`
    console.error('Kantei health check error:', err)
  } finally {
    loading.value = false
  }
}

const testGetTemplates = async () => {
  loading.value = true
  clearResults()

  try {
    const response = await apiClient.listDiagnoses()
    templatesResult.value = response
  } catch (err: any) {
    error.value = `診断一覧取得エラー: ${err.message}`
    console.error('Get diagnoses error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.api-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 10px;
}

button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}

.result {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.error {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.loading {
  text-align: center;
  font-weight: bold;
  color: #007bff;
  margin-top: 10px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-size: 12px;
}
</style>