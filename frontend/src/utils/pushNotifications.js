import { pushAPI } from '../services/api';

function decodeApplicationServerKey(encodedKey) {
  const padding = '='.repeat((4 - (encodedKey.length % 4)) % 4);
  const base64 = `${encodedKey.replace(/-/g, '+').replace(/_/g, '/')}${padding}`;
  const rawData = window.atob(base64);
  return Uint8Array.from(rawData, (character) => character.charCodeAt(0));
}

export async function createPushSubscription(publicKey) {
  if (!window.isSecureContext || !('serviceWorker' in navigator) || !('PushManager' in window)) {
    throw new Error('Este navegador não suporta notificações push neste endereço.');
  }

  if (!('Notification' in window)) {
    throw new Error('Este navegador não suporta notificações push.');
  }

  let permission = Notification.permission;
  if (permission === 'default') {
    permission = await Notification.requestPermission();
  }
  if (permission !== 'granted') {
    throw new Error('Permita notificações do PlacarCerto nas definições do navegador.');
  }

  const registration = await navigator.serviceWorker.ready;
  let subscription = await registration.pushManager.getSubscription();
  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: decodeApplicationServerKey(publicKey),
    });
  }

  await pushAPI.registerSubscription(subscription.toJSON());
  return subscription;
}