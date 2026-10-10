import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "motion/react";
import { Bell, Check } from "lucide-react";
import { api, errorMessage } from "../lib/api";
import { timeAgo } from "../lib/format";
import { useToast } from "../components/Toast";
import { PushCard } from "../components/PushCard";
import { Button, Card, EmptyState, KeywordChip, PageHeader, Skeleton, cx } from "../components/ui";

export default function Notifications() {
  const [tab, setTab] = useState("all");
  const qc = useQueryClient();
  const toast = useToast();

  const { data = [], isLoading } = useQuery({
    queryKey: ["notifications", "list", tab],
    queryFn: async () => (await api.get("/notifications", { params: { unread_only: tab === "unread", limit: 100 } })).data,
  });

  const refresh = () => qc.invalidateQueries({ queryKey: ["notifications"] });

  const markRead = useMutation({
    mutationFn: (id) => api.patch(`/notifications/${id}/read`, { is_read: true }),
    onSuccess: refresh,
    onError: (e) => toast.error(errorMessage(e)),
  });
  const markAll = useMutation({
    mutationFn: () => api.post("/notifications/read-all"),
    onSuccess: () => { refresh(); toast.success("All caught up."); },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const unreadCount = data.filter((n) => !n.is_read).length;

  return (
    <>
      <PageHeader
        eyebrow="Notifications"
        title="Things you shouldn't miss."
        text="You get one for each new announcement in the groups you follow."
        action={
          <Button variant="outline" size="sm" loading={markAll.isPending} disabled={tab === "all" && unreadCount === 0} onClick={() => markAll.mutate()}>
            <Check className="size-4" /> Mark all read
          </Button>
        }
      />

      <PushCard />

      <div className="mb-6 inline-flex rounded-full border border-line bg-card p-1">
        {["all", "unread"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cx("relative cursor-pointer rounded-full px-5 py-2 text-sm font-medium capitalize", tab === t ? "text-paper" : "text-ink-2")}
          >
            {tab === t && <motion.span layoutId="notif-tab" className="absolute inset-0 rounded-full bg-moss" transition={{ type: "spring", stiffness: 420, damping: 34 }} />}
            <span className="relative">{t}</span>
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-28" />)}</div>
      ) : data.length === 0 ? (
        <EmptyState
          icon={Bell}
          title={tab === "unread" ? "You're all caught up" : "No notifications yet"}
          text="Follow some groups and new announcements will land here."
        />
      ) : (
        <div className="space-y-3">
          <AnimatePresence initial={false}>
            {data.map((n) => (
              <motion.div key={n.id} layout initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -30 }}>
                <Card className={cx("flex gap-4 p-5", !n.is_read && "border-moss/40 bg-sage/40")}>
                  <span className={cx("mt-2 size-2.5 shrink-0 rounded-full", n.is_read ? "bg-line" : "bg-clay")} />
                  <div className="min-w-0 flex-1">
                    <p className="whitespace-pre-wrap text-[15.5px] leading-relaxed text-ink">{n.announcement?.message_content ?? "Announcement no longer available."}</p>
                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      {n.announcement?.keywords?.map((k) => <KeywordChip key={k.id} keyword={k} />)}
                      <span className="text-sm text-ink-3">{timeAgo(n.created_at)}</span>
                    </div>
                  </div>
                  {!n.is_read && (
                    <Button variant="ghost" size="sm" className="self-start" onClick={() => markRead.mutate(n.id)}>
                      Mark read
                    </Button>
                  )}
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </>
  );
}
