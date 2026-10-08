import { useEffect, useState } from "react";
import { animate } from "motion/react";

// Counts up from 0 to `value` whenever value changes.
export function AnimatedNumber({ value = 0 }) {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    const controls = animate(0, value, {
      duration: 1.1,
      ease: "easeOut",
      onUpdate: (v) => setShown(Math.round(v)),
    });
    return () => controls.stop();
  }, [value]);
  return <>{shown}</>;
}
