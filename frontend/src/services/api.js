import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.message || '网络请求失败'
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(new Error(message))
  }
)

export const userApi = {
  register: (data) => api.post('/user/register', data),
  login: (data) => api.post('/user/login', data),
  getInfo: () => api.get('/user/info'),
  logout: () => api.post('/user/logout'),
}

export const examApi = {
  start: (questionCount) => api.post('/exam/start', questionCount ? { question_count: questionCount } : {}),
  submit: (examId, answers) => api.post('/exam/submit', { exam_id: examId, answers }),
  getRecords: () => api.get('/exam/records'),
  getDetail: (examId) => api.get(`/exam/${examId}`),
}

export default api
