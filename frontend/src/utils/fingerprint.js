// Lightweight device fingerprint based on UA, language, timezone, screen
export function computeFingerprint() {
  try {
    const ua = navigator.userAgent || '';
    const lang = navigator.language || '';
    const tz = String(new Date().getTimezoneOffset());
    const screenRes = typeof screen !== 'undefined' ? `${screen.width}x${screen.height}x${screen.colorDepth}` : '';
    const plugins = navigator.plugins ? Array.from(navigator.plugins).map(p => p.name).join(',') : '';
    const data = [ua, lang, tz, screenRes, plugins].join('|');

    // djb2 hash to hex
    let hash = 5381;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) + hash) + data.charCodeAt(i);
      hash = hash & 0xffffffff;
    }
    return ('00000000' + (hash >>> 0).toString(16)).slice(-8);
  } catch (e) {
    return 'fp-unknown';
  }
}
