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
    id: 'verified_ticket',
    label: 'Bilhete verificado',
    hint: 'Bilhete múltiplo gerado antes dos jogos e que ganhou todas as seleções.',
  },
  {
    id: 'daily_hits',
    label: 'Acertos do dia',
    hint: 'Seleções individuais vencedoras. Não representa um bilhete completo.',
  },
  {
    id: 'simulation',
    label: 'Simulação pós-jogo',
    hint: 'Bilhete montado depois dos resultados. Sai sempre com marca de água.',
  },
];

export default socialProofAPI;
