import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { Logo } from "./Logo";

const FLOATERS = [
  { word: "exam", x: "8%", y: "14%", d: 0 },
  { word: "deadline", x: "52%", y: "22%", d: 1.2 },
  { word: "venue", x: "18%", y: "58%", d: 0.6 },
  { word: "registration", x: "46%", y: "68%", d: 1.8 },
  { word: "timetable", x: "10%", y: "84%", d: 0.9 },
];

// Two-column shell shared by Login and Register: a dark story panel + the form.
export function AuthLayout({ title, subtitle, children, footer }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1.05fr_1fr]">
      <aside className="relative hidden overflow-hidden bg-ink p-12 text-paper lg:flex lg:flex-col lg:justify-between">
        <Link to="/"><Logo light /></Link>

        {FLOATERS.map((f) => (
          <motion.span
            key={f.word}
            className="absolute rounded-full border border-paper/20 px-4 py-1.5 text-sm text-paper/70"
            style={{ left: f.x, top: f.y }}
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 5 + f.d, repeat: Infinity, ease: "easeInOut", delay: f.d }}
          >
            #{f.word}
          </motion.span>
        ))}

        <div className="relative">
          <p className="font-display text-[40px] italic leading-[1.1] text-paper">
            “The announcement you needed was message #312.”
          </p>
          <p className="mt-4 max-w-sm text-[15px] text-paper/60">
            Noticeboard pins the messages that matter, so you never have to scroll for them again.
          </p>
        </div>
      </aside>

      <main className="flex items-center justify-center px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-[420px]"
        >
          <Link to="/" className="mb-10 inline-block lg:hidden"><Logo /></Link>
          <h1 className="font-display text-4xl tracking-tight">{title}</h1>
          <p className="mt-2 text-[15px] text-ink-3">{subtitle}</p>
          <div className="mt-8">{children}</div>
          <p className="mt-8 text-center text-[15px] text-ink-3">{footer}</p>
        </motion.div>
      </main>
    </div>
  );
}
