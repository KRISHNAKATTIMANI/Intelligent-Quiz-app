import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (expired/invalid token)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  signup: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
};

// Category APIs
export const categoryAPI = {
  getAll: () => api.get('/categories/'),
  getById: (id) => api.get(`/categories/${id}`),
  getSubcategories: (id) => api.get(`/categories/${id}/subcategories`),
  getTopics: (subcategoryId) => api.get(`/subcategories/${subcategoryId}/topics`),
};

// Quiz APIs
export const quizAPI = {
  generate: (data) => api.post('/quiz/generate', data),
  getAll: () => api.get('/quiz/quizzes'),  // Changed from '/quizzes' to '/quiz/quizzes'
  getById: (id) => api.get(`/quiz/${id}`),  // Changed from '/quizzes/:id' to '/quiz/:id'
  start: (id) => api.post(`/quiz/${id}/start`),
  submit: (attemptId, answers) => api.post(`/attempt/${attemptId}/submit`, { answers }),
};

// Dashboard APIs
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentAttempts: () => api.get('/dashboard/recent-attempts'),
  getRecommendations: () => api.get('/dashboard/recommendations'),
};

// File Upload APIs
export const fileAPI = {
  upload: (formData) => {
    const token = localStorage.getItem('token');
    return axios.post('http://localhost:5000/api/upload/upload', formData, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      },
    });
  },
  generateQuiz: (fileId, data) => api.post(`/upload/${fileId}/generate-quiz`, data),
};

export default api;
