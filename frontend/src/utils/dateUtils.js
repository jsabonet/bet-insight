/**
 * Utilitários de Data/Hora para Moçambique (Africa/Maputo - UTC+2)
 * 
 * O backend Django já retorna datas em UTC timezone-aware.
 * O JavaScript automaticamente converte para o timezone local do navegador.
 * 
 * Para garantir exibição correta em Moçambique:
 * - Use estas funções ao invés de Date.prototype direto
 * - Todas as datas vêm do backend em formato ISO 8601 com timezone
 */

const MOZAMBIQUE_TIMEZONE = 'Africa/Maputo';
const LOCALE = 'pt-MZ'; // Português de Moçambique

/**
 * Formata data para exibição completa
 * @param {string|Date} dateString - Data em formato ISO ou objeto Date
 * @returns {string} - Ex: "29 de dezembro de 2025, 16:00"
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  
  return new Intl.DateTimeFormat(LOCALE, {
    timeZone: MOZAMBIQUE_TIMEZONE,
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false, // Formato 24h
  }).format(date);
};

/**
 * Formata apenas a data (sem hora)
 * @param {string|Date} dateString
 * @returns {string} - Ex: "29 de dezembro de 2025"
 */
export const formatDate = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  
  return new Intl.DateTimeFormat(LOCALE, {
    timeZone: MOZAMBIQUE_TIMEZONE,
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

/**
 * Formata data curta
 * @param {string|Date} dateString
 * @returns {string} - Ex: "29/12/2025"
 */
export const formatDateShort = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  
  return new Intl.DateTimeFormat(LOCALE, {
    timeZone: MOZAMBIQUE_TIMEZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);
};

/**
 * Formata apenas a hora
 * @param {string|Date} dateString
 * @returns {string} - Ex: "16:00"
 */
export const formatTime = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  
  return new Intl.DateTimeFormat(LOCALE, {
    timeZone: MOZAMBIQUE_TIMEZONE,
    hour: '2-digit',
    minute: '2-digit',
    hour12: false, // Formato 24h
  }).format(date);
};

/**
 * Formata data relativa (Hoje, Amanhã, ou data)
 * @param {string|Date} dateString
 * @returns {object} - { day: 'Hoje', time: '16:00' }
 */
export const formatMatchDate = (dateString) => {
  if (!dateString) return { day: '-', time: '-' };
  
  const date = new Date(dateString);
  
  // Criar datas no timezone de Moçambique
  const now = new Date();
  const options = { timeZone: MOZAMBIQUE_TIMEZONE };
  
  const matchDay = new Intl.DateTimeFormat('en-CA', { 
    ...options, 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  }).format(date);
  
  const todayDay = new Intl.DateTimeFormat('en-CA', { 
    ...options, 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  }).format(now);
  
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const tomorrowDay = new Intl.DateTimeFormat('en-CA', { 
    ...options, 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  }).format(tomorrow);
  
  let dayLabel;
  
  if (matchDay === todayDay) {
    dayLabel = 'Hoje';
  } else if (matchDay === tomorrowDay) {
    dayLabel = 'Amanhã';
  } else {
    // Ex: "Sáb, 30 Dez"
    dayLabel = new Intl.DateTimeFormat(LOCALE, {
      timeZone: MOZAMBIQUE_TIMEZONE,
      weekday: 'short',
      day: '2-digit',
      month: 'short',
    }).format(date);
  }
  
  const time = formatTime(dateString);
  
  return { day: dayLabel, time };
};

/**
 * Retorna diferença em dias
 * @param {string|Date} dateString
 * @returns {number} - Dias até a data (negativo se passou)
 */
export const getDaysUntil = (dateString) => {
  if (!dateString) return 0;
  
  const date = new Date(dateString);
  const now = new Date();
  
  const diffMs = date - now;
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
  
  return diffDays;
};

/**
 * Verifica se a partida é hoje
 * @param {string|Date} dateString
 * @returns {boolean}
 */
export const isToday = (dateString) => {
  if (!dateString) return false;
  
  const { day } = formatMatchDate(dateString);
  return day === 'Hoje';
};

/**
 * Verifica se a partida está acontecendo agora (com margem de 2h)
 * @param {string|Date} dateString
 * @param {number} marginHours - Margem em horas antes/depois
 * @returns {boolean}
 */
export const isLiveOrSoon = (dateString, marginHours = 2) => {
  if (!dateString) return false;
  
  const matchDate = new Date(dateString);
  const now = new Date();
  
  const diffMs = matchDate - now;
  const diffHours = diffMs / (1000 * 60 * 60);
  
  // Se já passou menos de 2h ou falta menos de 2h
  return diffHours >= -marginHours && diffHours <= marginHours;
};

/**
 * Formata duração relativa (Ex: "há 2 horas", "em 3 dias")
 * @param {string|Date} dateString
 * @returns {string}
 */
export const formatRelativeTime = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  const now = new Date();
  
  const diffMs = now - date;
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffSeconds < 60) {
    return 'agora mesmo';
  } else if (diffMinutes < 60) {
    return `há ${diffMinutes} ${diffMinutes === 1 ? 'minuto' : 'minutos'}`;
  } else if (diffHours < 24) {
    return `há ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`;
  } else if (diffDays < 7) {
    return `há ${diffDays} ${diffDays === 1 : 'dia' : 'dias'}`;
  } else {
    return formatDateShort(dateString);
  }
};

/**
 * Converte string de data da API para objeto Date
 * Garante compatibilidade com diferentes formatos
 * @param {string} dateString
 * @returns {Date|null}
 */
export const parseApiDate = (dateString) => {
  if (!dateString) return null;
  
  try {
    // Formatos aceitos:
    // - ISO 8601: "2025-12-29T14:00:00Z"
    // - ISO com timezone: "2025-12-29T14:00:00+00:00"
    // - ISO sem timezone: "2025-12-29T14:00:00"
    
    return new Date(dateString);
  } catch (error) {
    console.error('Erro ao parsear data:', dateString, error);
    return null;
  }
};

export default {
  formatDateTime,
  formatDate,
  formatDateShort,
  formatTime,
  formatMatchDate,
  getDaysUntil,
  isToday,
  isLiveOrSoon,
  formatRelativeTime,
  parseApiDate,
  MOZAMBIQUE_TIMEZONE,
  LOCALE,
};
