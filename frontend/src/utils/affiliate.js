// Helpers do Programa de Afiliados — leitura/persistência do código de indicação.

import { affiliateAPI } from '../services/api';

const STORAGE_KEY = 'affiliate_ref';
const EXPIRY_KEY = 'affiliate_ref_expiry';
const ATTRIBUTION_DAYS = 30;

/**
 * Lê o código de afiliado da URL (`?ref=CODE`) e persiste em localStorage.
 * Regista também o clique no backend (analítica + cookie de atribuição).
 * Devolve o código atual (da URL ou do localStorage) ou '' se não existir.
 */
export function captureAffiliateRef() {
  try {
    const params = new URLSearchParams(window.location.search);
    const ref = (params.get('ref') || '').trim().toUpperCase();
    if (ref) {
      localStorage.setItem(STORAGE_KEY, ref);
      localStorage.setItem(
        EXPIRY_KEY,
        String(Date.now() + ATTRIBUTION_DAYS * 24 * 60 * 60 * 1000)
      );
      // Regista o clique (fire-and-forget): alimenta a métrica "Cliques"
      // e define o cookie de atribuição no backend.
      affiliateAPI.trackClick(ref).catch(() => {});
      return ref;
    }
  } catch (e) {
    // Ignora falhas de parsing (SSR/ambientes sem window).
  }
  return getAffiliateRef();
}

/** Devolve o código de afiliado persistido (ou ''). */
export function getAffiliateRef() {
  try {
    const ref = localStorage.getItem(STORAGE_KEY) || '';
    const expiresAt = Number(localStorage.getItem(EXPIRY_KEY) || 0);
    if (!ref || !expiresAt || Date.now() >= expiresAt) {
      clearAffiliateRef();
      return '';
    }
    return ref;
  } catch (e) {
    return '';
  }
}

/** Remove o código de afiliado persistido (ex.: após uso no registo). */
export function clearAffiliateRef() {
  try {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(EXPIRY_KEY);
  } catch (e) {
    // ignora
  }
}
