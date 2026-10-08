import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "./ui";

export function Pagination({ page, pageSize, total, onChange }) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  if (pages <= 1) return null;
  return (
    <div className="mt-8 flex items-center justify-between">
      <p className="text-sm text-ink-3">
        Page {page} of {pages} · {total} total
      </p>
      <div className="flex gap-2">
        <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onChange(page - 1)}>
          <ChevronLeft className="size-4" /> Prev
        </Button>
        <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => onChange(page + 1)}>
          Next <ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}
