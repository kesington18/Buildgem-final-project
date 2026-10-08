import { BRAND } from "../lib/brand";

export function Logo({ light = false, className = "" }) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <svg viewBox="0 0 32 32" className="size-8" aria-hidden>
        <rect width="32" height="32" rx="9" fill={light ? "#f3efe6" : "#2f4a3c"} />
        <path d="M9 9h14v10l-5 5H9z" fill={light ? "#2f4a3c" : "#f3efe6"} />
        <path d="M18 24v-5h5z" fill="#c99a3b" />
        <circle cx="16" cy="9" r="2.6" fill="#b4532c" stroke={light ? "#f3efe6" : "#2f4a3c"} strokeWidth="1.4" />
      </svg>
      <span className={`font-display text-[22px] italic tracking-tight ${light ? "text-paper" : "text-ink"}`}>
        {BRAND.name}
      </span>
    </span>
  );
}
