import { useEffect, useState } from 'react';

const defaultConsent = {
  necessary: true,
  analytics: false,
  marketing: false,
};

function loadConsent() {
  try {
    const raw = localStorage.getItem('cookie_consent');
    if (!raw) return null;
    return { ...defaultConsent, ...JSON.parse(raw) };
  } catch {
    return null;
  }
}

function saveConsent(consent) {
  localStorage.setItem('cookie_consent', JSON.stringify(consent));
}

export function hasConsent(category) {
  const c = loadConsent();
  return !!(c && c[category]);
}

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const [consent, setConsent] = useState(defaultConsent);

  useEffect(() => {
    const existing = loadConsent();
    if (!existing) {
      setVisible(true);
    } else {
      setConsent(existing);
    }
  }, []);

  const acceptAll = () => {
    const all = { necessary: true, analytics: true, marketing: true };
    saveConsent(all);
    setConsent(all);
    setVisible(false);
  };

  const saveChoices = () => {
    const current = { ...consent, necessary: true };
    saveConsent(current);
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center pointer-events-none">
      <div className="pointer-events-auto m-4 w-full max-w-2xl rounded-lg bg-white dark:bg-gray-800 shadow-2xl border border-gray-200 dark:border-gray-700">
        <div className="p-4 sm:p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Nós usamos cookies</h3>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
            Utilizamos cookies necessários para o funcionamento do site e, com seu consentimento,
            cookies de análise e marketing para melhorar a sua experiência.
          </p>

          <div className="mt-4 space-y-3">
            <label className="flex items-start gap-3">
              <input type="checkbox" checked disabled className="mt-1" />
              <span className="text-sm text-gray-800 dark:text-gray-200">
                Necessários — essenciais para funcionamento do site.
              </span>
            </label>

            <label className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={consent.analytics}
                onChange={(e) => setConsent((c) => ({ ...c, analytics: e.target.checked }))}
                className="mt-1"
              />
              <span className="text-sm text-gray-800 dark:text-gray-200">
                Analíticos — ajudam a entender o uso para melhorar o produto.
              </span>
            </label>

            <label className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={consent.marketing}
                onChange={(e) => setConsent((c) => ({ ...c, marketing: e.target.checked }))}
                className="mt-1"
              />
              <span className="text-sm text-gray-800 dark:text-gray-200">
                Marketing — personalização e ofertas relevantes.
              </span>
            </label>
          </div>

          <div className="mt-6 flex flex-col sm:flex-row gap-3 sm:justify-end">
            <button
              onClick={acceptAll}
              className="w-full sm:w-auto inline-flex justify-center rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Aceitar todos
            </button>
            <button
              onClick={saveChoices}
              className="w-full sm:w-auto inline-flex justify-center rounded-md border px-4 py-2 text-gray-900 dark:text-gray-100 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Salvar preferências
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
