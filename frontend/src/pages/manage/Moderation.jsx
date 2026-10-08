import { useState } from "react";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "motion/react";
import { Archive, ArchiveRestore, Search, ShieldCheck, Trash2 } from "lucide-react";
import { api, errorMessage } from "../../lib/api";
import { timeAgo } from "../../lib/format";
import { useDebounce } from "../../hooks/useDebounce";
import { useToast } from "../../components/Toast";
import { Pagination } from "../../components/Pagination";
import { Badge, Button, Card, ConfirmModal, EmptyState, Input, KeywordChip, PageHeader, Select, Skeleton } from "../../components/ui";

const PAGE_SIZE = 10;

export default function Moderation() {
  const qc = useQueryClient();
  const toast = useToast();
  const [status, setStatus] = useState("");
  const [group, setGroup] = useState("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [toDelete, setToDelete] = useState(null);
  const debouncedQ = useDebounce(q);

  const { data: groups = [] } = useQuery({ queryKey: ["admin-groups"], queryFn: async () => (await api.get("/admin/groups")).data });
  const groupNames = Object.fromEntries(groups.map((g) => [g.id, g.name]));

  const params = { page, page_size: PAGE_SIZE, status: status || undefined, group_id: group || undefined, q: debouncedQ || undefined };
  const { data, isLoading } = useQuery({
    queryKey: ["admin-announcements", params],
    queryFn: async () => {
      const res = await api.get("/admin/announcements", { params });
      return { items: res.data, total: Number(res.headers["x-total-count"] ?? res.data.length) };
    },
    placeholderData: keepPreviousData,
  });

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["admin-announcements"] });
    qc.invalidateQueries({ queryKey: ["announcements"] });
    qc.invalidateQueries({ queryKey: ["analytics"] });
  };
  const onError = (e) => toast.error(errorMessage(e));

  const setStatusMut = useMutation({
    mutationFn: ({ id, status }) => api.patch(`/admin/announcements/${id}`, { status }),
    onSuccess: (_r, v) => { refresh(); toast.success(v.status === "archived" ? "Archived. Students no longer see it." : "Restored to the feed."); },
    onError,
  });
  const remove = useMutation({
    mutationFn: (id) => api.delete(`/admin/announcements/${id}`),
    onSuccess: () => { refresh(); setToDelete(null); toast.success("Deleted."); },
    onError: (e) => { setToDelete(null); onError(e); },
  });

  const reset = (setter) => (e) => { setter(e.target.value); setPage(1); };

  return (
    <>
      <PageHeader eyebrow="Moderation" title="Keep the feed clean." text="Archive what's outdated, restore it if you change your mind, or delete it for good." />

      <div className="mb-6 grid gap-3 sm:grid-cols-[1fr_180px_220px]">
        <div className="relative">
          <Search className="pointer-events-none absolute left-4 top-1/2 size-[18px] -translate-y-1/2 text-ink-3" />
          <Input className="pl-11" placeholder="Search text…" value={q} onChange={reset(setQ)} aria-label="Search announcements" />
        </div>
        <Select value={status} onChange={reset(setStatus)} aria-label="Status">
          <option value="">Active + archived</option>
          <option value="active">Active only</option>
          <option value="archived">Archived only</option>
        </Select>
        <Select value={group} onChange={reset(setGroup)} aria-label="Group">
          <option value="">All my groups</option>
          {groups.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
        </Select>
      </div>

      {isLoading ? (
        <div className="space-y-3">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-32" />)}</div>
      ) : data.items.length === 0 ? (
        <EmptyState icon={ShieldCheck} title="Nothing to moderate" text="Announcements will show up here as the bot pins them." />
      ) : (
        <>
          <div className="space-y-3">
            <AnimatePresence initial={false}>
              {data.items.map((a) => (
                <motion.div key={a.id} layout initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -30 }}>
                  <Card className="p-5">
                    <div className="mb-2 flex flex-wrap items-center gap-2 text-sm text-ink-3">
                      <span className="font-semibold text-ink-2">{groupNames[a.source_group_id] ?? "Unknown group"}</span>
                      <span>·</span>
                      <span>{timeAgo(a.message_timestamp)}</span>
                      {a.status === "archived" && <Badge tone="ochre">Archived</Badge>}
                    </div>
                    <p className="line-clamp-4 whitespace-pre-wrap text-[15.5px] leading-relaxed">{a.message_content}</p>
                    <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                      <div className="flex flex-wrap gap-2">{a.keywords?.map((k) => <KeywordChip key={k.id} keyword={k} />)}</div>
                      <div className="flex gap-2">
                        {a.status === "archived" ? (
                          <Button size="sm" variant="outline" onClick={() => setStatusMut.mutate({ id: a.id, status: "active" })}>
                            <ArchiveRestore className="size-4" /> Restore
                          </Button>
                        ) : (
                          <Button size="sm" variant="outline" onClick={() => setStatusMut.mutate({ id: a.id, status: "archived" })}>
                            <Archive className="size-4" /> Archive
                          </Button>
                        )}
                        <Button size="sm" variant="danger" aria-label="Delete announcement" onClick={() => setToDelete(a)}>
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
          <Pagination page={page} pageSize={PAGE_SIZE} total={data.total} onChange={setPage} />
        </>
      )}

      <ConfirmModal
        open={Boolean(toDelete)}
        onClose={() => setToDelete(null)}
        onConfirm={() => remove.mutate(toDelete.id)}
        loading={remove.isPending}
        title="Delete this announcement?"
        text="It's removed for everyone, including any notifications about it. This can't be undone. Consider archiving instead."
      />
    </>
  );
}
