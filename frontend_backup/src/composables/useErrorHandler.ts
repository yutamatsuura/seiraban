/**
 * グローバルエラーハンドリング用コンポーザブル
 *
 * 統一されたエラー処理、ユーザーフレンドリーなエラーメッセージ、
 * リトライ機能、ネットワークエラー処理などを提供
 */

import { ref, computed } from 'vue'

export interface ErrorState {
  message: string
  code?: string | number
  type: 'network' | 'validation' | 'server' | 'unknown'
  retryable: boolean
  originalError?: any
}

export interface LoadingState {
  loading: boolean
  progress?: number
  message?: string
}

// グローバルエラー状態
const globalError = ref<ErrorState | null>(null)
const globalLoading = ref<LoadingState>({ loading: false })

// エラータイプ別の設定
const ERROR_CONFIGS = {
  network: {
    retryable: true,
    defaultMessage: 'ネットワーク接続を確認してください',
    icon: 'wifi_off'
  },
  validation: {
    retryable: false,
    defaultMessage: '入力内容を確認してください',
    icon: 'error'
  },
  server: {
    retryable: true,
    defaultMessage: 'サーバーエラーが発生しました',
    icon: 'error_outline'
  },
  unknown: {
    retryable: false,
    defaultMessage: '予期しないエラーが発生しました',
    icon: 'help_outline'
  }
}

export function useErrorHandler() {
  // ローカルエラー状態
  const error = ref<ErrorState | null>(null)
  const loading = ref<LoadingState>({ loading: false })

  // 計算プロパティ
  const hasError = computed(() => !!error.value)
  const hasGlobalError = computed(() => !!globalError.value)
  const isLoading = computed(() => loading.value.loading)
  const isGlobalLoading = computed(() => globalLoading.value.loading)

  /**
   * エラーを解析してErrorStateを生成
   */
  const parseError = (err: any): ErrorState => {
    // ネットワークエラー
    if (!navigator.onLine || err.message?.includes('Failed to fetch')) {
      return {
        message: 'インターネット接続を確認してください',
        type: 'network',
        retryable: true,
        originalError: err
      }
    }

    // HTTPエラー
    if (err.response) {
      const status = err.response.status
      const data = err.response.data

      if (status >= 400 && status < 500) {
        return {
          message: data?.detail || data?.message || 'リクエストが無効です',
          code: status,
          type: 'validation',
          retryable: false,
          originalError: err
        }
      }

      if (status >= 500) {
        return {
          message: 'サーバーエラーが発生しました。しばらく時間をおいてお試しください',
          code: status,
          type: 'server',
          retryable: true,
          originalError: err
        }
      }
    }

    // APIエラー（カスタムエラー）
    if (err.message) {
      return {
        message: err.message,
        type: 'server',
        retryable: false,
        originalError: err
      }
    }

    // 不明なエラー
    return {
      message: '予期しないエラーが発生しました',
      type: 'unknown',
      retryable: false,
      originalError: err
    }
  }

  /**
   * エラーを設定
   */
  const setError = (err: any, global = false) => {
    const errorState = parseError(err)

    if (global) {
      globalError.value = errorState
    } else {
      error.value = errorState
    }

    // エラーをコンソールにログ出力（開発時のデバッグ用）
    if (import.meta.env.DEV) {
      console.error('Error captured:', errorState)
    }
  }

  /**
   * エラーをクリア
   */
  const clearError = (global = false) => {
    if (global) {
      globalError.value = null
    } else {
      error.value = null
    }
  }

  /**
   * ローディング状態を設定
   */
  const setLoading = (state: boolean | LoadingState, global = false) => {
    const loadingState = typeof state === 'boolean'
      ? { loading: state }
      : state

    if (global) {
      globalLoading.value = loadingState
    } else {
      loading.value = loadingState
    }
  }

  /**
   * 非同期処理をラップしてエラーハンドリングとローディング状態を管理
   */
  const withErrorHandling = async <T>(
    asyncFn: () => Promise<T>,
    options: {
      loadingMessage?: string
      globalError?: boolean
      globalLoading?: boolean
      retryCount?: number
      retryDelay?: number
    } = {}
  ): Promise<T | null> => {
    const {
      loadingMessage = '処理中...',
      globalError = false,
      globalLoading = false,
      retryCount = 0,
      retryDelay = 1000
    } = options

    // エラーをクリア
    clearError(globalError)

    // ローディング開始
    setLoading({ loading: true, message: loadingMessage }, globalLoading)

    let lastError: any
    let attempts = 0
    const maxAttempts = retryCount + 1

    while (attempts < maxAttempts) {
      try {
        const result = await asyncFn()
        setLoading(false, globalLoading)
        return result
      } catch (err) {
        lastError = err
        attempts++

        // 最後の試行の場合はエラーを設定
        if (attempts >= maxAttempts) {
          setError(err, globalError)
          setLoading(false, globalLoading)
          return null
        }

        // リトライ可能なエラーかチェック
        const errorState = parseError(err)
        if (!errorState.retryable) {
          setError(err, globalError)
          setLoading(false, globalLoading)
          return null
        }

        // リトライ前に遅延
        if (retryDelay > 0) {
          await new Promise(resolve => setTimeout(resolve, retryDelay * attempts))
        }
      }
    }

    setError(lastError, globalError)
    setLoading(false, globalLoading)
    return null
  }

  /**
   * リトライ処理
   */
  const retry = async <T>(
    asyncFn: () => Promise<T>,
    options: { globalError?: boolean; globalLoading?: boolean } = {}
  ): Promise<T | null> => {
    clearError(options.globalError)
    return withErrorHandling(asyncFn, {
      ...options,
      retryCount: 1
    })
  }

  /**
   * 特定のエラータイプかチェック
   */
  const isErrorType = (type: ErrorState['type'], global = false) => {
    const errorState = global ? globalError.value : error.value
    return errorState?.type === type
  }

  /**
   * エラーメッセージを取得
   */
  const getErrorMessage = (global = false) => {
    const errorState = global ? globalError.value : error.value
    return errorState?.message || ''
  }

  /**
   * エラーアイコンを取得
   */
  const getErrorIcon = (global = false) => {
    const errorState = global ? globalError.value : error.value
    if (!errorState) return 'error'
    return ERROR_CONFIGS[errorState.type].icon
  }

  /**
   * リトライ可能かチェック
   */
  const canRetry = (global = false) => {
    const errorState = global ? globalError.value : error.value
    return errorState?.retryable || false
  }

  return {
    // 状態
    error: computed(() => error.value),
    globalError: computed(() => globalError.value),
    loading: computed(() => loading.value),
    globalLoading: computed(() => globalLoading.value),

    // 計算プロパティ
    hasError,
    hasGlobalError,
    isLoading,
    isGlobalLoading,

    // メソッド
    setError,
    clearError,
    setLoading,
    withErrorHandling,
    retry,
    isErrorType,
    getErrorMessage,
    getErrorIcon,
    canRetry
  }
}

/**
 * グローバルエラーとローディング状態のみを扱うコンポーザブル
 */
export function useGlobalErrorHandler() {
  const errorHandler = useErrorHandler()

  return {
    error: errorHandler.globalError,
    loading: errorHandler.globalLoading,
    hasError: errorHandler.hasGlobalError,
    isLoading: errorHandler.isGlobalLoading,
    setError: (err: any) => errorHandler.setError(err, true),
    clearError: () => errorHandler.clearError(true),
    setLoading: (state: boolean | LoadingState) => errorHandler.setLoading(state, true),
    withErrorHandling: <T>(asyncFn: () => Promise<T>, options: any = {}) =>
      errorHandler.withErrorHandling(asyncFn, { ...options, globalError: true, globalLoading: true }),
    retry: <T>(asyncFn: () => Promise<T>) =>
      errorHandler.retry(asyncFn, { globalError: true, globalLoading: true }),
    isErrorType: (type: ErrorState['type']) => errorHandler.isErrorType(type, true),
    getErrorMessage: () => errorHandler.getErrorMessage(true),
    getErrorIcon: () => errorHandler.getErrorIcon(true),
    canRetry: () => errorHandler.canRetry(true)
  }
}