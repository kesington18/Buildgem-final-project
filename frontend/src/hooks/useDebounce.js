import { useEffect, useState } from "react";

// Returns `value`, but only after it has stopped changing for `delay` ms.
// Used so typing in the search box doesn't fire a request on every keystroke.
export function useDebounce(value, delay = 350) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}
