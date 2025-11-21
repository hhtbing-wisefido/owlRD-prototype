/**
 * API Configuration - Auto-adapt for localhost and LAN access
 */

export const getApiBaseUrl = (): string => {
  const hostname = window.location.hostname
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1'
  
  if (isLocalhost) {
    return 'http://localhost:8000'
  }
  
  return `http://${hostname}:8000`
}

export const getWsBaseUrl = (): string => {
  const hostname = window.location.hostname
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1'
  
  if (isLocalhost) {
    return 'ws://localhost:8000'
  }
  
  return `ws://${hostname}:8000`
}

// 使用getter避免在模块加载时立即执行
const createApiConfig = () => ({
  get BASE_URL() {
    return getApiBaseUrl()
  },
  get WS_BASE_URL() {
    return getWsBaseUrl()
  },
  TIMEOUT: 30000,
  DEFAULT_TENANT_ID: '10000000-0000-0000-0000-000000000001',
})

export const API_CONFIG = createApiConfig()

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    LOGOUT: '/api/v1/auth/logout',
  },
  USERS: '/api/v1/users',
  ROLES: '/api/v1/roles',
  RESIDENTS: '/api/v1/residents',
  DEVICES: '/api/v1/devices',
  LOCATIONS: '/api/v1/locations',
  ALERTS: '/api/v1/alerts',
  CARE_QUALITY: '/api/v1/care-quality',
}

export default API_CONFIG
