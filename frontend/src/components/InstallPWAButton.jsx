import { useEffect, useState, useCallback } from 'react';
import { Download } from 'lucide-react';

/**
 * InstallPWAButton
 * Renders an install button when the app is installable (Chrome/Edge).
 * Uses the `beforeinstallprompt` event to show a custom UI.
 */
export default function InstallPWAButton({ className = '' }) {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [installed, setInstalled] = useState(false);
  const [feedback, setFeedback] = useState('');

  const checkInstalled = useCallback(() => {
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    setInstalled(isStandalone);
    if (isStandalone) {
      setIsInstallable(false);
      setDeferredPrompt(null);
    }
  }, []);

  useEffect(() => {
    checkInstalled();

    const onBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
      setFeedback('');
    };

    const onAppInstalled = () => {
      setInstalled(true);
      setIsInstallable(false);
      setDeferredPrompt(null);
      setFeedback('Aplicativo instalado!');
    };

    window.addEventListener('beforeinstallprompt', onBeforeInstall);
    window.addEventListener('appinstalled', onAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstall);
      window.removeEventListener('appinstalled', onAppInstalled);
    };
  }, [checkInstalled]);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    try {
      const choiceResult = await deferredPrompt.prompt();
      // choiceResult.outcome: 'accepted' | 'dismissed'
      if (choiceResult.outcome === 'accepted') {
        setFeedback('Instalação aceita. Verifique seu app.');
        setIsInstallable(false);
        setDeferredPrompt(null);
      } else {
        setFeedback('Instalação cancelada.');
      }
    } catch (err) {
      setFeedback('Não foi possível instalar.');
    }
  };

  // Hide button if already installed or not installable
  if (installed || !isInstallable) {
    return feedback ? (
      <span className="text-xs text-primary-100 dark:text-gray-400">{feedback}</span>
    ) : null;
  }

  return (
    <button
      onClick={handleInstall}
      className={`w-10 h-10 bg-white/15 dark:bg-gray-700/50 backdrop-blur-sm rounded-xl flex items-center justify-center hover:bg-white/25 dark:hover:bg-gray-600/50 transition-all border border-white/30 dark:border-gray-600/50 ${className}`}
      aria-label="Instalar aplicativo"
      title="Instalar aplicativo"
    >
      <Download className="w-5 h-5" />
    </button>
  );
}
