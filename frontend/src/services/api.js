import axios from 'axios'
const api = axios.create({ baseURL: '/api', timeout: 15000 })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use((response) => response.data, (error) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('token'); localStorage.removeItem('user')
  }
  return Promise.reject(new Error(error.response?.data?.message || '网络请求失败'))
})
export const userApi = {
  register: (data) => api.post('/user/register', data), login: (data) => api.post('/user/login', data),
  getInfo: () => api.get('/user/info'), logout: () => api.post('/user/logout'),
}
export const examApi = {
  list: () => api.get('/exams'), create: (data) => api.post('/exams', data),
  start: (id) => api.post(`/exams/${id}/start`),
  submit: (attemptId, answers) => api.post(`/exams/attempts/${attemptId}/submit`, { answers }),
  records: () => api.get('/exams/records'), detail: (id) => api.get(`/exams/records/${id}`),
}
export const statisticApi = {
  overview: () => api.get('/statistics/overview'), wordcloud: (days = 7) => api.get(`/statistics/wordcloud?days=${days}`),
}
export default api
