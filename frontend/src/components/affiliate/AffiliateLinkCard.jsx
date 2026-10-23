import { useState } from 'react';
import { Link2, Copy, Check } from 'lucide-react';

export default function AffiliateLinkCard({ referralLink, code }) {
  const [copied, setCopied] = useState('');

  const copy = async (value, key) => {
    try {
      await navigator.clipboard.writeText(value);
    } catch (e) {
      // Fallback para navegadores sem clipboard API.
      const ta = document.createElement('textarea');
      ta.value = value;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    setCopied(key);
    setTimeout(() => setCopied(''), 2000);
  };

  return (
    <div className="card animate-slide-up">
      <div className="flex items-center gap-2 mb-3">
        <Link2 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        <h3 className="font-bold text-gray-900 dark:text-gray-100">Seu Link de Indicação</h3>
      </div>

      <div className="rounded-xl bg-gray-50 dark:bg-gray-700/50 p-3 mb-3">
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Link completo</p>
        <p className="text-sm font-mono break-all text-gray-800 dark:text-gray-200">{referralLink}</p>
      </div>

      <div className="rounded-xl bg-gray-50 dark:bg-gray-700/50 p-3 mb-4">
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Código</p>
        <p className="text-xl font-bold tracking-widest text-primary-600 dark:text-primary-400">{code}</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => copy(referralLink, 'link')}
          className="flex items-center justify-center gap-2 py-3 rounded-xl bg-primary-600 hover:bg-primary-700 text-white font-semibold transition-all"
        >
          {copied === 'link' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          {copied === 'link' ? 'Copiado!' : 'Copiar link'}
        </button>
        <button
          onClick={() => copy(code, 'code')}
          className="flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-primary-600 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 font-semibold transition-all"
        >
          {copied === 'code' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          {copied === 'code' ? 'Copiado!' : 'Copiar código'}
        </button>
      </div>
    </div>
  );
}
