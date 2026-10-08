import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { buttonClass } from "../components/ui";

export default function NotFound() {
  return (
    <div className="grid min-h-screen place-items-center px-6 text-center">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <p className="font-display text-[120px] italic leading-none text-clay">404</p>
        <h1 className="mt-2 font-display text-3xl">This page wandered off the board.</h1>
        <p className="mt-2 text-ink-3">The link may be old, or the page may have moved.</p>
        <Link to="/" className={buttonClass("primary", "md", "mt-8")}>Back to home</Link>
      </motion.div>
    </div>
  );
}
