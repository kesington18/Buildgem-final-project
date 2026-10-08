/* Noticeboard service worker: its only job is to show push notifications and handle taps on them.
   It lives at the site root (/sw.js) so it can control every page. */

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

// The server sends JSON: { title, body, url, tag }.
self.addEventListener("push", (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch {
    data = { body: event.data ? event.data.text() : "" };
  }

  event.waitUntil(
    self.registration.showNotification(data.title || "Noticeboard", {
      body: data.body || "You have a new announcement.",
      icon: "/icon-192.png",
      badge: "/icon-192.png",
      tag: data.tag || undefined, // same tag = replaces instead of stacking duplicates
      data: { url: data.url || "/app/notifications" },
    })
  );
});

// Tapping the notification focuses an open tab (or opens one) on the right page.
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = new URL(event.notification.data?.url || "/app/notifications", self.location.origin).href;

  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(async (windows) => {
      for (const client of windows) {
        if (new URL(client.url).origin === self.location.origin) {
          await client.focus();
          if ("navigate" in client) await client.navigate(target);
          return;
        }
      }
      return self.clients.openWindow(target);
    })
  );
});
