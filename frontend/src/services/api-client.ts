// FastAPI backend client for sindankantei system
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8502'

// TypeScript interfaces for API data
export interface KyuseiRequest {
  birth_date: string  // YYYY-MM-DD format
  gender: 'male' | 'female'
}

export interface SeimeiRequest {
  name: string  // "姓 名" format
}

export interface DiagnosisRequest {
  client_name: string
  birth_date: string
  gender: 'male' | 'female'
  name_for_seimei?: string
  diagnosis_pattern?: string  // "kyusei_only" | "seimei_only" | "all"
  birth_time?: string  // 出生時間（HH:MM形式、任意）
}

export interface DiagnosisResult {
  id: string
  client_name: string
  created_at: string
  kyusei_result?: any
  seimei_result?: any
  status: 'processing' | 'completed' | 'failed'
  error_message?: string
  diagnosis_pattern?: string  // "kyusei_only" | "seimei_only" | "all"
}

export interface TemplateSettings {
  id: number
  user_id: number
  logo_url?: string
  logo_file_size?: number
  business_name: string
  operator_name: string
  color_theme: string
  font_family: string
  font_size?: string
  layout_style: string
  design_pattern?: string
  custom_css?: string
  settings_version: string
  created_at: string
  updated_at: string
}

export interface TemplateSettingsRequest {
  business_name: string
  operator_name: string
  color_theme: string
  font_family: string
  font_size?: string
  layout_style: string
  design_pattern?: string
  custom_css?: string
}

export interface TemplateSettingsUpdate {
  business_name?: string
  operator_name?: string
  color_theme?: string
  font_family?: string
  font_size?: string
  layout_style?: string
  design_pattern?: string
  custom_css?: string
  logo_url?: string
}

export interface LogoUploadResponse {
  success: boolean
  logo_url: string
  file_size: number
  message: string
}

// 認証関連の型定義
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user_id: number
  is_superuser: boolean
  subscription_status: string
  utage_user_id?: string
}

export interface UserResponse {
  id: number
  email: string
  business_name?: string
  operator_name?: string
  subscription_status: string
  utage_user_id?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface MessageResponse {
  success: boolean
  message: string
}

export interface RegistrationRequest {
  email: string
  password: string
  business_name?: string
  operator_name?: string
  utage_user_id?: string
}

export interface RegistrationResponse {
  success: boolean
  message: string
  user_id: number
  email: string
}

// HTTP client class using user store for authentication
class ApiClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  setToken(token: string) {
    // This method is kept for compatibility but the actual token is managed by user store
    console.warn('setToken is deprecated. Use user store for authentication.')
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options?.headers as Record<string, string>),
    }

    // Get token from user store
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token')
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    return response.json()
  }

  // Health check
  async health() {
    return this.request<{ status: string; timestamp: string }>('/health')
  }

  // Kyusei (Nine Star Astrology) API
  async calculateKyusei(request: KyuseiRequest) {
    return this.request<{ success: boolean; data: any; input: any }>('/api/kyusei', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // Seimei (Name Divination) API
  async calculateSeimei(request: SeimeiRequest) {
    return this.request<{ success: boolean; data: any; input: any }>('/api/seimei', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // Diagnosis (Combined) API
  async createDiagnosis(request: DiagnosisRequest) {
    return this.request<{ success: boolean; diagnosis_id: string; status: string; message: string }>('/api/diagnosis', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getDiagnosis(diagnosisId: string, adminMode: boolean = false) {
    const params = adminMode ? `?admin_mode=true` : ''
    return this.request<DiagnosisResult>(`/api/diagnosis/${diagnosisId}${params}`)
  }

  async listDiagnoses() {
    return this.request<{ diagnoses: DiagnosisResult[] }>('/api/diagnosis')
  }

  // PDF Generation API
  async generatePDF(diagnosisId: string) {
    return this.request<{ success: boolean; pdf_url: string; filename: string; message: string }>(`/api/diagnosis/${diagnosisId}/pdf`, {
      method: 'POST',
    })
  }

  async downloadPDF(diagnosisId: string) {
    return this.request<{ message: string; diagnosis_id: string }>(`/api/diagnosis/${diagnosisId}/pdf/download`)
  }

  // Template Settings API
  async getTemplateSettings() {
    return this.request<TemplateSettings>('/api/template/settings')
  }

  async updateTemplateSettings(settings: TemplateSettingsUpdate) {
    const response = await this.request<{success: boolean, message: string, data: TemplateSettings}>('/api/template/update', {
      method: 'PUT',
      body: JSON.stringify(settings),
    })
    return response.data
  }

  async uploadLogo(file: File) {
    const formData = new FormData()
    formData.append('logo_file', file)

    const url = `${this.baseURL}/api/template/upload-logo`
    const headers: Record<string, string> = {}

    // Get token from localStorage like other methods
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token')
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    return response.json() as Promise<LogoUploadResponse>
  }

  async deleteLogo() {
    return this.request<{ success: boolean; message: string }>('/api/template/logo', {
      method: 'DELETE',
    })
  }

  // 認証API
  async login(credentials: LoginRequest) {
    return this.request<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
  }

  async logout() {
    return this.request<MessageResponse>('/api/auth/logout', {
      method: 'POST',
    })
  }

  async verifyToken() {
    return this.request<UserResponse>('/api/auth/verify')
  }

  async register(registrationData: RegistrationRequest) {
    return this.request<RegistrationResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(registrationData),
    })
  }

  async promoteToAdmin(credentials: LoginRequest) {
    return this.request<MessageResponse>('/api/auth/promote-to-admin', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
  }

  // 管理者用API
  async getUsers(skip: number = 0, limit: number = 100, search?: string) {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString()
    })
    if (search) {
      params.append('search', search)
    }
    return this.request<any[]>(`/api/admin/users?${params}`)
  }

  async getSystemStats() {
    return this.request<any>('/api/admin/stats')
  }

  async getUserDetail(userId: number) {
    return this.request<UserResponse>(`/api/admin/users/${userId}`)
  }

  async updateUser(userId: number, updateData: any) {
    return this.request<any>(`/api/admin/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    })
  }

  async testAdminAccess() {
    return this.request<any>('/api/admin/test-admin')
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL)

// Helper functions for compatibility
export const setAuthToken = (token: string | undefined) => {
  if (token) {
    apiClient.setToken(token)
  }
}

export const getAuthToken = () => {
  // For now, return undefined since we don't store the token locally yet
  return undefined
}