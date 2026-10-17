import api from './api';

export const dailyBetsAPI = {
  /**
   * Busca bilhetes do dia (ou de uma data específica para admins)
   * @param {string} [date] - Data no formato YYYY-MM-DD (opcional)
   */
  getToday: (date) => {
    const query = date ? `?date=${date}` : '';
    return api.get(`/daily-bets/today/${query}`);
  },

  /**
   * Busca histórico de bilhetes
   * @param {number} days - Número de dias (default: 30)
   */
  getHistory: (days = 30) => {
    return api.get(`/daily-bets/history/?days=${days}`);
  },

  /**
   * Busca estatísticas públicas
   */
  getPublicStats: () => {
    return api.get('/daily-bets/stats/');
  },

  /**
   * Busca detalhes de um bilhete específico
   * @param {number} id - ID do bilhete
   */
  getDetail: (id) => {
    return api.get(`/daily-bets/${id}/`);
  }
};
