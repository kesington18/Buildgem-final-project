import { api } from "./api";

// Does this browser/device support web push at all?
// (On iPhone this is only true once the site is added to the Home Screen.)
export const pushSupported = () =>
  typeof window !== "undefined" && "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;

export const isIOS = () => /iphone|ipad|ipod/i.test(navigator.userAgent);

// The server gives the public key as base64url text; the browser wants raw bytes.
function keyToBytes(base64url) {
  const padded = base64url + "=".repeat((4 - (base64url.length % 4)) % 4);
  const raw = atob(padded.replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(raw, (c) => c.charCodeAt(0));
}

// This device's current push subscription, or null.
export async function currentSubscription() {
  if (!pushSupported()) return null;
  const registration = await navigator.serviceWorker.getRegistration();
  return registration ? registration.pushManager.getSubscription() : null;
}

// Ask permission, subscribe this browser, and tell the server about it.
export async function enablePush() {
  if (!pushSupported()) throw new Error("This browser doesn't support push notifications.");

  const permission = await Notification.requestPermission();
  if (permission !== "granted") {
    throw new Error("Notifications are blocked. Allow them in your browser's site settings, then try again.");
  }

  const { data } = await api.get("/notifications/vapid-public-key");
  if (!data.public_key) throw new Error("Push isn't set up on the server yet.");

  await navigator.serviceWorker.register("/sw.js");
  const registration = await navigator.serviceWorker.ready;

  let subscription = await registration.pushManager.getSubscription();
  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true, // browsers require every push to show a visible notification
      applicationServerKey: keyToBytes(data.public_key),
    });
  }

  const { endpoint, keys } = subscription.toJSON();
  await api.post("/notifications/push-subscription", { endpoint, keys });
  return subscription;
}

// Stop pushes to this device: remove it on the server, then unsubscribe in the browser.
export async function disablePush() {
  const subscription = await currentSubscription();
  if (!subscription) return;
  try {
    await api.delete("/notifications/push-subscription", { params: { endpoint: subscription.endpoint } });
  } catch {
    /* even if the server call fails, still unsubscribe locally */
  }
  await subscription.unsubscribe();
}
