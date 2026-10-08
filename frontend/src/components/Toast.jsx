import { createContext, useCallback, useContext, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Check, X } from "lucide-react";

const ToastContext = createContext(null);
export const useToast = () => useContext(ToastContext);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const push = useCallback((type, message) => {
    const id = crypto.randomUUID();
    setToasts((list) => [...list, { id, type, message }]);
    setTimeout(() => setToasts((list) => list.filter((t) => t.id !== id)), 4200);
  }, []);

  const api = {
    success: (message) => push("success", message),
    error: (message) => push("error", message),
  };

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-[60] flex w-[min(92vw,360px)] flex-col gap-2">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              layout
              initial={{ opacity: 0, x: 40, scale: 0.96 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 40 }}
              transition={{ type: "spring", stiffness: 420, damping: 32 }}
              className="pointer-events-auto flex items-start gap-3 rounded-2xl border border-line bg-card px-4 py-3 shadow-lg shadow-ink/10"
            >
              <span
                className={`mt-0.5 grid size-5 shrink-0 place-items-center rounded-full text-paper ${
                  t.type === "success" ? "bg-moss" : "bg-clay"
                }`}
              >
                {t.type === "success" ? <Check className="size-3.5" /> : <X className="size-3.5" />}
              </span>
              <p className="text-[15px] leading-snug text-ink">{t.message}</p>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}
