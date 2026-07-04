import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const client = axios.create({ baseURL })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('jc_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !err.config?.url?.includes('/auth/')) {
      localStorage.removeItem('jc_token')
      clearSystemInfoCache()
      if (!location.pathname.startsWith('/login')) location.assign('/login')
    }
    return Promise.reject(err)
  },
)

// System info (memory/LLM backend) is static per session — fetch it once and share.
let _systemInfo
export function getSystemInfo() {
  if (!_systemInfo) _systemInfo = client.get('/dashboard/system').then((r) => r.data)
  return _systemInfo
}

export function clearSystemInfoCache() {
  _systemInfo = null
}

// Pull a human-friendly message out of a FastAPI error response.
export function errMessage(err, fallback = 'Something went wrong') {
  const d = err?.response?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d) && d[0]?.msg) return d[0].msg
  return err?.message || fallback
}

export default client
