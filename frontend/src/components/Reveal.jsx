import { motion } from "motion/react";

// Fades + slides its children up the first time they scroll into view.
export function Reveal({ children, delay = 0, y = 26, className, as = "div" }) {
  const Tag = motion[as];
  return (
    <Tag
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </Tag>
  );
}

// Parent/child variants: children animate one after another.
export const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
};
export const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] } },
};
