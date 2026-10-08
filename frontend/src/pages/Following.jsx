import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Check, Rss } from "lucide-react";
import { api, errorMessage } from "../lib/api";
import { useToast } from "../components/Toast";
import { fadeUp, stagger } from "../components/Reveal";
import { Button, Card, EmptyState, PageHeader, Skeleton, cx } from "../components/ui";

export default function Following() {
  const qc = useQueryClient();
  const toast = useToast();

  const groupsQ = useQuery({ queryKey: ["groups"], queryFn: async () => (await api.get("/groups")).data });
  const prefsQ = useQuery({ queryKey: ["preferences"], queryFn: async () => (await api.get("/notifications/preferences")).data });

  // `selected` is null until you click something; until then we just mirror what's saved.
  const saved = useMemo(() => new Set((prefsQ.data ?? []).map((p) => p.group_id)), [prefsQ.data]);
  const [selected, setSelected] = useState(null);
  const chosen = selected ?? saved;
  const dirty = selected !== null && (selected.size !== saved.size || [...selected].some((id) => !saved.has(id)));

  const toggle = (id) => {
    const next = new Set(chosen);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const save = useMutation({
    mutationFn: () => api.put("/notifications/preferences", { group_ids: [...chosen], channel: "in_app" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["preferences"] });
      setSelected(null);
      toast.success("Saved. You'll be notified for these groups.");
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const groups = groupsQ.data ?? [];

  return (
    <>
      <PageHeader
        eyebrow="Following"
        title="Choose whose news you get."
        text="You'll only be notified about announcements from the groups you follow."
        action={
          <Button loading={save.isPending} disabled={!dirty} onClick={() => save.mutate()}>
            Save changes
          </Button>
        }
      />

      {groupsQ.isLoading || prefsQ.isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">{[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-24" />)}</div>
      ) : groups.length === 0 ? (
        <EmptyState icon={Rss} title="No groups yet" text="Once a class governor links their Telegram group, it will appear here for you to follow." />
      ) : (
        <motion.div variants={stagger} initial="hidden" animate="show" className="grid gap-4 sm:grid-cols-2">
          {groups.map((g) => {
            const on = chosen.has(g.id);
            return (
              <motion.button key={g.id} variants={fadeUp} whileTap={{ scale: 0.98 }} onClick={() => toggle(g.id)} className="cursor-pointer text-left">
                <Card className={cx("flex items-center gap-4 p-5 transition-colors", on ? "border-moss bg-sage/50" : "hover:border-ink-3")}>
                  <span className={cx("grid size-11 shrink-0 place-items-center rounded-full font-display text-lg", on ? "bg-moss text-paper" : "bg-paper-2 text-ink-2")}>
                    {g.name.replace(/[^\p{L}\p{N}]/gu, "").charAt(0).toUpperCase() || "#"}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-semibold text-ink">{g.name}</span>
                    <span className="text-sm text-ink-3">{on ? "Following" : "Not following"}</span>
                  </span>
                  <span className={cx("grid size-6 place-items-center rounded-full border", on ? "border-moss bg-moss text-paper" : "border-line")}>
                    {on && <Check className="size-4" />}
                  </span>
                </Card>
              </motion.button>
            );
          })}
        </motion.div>
      )}
    </>
  );
}
