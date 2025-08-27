// Environment Configuration
// This file handles environment variables for both development and production

interface EnvironmentConfig {
  apiBaseUrl: string
  wsUrl: string
  appTitle: string
}

// Get environment variables with fallbacks
const getEnvVar = (key: string, fallback: string): string => {
  // For Vite, environment variables are available at build time
  // For development, we'll use fallbacks
  return (import.meta as any).env?.[key] || fallback
}

// Environment configuration
export const env: EnvironmentConfig = {
  apiBaseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000'),
  wsUrl: getEnvVar('VITE_WS_URL', 'ws://localhost:8000'),
  appTitle: getEnvVar('VITE_APP_TITLE', 'Real-Time Speech Translator'),
}

// Helper function to get WebSocket URL from API base URL
export const getWebSocketUrl = (): string => {
  const apiBase = env.apiBaseUrl
  return `${apiBase.replace(/^http/, 'ws')}/ws`
}

// Log environment configuration (development only)
// Note: import.meta.env is available at build time in Vite
