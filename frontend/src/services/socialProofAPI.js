import api from './api';

const BASE = '/daily-bets/admin/social-proof';

export const socialProofAPI = {
  getCandidates: (date, kind) =>
    api.get(`${BASE}/candidates/`, { params: { date, kind } }),

  getTickets: (params = {}) => api.get(`${BASE}/tickets/`, { params }),

  getTicket: (id) => api.get(`${BASE}/tickets/${id}/`),

  generate: (data) => api.post(`${BASE}/generate/`, data),

  approve: (id) => api.post(`${BASE}/tickets/${id}/approve/`),

  registerExport: (id) => api.post(`${BASE}/tickets/${id}/export/`),

  discard: (id) => api.post(`${BASE}/tickets/${id}/discard/`),

  syncResults: (date) => api.post(`${BASE}/sync-results/`, { date }),
};

export const SOCIAL_PROOF_KINDS = [
  {
    id: 'simulation',
    label: 'Simulação pós-jogo',
    hint: 'Bilhete montado depois dos resultados para fins de marketing.',
  },
];

export default socialProofAPI;
