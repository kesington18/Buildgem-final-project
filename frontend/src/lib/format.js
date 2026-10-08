// The API sometimes returns timestamps without a timezone ("2026-10-07T13:42:40").
// Browsers would read those as LOCAL time, so we treat them as UTC, which is what the server stores.
export function parseDate(value) {
  if (!value) return null;
  const hasZone = /[zZ]|[+-]\d{2}:?\d{2}$/.test(value);
  return new Date(hasZone ? value : `${value}Z`);
}

export function timeAgo(value) {
  const date = parseDate(value);
  if (!date) return "";
  const seconds = Math.round((Date.now() - date.getTime()) / 1000);
  if (seconds < 45) return "just now";
  const units = [
    ["year", 31536000],
    ["month", 2592000],
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
  ];
  for (const [name, size] of units) {
    if (seconds >= size) {
      const n = Math.floor(seconds / size);
      return `${n} ${name}${n > 1 ? "s" : ""} ago`;
    }
  }
  return "just now";
}

export function formatDate(value, withTime = false) {
  const date = parseDate(value);
  if (!date) return "";
  return date.toLocaleString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    ...(withTime ? { hour: "2-digit", minute: "2-digit" } : {}),
  });
}

export const initials = (name = "") =>
  name.split(" ").filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join("") || "?";
