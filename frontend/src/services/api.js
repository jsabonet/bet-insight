import axios from 'axios';

// Normaliza para terminar sempre em /api (o VITE_API_URL de produção pode vir
// com ou sem sufixo).
function normalizeApiUrl(url) {
  const base = String(url || '').replace(/\/+$/, '');
  if (!base) return 'http://localhost:8000/api';
  return base.endsWith('/api') ? base : `${base}/api`;
}

// Permite configurar o backend em runtime (docker/frontend/entrypoint.sh gera
// /config.js com window.ENV.API_URL), sem ter de reconstruir a imagem. Em dev
// o /config.js não existe e usa-se o valor do build (import.meta.env).
const API_URL = normalizeApiUrl(
  (typeof window !== 'undefined' && window.ENV && window.ENV.API_URL) ||
    import.meta.env.VITE_API_URL
);

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

export const pushAPI = {
  getStatus: () => api.get('/users/push/status/'),
  registerSubscription: (subscription) => api.post('/users/push/subscriptions/', { subscription }),
  removeSubscription: (endpoint) => api.delete('/users/push/subscriptions/', { data: { endpoint } }),
  updatePreferences: (data) => api.patch('/users/push/preferences/', data),
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
  
  // 🎯 Daily Bets Admin Actions
  generateDailyBets: () => api.post('/daily-bets/admin/generate-now/'),
  validateDailyBets: () => api.post('/daily-bets/admin/validate-now/'),
  cancelDailyBetsGeneration: () => api.post('/daily-bets/admin/cancel-generation/'),
  getExecutionStatus: (limit = 20) => api.get('/daily-bets/admin/execution-status/', { params: { limit } }),
  getExecutionDetail: (id) => api.get(`/daily-bets/admin/execution-detail/${id}/`),
  getGeneratorStats: () => api.get('/daily-bets/admin/generator-stats/'),
  getGenerationProgress: () => api.get('/daily-bets/admin/generation-progress/'),
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
  getPastMatches: (date) => api.get('/matches/past_matches/', { params: { date } }),
  getApiDetail: (id) => api.get('/matches/api_detail/', { params: { id } }),
  getApiDetailEnrichment: (id, group) => api.get('/matches/api_detail_enrichment/', { params: { id, group } }),
  searchMatches: (query) => api.get('/matches/search/', { params: { q: query } }),
  analyzeMatch: (matchId) => api.post(`/matches/${matchId}/analyze/`),
  quickAnalyze: (data) => api.post('/matches/quick_analyze/', data),
  statisticalPreview: (data) => api.post('/matches/statistical_preview/', data), // Novo endpoint rápido
  getLiveProbabilities: (matchId) => api.get(`/matches/${matchId}/live_probabilities/`), // ✅ Probabilidades ao vivo
  
  // 🚀 Endpoint unificado com cache inteligente
  unifiedAnalysis: (matchId, strategy, includeAI = true, forceRefresh = true) =>
    api.post(`/matches/${matchId}/unified-analysis/`, {
      strategy,
      include_ai: includeAI,
      force_refresh: forceRefresh
    }),
};

// Leagues endpoints
export const leaguesAPI = {
  getAll: () => api.get('/leagues/'),
};

// Analysis endpoints
export const analysisAPI = {
  getAll: (params) => api.get('/analyses/', { params }),
  getUserAnalyses: (page = 1, search = '') => {
    const params = new URLSearchParams({ page });
    if (search) params.append('search', search);
    return api.get(`/analyses/?${params.toString()}`);
  },
  requestAnalysis: (matchId, forceRecalculate = false) => api.post('/analyses/request_analysis/', { 
    match_id: matchId,
    force_recalculate: forceRecalculate 
  }),
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
  createVpayPayment: (data) => api.post('/subscriptions/payments/vpay/create/', data),
  checkPaymentStatus: (txId) => api.get(`/subscriptions/payments/check/${txId}/`),
  getMyPayments: () => api.get('/subscriptions/payments/my-payments/'),
};

// Legacy payment endpoint (manter compatibilidade)
export const paymentsAPI = {
  getAll: () => api.get('/subscriptions/payments/my-payments/'),
};

// Affiliates endpoints (Programa de Afiliados)
export const affiliateAPI = {
  // Público
  trackClick: (code) => api.post('/affiliates/track/', { code }),
  validateCode: (code) => api.post('/affiliates/validate-code/', { code }),

  // Afiliado (autenticado)
  apply: (data) => api.post('/affiliates/apply/', data),
  getMe: () => api.get('/affiliates/me/'),
  updateMe: (data) => api.patch('/affiliates/me/', data),
  getStats: () => api.get('/affiliates/me/stats/'),
  getCommissions: (status) => api.get('/affiliates/me/commissions/', { params: status ? { status } : {} }),
  getReferrals: () => api.get('/affiliates/me/referrals/'),
  getWithdrawals: () => api.get('/affiliates/me/withdrawals/'),
  withdraw: (amount) => api.post('/affiliates/me/withdraw/', { amount }),
};

// Admin affiliates endpoints
export const affiliateAdminAPI = {
  getOverview: () => api.get('/affiliates/admin/overview/'),
  getAffiliates: (params) => api.get('/affiliates/admin/affiliates/', { params }),
  getCommissions: (params) => api.get('/affiliates/admin/commissions/', { params }),
  getWithdrawals: (params) => api.get('/affiliates/admin/withdrawals/', { params }),
  approveCommission: (id) => api.post(`/affiliates/admin/commissions/${id}/approve/`),
  markPaid: (id) => api.post(`/affiliates/admin/commissions/${id}/mark-paid/`),
  processWithdrawal: (id) => api.post(`/affiliates/admin/withdrawals/${id}/process/`),
  completeWithdrawal: (id, transactionReference) => api.post(`/affiliates/admin/withdrawals/${id}/complete/`, { transaction_reference: transactionReference }),
  rejectWithdrawal: (id, reason) => api.post(`/affiliates/admin/withdrawals/${id}/reject/`, { reason }),
  setTier: (id, data) => api.post(`/affiliates/admin/affiliates/${id}/set-tier/`, data),
  toggleSuspend: (id) => api.post(`/affiliates/admin/affiliates/${id}/toggle-suspend/`),
  exportCommissions: () => api.get('/affiliates/admin/commissions/export/', { responseType: 'blob' }),
};
