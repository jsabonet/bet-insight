import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

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
  changePassword: (data) => api.post('/users/change-password/', data),
  deleteAccount: (password) => api.delete('/users/delete-account/', { data: { password } }),
};

// Admin endpoints
export const adminAPI = {
  getStats: () => api.get('/users/admin/stats/'),
  getUsers: (params) => api.get('/users/admin/users/', { params }),
  getUser: (id) => api.get(`/users/admin/users/${id}/`),
  updateUser: (id, data) => api.patch(`/users/admin/users/${id}/`, data),
  deleteUser: (id) => api.delete(`/users/admin/users/${id}/delete/`),
  togglePremium: (id) => api.post(`/users/admin/users/${id}/toggle_premium/`),
  resetDailyLimit: (id) => api.post(`/users/admin/users/${id}/reset_daily_limit/`),
  getAnalysesStats: () => api.get('/users/admin/analyses-stats/'),
  assignSubscription: (userId, planSlug, durationDays) =>
    api.post('/subscriptions/admin/assign-subscription/', {
      user_id: userId,
      plan_slug: planSlug,
      duration_days: durationDays,
    }),
  removeSubscription: (userId) =>
    api.post('/subscriptions/admin/remove-subscription/', { user_id: userId }),
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
  getApiDetail: (id) => api.get('/matches/api_detail/', { params: { id } }),
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
  // Planos
  getPlans: () => api.get('/subscriptions/plans/'),
  getPremiumPlans: () => api.get('/subscriptions/plans/premium/'),
  getPlanDetails: (slug) => api.get(`/subscriptions/plans/${slug}/`),
  
  // Assinaturas
  getMySubscription: () => api.get('/subscriptions/my-subscription/'),
  cancelSubscription: () => api.post('/subscriptions/cancel/'),
  getHistory: () => api.get('/subscriptions/history/'),
  
  // Pagamentos
  createPayment: (data) => api.post('/subscriptions/payments/create/', data),
  checkPaymentStatus: (txId) => api.get(`/subscriptions/payments/check/${txId}/`),
  getMyPayments: () => api.get('/subscriptions/payments/my-payments/'),
};

// Legacy payment endpoint (manter compatibilidade)
export const paymentsAPI = {
  getAll: () => api.get('/subscriptions/payments/my-payments/'),
  createPayment: (data) => api.post('/subscriptions/payments/create/', data),
};
