import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "motion/react";
import { ArrowLeft, Check, Pencil, Plus, Tag, Trash2, X } from "lucide-react";
import { api, errorMessage } from "../../lib/api";
import { useToast } from "../../components/Toast";
import { Badge, Button, Card, ConfirmModal, EmptyState, Field, Input, Modal, PageHeader, Skeleton, cx } from "../../components/ui";

const SUGGESTED_CATEGORIES = ["academic", "general", "events", "finance", "hostel", "sports"];

// A small on/off switch.
function Switch({ on, onChange, label }) {
  return (
    <button
      role="switch"
      aria-checked={on}
      aria-label={label}
      onClick={() => onChange(!on)}
      className={cx("flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full p-0.5 transition-colors", on ? "bg-moss" : "bg-line")}
    >
      <motion.span layout transition={{ type: "spring", stiffness: 500, damping: 32 }} className={cx("size-5 rounded-full bg-card shadow", on && "ml-auto")} />
    </button>
  );
}

export default function GroupDetail() {
  const { id } = useParams();
  const qc = useQueryClient();
  const toast = useToast();

  const [term, setTerm] = useState("");
  const [category, setCategory] = useState("academic");
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);

  const groupsQ = useQuery({ queryKey: ["admin-groups"], queryFn: async () => (await api.get("/admin/groups")).data });
  const group = groupsQ.data?.find((g) => g.id === id);

  const kwQ = useQuery({ queryKey: ["keywords", id], queryFn: async () => (await api.get(`/groups/${id}/keywords`)).data });
  const keywords = kwQ.data ?? [];
  const pending = keywords.filter((k) => k.status === "pending");
  const approved = keywords.filter((k) => k.status === "approved");
  const categories = [...new Set([...SUGGESTED_CATEGORIES, ...keywords.map((k) => k.category)])];

  const refresh = () => qc.invalidateQueries({ queryKey: ["keywords", id] });
  const onError = (e) => toast.error(errorMessage(e));

  const add = useMutation({
    mutationFn: () => api.post(`/groups/${id}/keywords`, { term, category }),
    onSuccess: () => { refresh(); setTerm(""); toast.success("Keyword added. The bot is listening for it."); },
    onError,
  });
  const patch = useMutation({
    mutationFn: ({ kid, body }) => api.patch(`/groups/${id}/keywords/${kid}`, body),
    onSuccess: () => { refresh(); setEditing(null); },
    onError,
  });
  const remove = useMutation({
    mutationFn: (kid) => api.delete(`/groups/${id}/keywords/${kid}`),
    onSuccess: () => { refresh(); setDeleting(null); toast.success("Keyword removed."); },
    onError,
  });

  const submit = (e) => {
    e.preventDefault();
    if (term.trim()) add.mutate();
  };

  return (
    <>
      <Link to="/app/manage/groups" className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-ink-3 hover:text-ink">
        <ArrowLeft className="size-4" /> All groups
      </Link>

      <PageHeader
        eyebrow="Keywords"
        title={group?.name ?? "Group"}
        text="The bot pins any message in this group that contains one of these words. Matching ignores upper and lower case."
        action={group && <Badge tone={group.is_active ? "moss" : "ochre"}>{group.is_active ? "Active" : "Paused"}</Badge>}
      />

      {/* Add */}
      <Card className="mb-8 p-5">
        <form onSubmit={submit} className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <Field label="New keyword">
              <Input value={term} onChange={(e) => setTerm(e.target.value)} placeholder="e.g. timetable" maxLength={60} />
            </Field>
          </div>
          <div className="sm:w-52">
            <Field label="Category">
              <Input list="category-options" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="academic" />
              <datalist id="category-options">{categories.map((c) => <option key={c} value={c} />)}</datalist>
            </Field>
          </div>
          <Button type="submit" loading={add.isPending} disabled={!term.trim() || !category.trim()}>
            <Plus className="size-4" /> Add
          </Button>
        </form>
      </Card>

      {/* Suggestions from students */}
      <AnimatePresence>
        {pending.length > 0 && (
          <motion.section initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="mb-8 overflow-hidden">
            <h2 className="mb-3 font-display text-2xl">Suggestions waiting</h2>
            <div className="space-y-2">
              {pending.map((k) => (
                <Card key={k.id} className="flex items-center gap-3 border-ochre/50 bg-ochre/10 p-4">
                  <span className="font-semibold">#{k.term}</span>
                  <Badge>{k.category}</Badge>
                  <div className="ml-auto flex gap-2">
                    <Button size="sm" onClick={() => patch.mutate({ kid: k.id, body: { status: "approved" } })}><Check className="size-4" /> Approve</Button>
                    <Button size="sm" variant="danger" onClick={() => remove.mutate(k.id)}><X className="size-4" /> Reject</Button>
                  </div>
                </Card>
              ))}
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Active keywords */}
      <h2 className="mb-3 font-display text-2xl">Listening for</h2>
      {kwQ.isLoading ? (
        <div className="space-y-2">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-16" />)}</div>
      ) : approved.length === 0 ? (
        <EmptyState icon={Tag} title="No keywords yet" text="Add your first keyword above. Until you do, the bot won't pin anything from this group." />
      ) : (
        <div className="space-y-2">
          <AnimatePresence initial={false}>
            {approved.map((k) => (
              <motion.div key={k.id} layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -24 }}>
                <Card className={cx("flex items-center gap-3 p-4", !k.is_active && "opacity-60")}>
                  <span className="font-semibold">#{k.term}</span>
                  <Badge tone={k.category === "academic" ? "moss" : "neutral"}>{k.category}</Badge>
                  <div className="ml-auto flex items-center gap-1">
                    <Switch on={k.is_active} label={`Toggle ${k.term}`} onChange={(v) => patch.mutate({ kid: k.id, body: { is_active: v } })} />
                    <Button variant="ghost" size="sm" aria-label={`Edit ${k.term}`} onClick={() => setEditing({ ...k })}><Pencil className="size-4" /></Button>
                    <Button variant="ghost" size="sm" aria-label={`Delete ${k.term}`} onClick={() => setDeleting(k)}><Trash2 className="size-4 text-clay" /></Button>
                  </div>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      <Modal open={Boolean(editing)} onClose={() => setEditing(null)} title="Edit keyword">
        {editing && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              patch.mutate({ kid: editing.id, body: { term: editing.term, category: editing.category } });
            }}
            className="space-y-4"
          >
            <Field label="Keyword"><Input value={editing.term} onChange={(e) => setEditing({ ...editing, term: e.target.value })} /></Field>
            <Field label="Category"><Input value={editing.category} onChange={(e) => setEditing({ ...editing, category: e.target.value })} /></Field>
            <div className="flex justify-end gap-3 pt-2">
              <Button type="button" variant="ghost" onClick={() => setEditing(null)}>Cancel</Button>
              <Button type="submit" loading={patch.isPending}>Save</Button>
            </div>
          </form>
        )}
      </Modal>

      <ConfirmModal
        open={Boolean(deleting)}
        onClose={() => setDeleting(null)}
        onConfirm={() => remove.mutate(deleting.id)}
        loading={remove.isPending}
        title="Delete this keyword?"
        text={`The bot will stop pinning messages that contain "${deleting?.term}". Announcements already pinned stay.`}
      />
    </>
  );
}
