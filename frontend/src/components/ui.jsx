import { useEffect } from "react";
import { AnimatePresence, motion } from "motion/react";
import { X } from "lucide-react";
import { Logo } from "./Logo";

export const cx = (...parts) => parts.filter(Boolean).join(" ");

/* ---------- Buttons ---------- */
const VARIANTS = {
  primary: "bg-moss text-paper hover:bg-moss-2",
  clay: "bg-clay text-paper hover:bg-clay-2",
  outline: "border border-line bg-card text-ink hover:border-ink-3",
  ghost: "text-ink-2 hover:bg-paper-2",
  danger: "border border-line bg-card text-clay hover:border-clay",
};
const SIZES = {
  sm: "h-9 px-4 text-sm",
  md: "h-11 px-6 text-[15px]",
  lg: "h-13 px-8 text-base",
};

// Class string only, so <Link> and <a> can look like buttons too.
export const buttonClass = (variant = "primary", size = "md", extra = "") =>
  cx(
    "inline-flex cursor-pointer select-none items-center justify-center gap-2 rounded-full font-medium transition-colors",
    "disabled:pointer-events-none disabled:opacity-50",
    VARIANTS[variant],
    SIZES[size],
    extra
  );

export function Button({ variant = "primary", size = "md", loading = false, className, children, disabled, ...props }) {
  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      disabled={disabled || loading}
      className={buttonClass(variant, size, className)}
      {...props}
    >
      {loading && <Spinner />}
      {children}
    </motion.button>
  );
}

export function Spinner({ className }) {
  return (
    <span
      aria-hidden
      className={cx("inline-block size-4 animate-spin rounded-full border-2 border-current border-t-transparent", className)}
    />
  );
}

/* ---------- Form controls ---------- */
export const inputClass =
  "w-full h-11 rounded-xl border border-line bg-card px-4 text-[15px] text-ink placeholder:text-ink-3 outline-none transition focus:border-moss focus:ring-4 focus:ring-moss/10";

export function Field({ label, hint, error, children }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-sm font-medium text-ink-2">{label}</span>}
      {children}
      {error ? (
        <span className="mt-1.5 block text-sm text-clay">{error}</span>
      ) : (
        hint && <span className="mt-1.5 block text-sm text-ink-3">{hint}</span>
      )}
    </label>
  );
}

export function Input({ className, ...props }) {
  return <input className={cx(inputClass, className)} {...props} />;
}

export function Select({ className, children, ...props }) {
  return (
    <select className={cx(inputClass, "cursor-pointer pr-8", className)} {...props}>
      {children}
    </select>
  );
}

/* ---------- Surfaces ---------- */
export function Card({ className, children, ...props }) {
  return (
    <div className={cx("rounded-2xl border border-line bg-card", className)} {...props}>
      {children}
    </div>
  );
}

const TONES = {
  moss: "bg-sage text-moss",
  clay: "bg-clay/10 text-clay",
  ochre: "bg-ochre/20 text-[#7a5a14]",
  neutral: "bg-paper-2 text-ink-2",
};
export function Badge({ tone = "neutral", className, children }) {
  return (
    <span className={cx("inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold", TONES[tone], className)}>
      {children}
    </span>
  );
}

// Category -> colour, so "academic" always looks the same everywhere.
export function KeywordChip({ keyword }) {
  const tone = keyword.category === "academic" ? "moss" : keyword.category === "general" ? "neutral" : "ochre";
  return (
    <Badge tone={tone}>
      <span className="opacity-60">#</span>
      {keyword.term}
    </Badge>
  );
}

export function Skeleton({ className }) {
  return <div className={cx("animate-pulse rounded-lg bg-paper-2", className)} />;
}

export function EmptyState({ icon: Icon, title, text, action }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center rounded-2xl border border-dashed border-line px-6 py-14 text-center"
    >
      {Icon && (
        <div className="mb-4 grid size-12 place-items-center rounded-full bg-paper-2 text-ink-2">
          <Icon className="size-5" />
        </div>
      )}
      <h3 className="font-display text-xl text-ink">{title}</h3>
      {text && <p className="mt-1.5 max-w-sm text-[15px] text-ink-3">{text}</p>}
      {action && <div className="mt-5">{action}</div>}
    </motion.div>
  );
}

export function PageHeader({ eyebrow, title, text, action }) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        {eyebrow && <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-clay">{eyebrow}</p>}
        <h1 className="font-display text-4xl tracking-tight text-ink sm:text-[44px] sm:leading-[1.05]">{title}</h1>
        {text && <p className="mt-2 max-w-xl text-[15px] text-ink-3">{text}</p>}
      </div>
      {action}
    </div>
  );
}

/* ---------- Modal ---------- */
export function Modal({ open, onClose, title, children }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 grid place-items-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="absolute inset-0 bg-ink/40 backdrop-blur-[2px]" onClick={onClose} />
          <motion.div
            role="dialog"
            aria-modal="true"
            initial={{ opacity: 0, y: 24, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ type: "spring", stiffness: 380, damping: 32 }}
            className="relative w-full max-w-md rounded-3xl border border-line bg-card p-6 shadow-2xl shadow-ink/10"
          >
            <div className="mb-4 flex items-start justify-between gap-4">
              <h2 className="font-display text-2xl text-ink">{title}</h2>
              <button onClick={onClose} aria-label="Close" className="rounded-full p-1.5 text-ink-3 hover:bg-paper-2">
                <X className="size-5" />
              </button>
            </div>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function ConfirmModal({ open, onClose, onConfirm, title, text, confirmLabel = "Delete", loading }) {
  return (
    <Modal open={open} onClose={onClose} title={title}>
      <p className="text-[15px] text-ink-2">{text}</p>
      <div className="mt-6 flex justify-end gap-3">
        <Button variant="ghost" onClick={onClose}>Cancel</Button>
        <Button variant="clay" loading={loading} onClick={onConfirm}>{confirmLabel}</Button>
      </div>
    </Modal>
  );
}

/* ---------- Full-screen loader shown while restoring a session ---------- */
export function BootScreen() {
  return (
    <div className="grid min-h-screen place-items-center">
      <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ duration: 1.6, repeat: Infinity }}>
        <Logo />
      </motion.div>
    </div>
  );
}
