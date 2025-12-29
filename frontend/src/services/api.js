import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Criar instância do axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para lidar com erros de autenticação
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/users/auth/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/users/auth/register/', data),
  login: (data) => api.post('/users/auth/login/', data),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  getProfile: () => api.get('/users/profile/'),
  updateProfile: (data) => api.patch('/users/profile/', data),
  getStats: () => api.get('/users/stats/'),
};

// Matches endpoints
export const matchesAPI = {
  getAll: (params) => api.get('/matches/', { params }),
  getUpcoming: () => api.get('/matches/upcoming/'),
  getToday: () => api.get('/matches/today/'),
  getLive: () => api.get('/matches/live/'),
  getDetail: (id) => api.get(`/matches/${id}/`),
  
  // Novos endpoints - Integração com APIs externas
  getFromAPI: (date) => api.get('/matches/from_api/', { params: { date } }),
  analyzeMatch: (matchId) => api.post(`/matches/${matchId}/analyze/`),
  quickAnalyze: (data) => api.post('/matches/quick_analyze/', data),
};

// Leagues endpoints
export const leaguesAPI = {
  getAll: () => api.get('/leagues/'),
};

// Analysis endpoints
export const analysisAPI = {
  getAll: (params) => api.get('/analyses/', { params }),
  getUserAnalyses: () => api.get('/analyses/'),
  requestAnalysis: (matchId) => api.post('/analyses/request_analysis/', { match_id: matchId }),
  getMyStats: () => api.get('/analyses/my_stats/'),
};

// Subscriptions endpoints
export const subscriptionsAPI = {
  getAll: () => api.get('/subscriptions/'),
  getCurrent: () => api.get('/subscriptions/current/'),
  cancel: (id) => api.post(`/subscriptions/${id}/cancel/`),
};

// Payments endpoints
export const paymentsAPI = {
  getAll: () => api.get('/payments/'),
  createPayment: (data) => api.post('/payments/create_payment/', data),
};
