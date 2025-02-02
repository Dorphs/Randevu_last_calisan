import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

// Axios instance'ı oluştur
const api = axios.create({
  baseURL: API_URL,
})

// Request interceptor - token ekle
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  console.log('API Request:', config.method.toUpperCase(), config.url, config.data)
  return config
})

// Response interceptor - hata kontrolü ve debug
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.method.toUpperCase(), response.config.url, response.data)
    return response
  },
  (error) => {
    console.error('API Error:', error.config?.method.toUpperCase(), error.config?.url, error.response?.data)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Kullanıcı servisi
export const userService = {
  getAll: () => api.get('/users/'),
  getById: (id) => api.get(`/users/${id}/`),
}

// Toplantı odası servisi
export const toplantiOdasiService = {
  getAll: () => api.get('/toplanti-odalari/'),
  getById: (id) => api.get(`/toplanti-odalari/${id}/`),
  create: (data) => api.post('/toplanti-odalari/', data),
  update: (id, data) => api.put(`/toplanti-odalari/${id}/`, data),
  delete: (id) => api.delete(`/toplanti-odalari/${id}/`),
}

// Toplantı servisi
export const toplantiService = {
  getAll: () => api.get('/toplantilar/'),
  getById: (id) => api.get(`/toplantilar/${id}/`),
  create: (data) => api.post('/toplantilar/', data),
  update: (id, data) => api.put(`/toplantilar/${id}/`, data),
  delete: (id) => api.delete(`/toplantilar/${id}/`),
}

// Ziyaretçi servisi
export const ziyaretciService = {
  getAll: () => api.get('/ziyaretciler/'),
  getById: (id) => api.get(`/ziyaretciler/${id}/`),
  create: (data) => api.post('/ziyaretciler/', data),
  update: (id, data) => api.put(`/ziyaretciler/${id}/`, data),
  delete: (id) => api.delete(`/ziyaretciler/${id}/`),
}

export default api
