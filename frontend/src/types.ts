export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error'

export interface LanguagePair {
  source: string  // 'auto' for Azure auto-detection
  target: string
}

export interface TranscriptEntry {
  id: string
  type: 'partial' | 'final'
  original: string
  translated?: string
  detectedLanguage?: string  // Azure provides detected language
  confidence?: number
  timestamp: string
  isProcessing?: boolean
  hasTranslation?: boolean  // Indicates if translation is available for partial results
}

export interface WebSocketMessage {
  type: string
  [key: string]: any
}

export interface AudioCaptureConfig {
  sampleRate: number
  frameSize: number
  channels: number
}

export interface ConnectionConfig {
  backendUrl: string
  sessionId: string
  languagePair: LanguagePair
}

// Azure Speech specific types
export interface AzureSpeechConfig {
  subscriptionKey: string
  region: string
  autoLanguageDetection: boolean
  multilingualSupport: boolean
}

export interface AzureSessionInfo {
  sessionId: string
  service: 'azure_speech'
  multilingualSupport: boolean
  autoLanguageDetection: boolean
  sourceLanguage: string
  targetLanguage: string
}

// Vite environment variables
export interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_WS_URL?: string
  readonly VITE_APP_TITLE?: string
}

export interface ImportMeta {
  readonly env: ImportMetaEnv
}
