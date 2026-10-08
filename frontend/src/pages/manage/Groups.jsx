import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "motion/react";
import { ArrowRight, Pause, Play, Trash2, Users } from "lucide-react";
import { useAuth } from "../../auth/AuthContext";
import { api, errorMessage } from "../../lib/api";
import { formatDate } from "../../lib/format";
import { useToast } from "../../components/Toast";
import { fadeUp, stagger } from "../../components/Reveal";
import { Badge, Button, Card, ConfirmModal, EmptyState, PageHeader, Skeleton, buttonClass } from "../../components/ui";

function ownerLabel(group, userId) {
  if (group.owner_id === userId) return "You";
  return group.owner_id ? "Another student" : "Unclaimed";
}

export default function ManageGroups() {
  const { user, isAdmin } = useAuth();
  const qc = useQueryClient();
  const toast = useToast();
  const [toDelete, setToDelete] = useState(null);

  const { data: groups = [], isLoading } = useQuery({
    queryKey: ["admin-groups"],
    queryFn: async () => (await api.get("/admin/groups")).data,
  });

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["admin-groups"] });
    qc.invalidateQueries({ queryKey: ["groups"] });
  };

  const setActive = useMutation({
    mutationFn: ({ id, is_active }) => api.patch(`/admin/groups/${id}`, { is_active }),
    onSuccess: (_res, vars) => { refresh(); toast.success(vars.is_active ? "Group is live." : "Group paused."); },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const remove = useMutation({
    mutationFn: (id) => api.delete(`/admin/groups/${id}`),
    onSuccess: (res) => { refresh(); setToDelete(null); toast.success(res.data.detail); },
    onError: (e) => { setToDelete(null); toast.error(errorMessage(e)); },
  });

  const pending = groups.filter((g) => !g.is_active).length;

  return (
    <>
      <PageHeader
        eyebrow={isAdmin ? "Site admin" : "Group owner"}
        title="Groups & keywords."
        text={
          isAdmin
            ? "Every group the bot has joined. New groups appear here automatically; activate one to start capturing."
            : "The groups you own. Open one to manage what the bot listens for."
        }
        action={pending > 0 && <Badge tone="ochre">{pending} waiting for approval</Badge>}
      />

      {isLoading ? (
        <div className="space-y-4">{[0, 1].map((i) => <Skeleton key={i} className="h-40" />)}</div>
      ) : groups.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No groups yet"
          text="Add the bot to a Telegram group, then claim it from 'Own a group'."
          action={<Link to="/app/claim" className={buttonClass("primary", "md")}>Claim a group</Link>}
        />
      ) : (
        <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-4">
          {groups.map((g) => (
            <motion.div key={g.id} variants={fadeUp}>
              <Card className="p-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h3 className="truncate font-display text-2xl">{g.name}</h3>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <Badge tone={g.is_active ? "moss" : "ochre"}>{g.is_active ? "Active" : "Pending"}</Badge>
                      <Badge>Owner: {ownerLabel(g, user.id)}</Badge>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Link to={`/app/manage/groups/${g.id}`} className={buttonClass("primary", "sm")}>
                      Keywords <ArrowRight className="size-4" />
                    </Link>
                    <Button
                      variant="outline"
                      size="sm"
                      loading={setActive.isPending && setActive.variables?.id === g.id}
                      onClick={() => setActive.mutate({ id: g.id, is_active: !g.is_active })}
                    >
                      {g.is_active ? <><Pause className="size-4" /> Pause</> : <><Play className="size-4" /> Activate</>}
                    </Button>
                    <Button variant="danger" size="sm" aria-label="Delete group" onClick={() => setToDelete(g)}>
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </div>

                <dl className="mt-5 grid gap-x-8 gap-y-2 border-t border-line pt-4 text-sm sm:grid-cols-3">
                  <div>
                    <dt className="text-ink-3">Bot added by</dt>
                    <dd className="font-medium text-ink-2">{g.telegram_added_by_name || "Unknown"}</dd>
                  </div>
                  <div>
                    <dt className="text-ink-3">Approved</dt>
                    <dd className="font-medium text-ink-2">{g.approved_at ? formatDate(g.approved_at) : "Not yet"}</dd>
                  </div>
                  <div>
                    <dt className="text-ink-3">Seen since</dt>
                    <dd className="font-medium text-ink-2">{formatDate(g.created_at)}</dd>
                  </div>
                </dl>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}

      <ConfirmModal
        open={Boolean(toDelete)}
        onClose={() => setToDelete(null)}
        onConfirm={() => remove.mutate(toDelete.id)}
        loading={remove.isPending}
        title="Remove this group?"
        text={`"${toDelete?.name}" will stop being monitored. If it already has announcements, it's paused instead so history is kept.`}
        confirmLabel="Remove"
      />
    </>
  );
}
