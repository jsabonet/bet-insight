// Helpers do Programa de Afiliados — leitura/persistência do código de indicação.

const STORAGE_KEY = 'affiliate_ref';

/**
 * Lê o código de afiliado da URL (`?ref=CODE`) e persiste em localStorage.
 * Devolve o código atual (da URL ou do localStorage) ou '' se não existir.
 */
export function captureAffiliateRef() {
  try {
    const params = new URLSearchParams(window.location.search);
    const ref = (params.get('ref') || '').trim().toUpperCase();
    if (ref) {
      localStorage.setItem(STORAGE_KEY, ref);
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
    return localStorage.getItem(STORAGE_KEY) || '';
  } catch (e) {
    return '';
  }
}

/** Remove o código de afiliado persistido (ex.: após uso no registo). */
export function clearAffiliateRef() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    // ignora
  }
}
