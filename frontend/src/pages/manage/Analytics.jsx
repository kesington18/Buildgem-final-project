import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Activity } from "lucide-react";
import { api } from "../../lib/api";
import { AnimatedNumber } from "../../components/AnimatedNumber";
import { fadeUp, stagger } from "../../components/Reveal";
import { Card, EmptyState, PageHeader, Skeleton } from "../../components/ui";

const STATS = [
  ["announcements", "Announcements pinned"],
  ["active_announcements", "Visible to students"],
  ["keywords", "Keywords listening"],
  ["groups", "Active groups"],
];

// The last `n` calendar days as YYYY-MM-DD (UTC, matching the server), oldest first.
function lastDays(n) {
  return Array.from({ length: n }, (_, i) => {
    const d = new Date();
    d.setUTCDate(d.getUTCDate() - (n - 1 - i));
    return d.toISOString().slice(0, 10);
  });
}

function BarList({ title, data }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...entries.map(([, v]) => v));
  return (
    <Card className="p-6">
      <h3 className="mb-5 font-display text-2xl">{title}</h3>
      {entries.length === 0 ? (
        <p className="text-sm text-ink-3">Nothing to show yet.</p>
      ) : (
        <div className="space-y-4">
          {entries.map(([label, value], i) => (
            <div key={label}>
              <div className="mb-1.5 flex justify-between text-sm">
                <span className="truncate font-medium text-ink-2">{label}</span>
                <span className="text-ink-3">{value}</span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-paper-2">
                <motion.div
                  className="h-full rounded-full bg-moss"
                  initial={{ width: 0 }}
                  animate={{ width: `${(value / max) * 100}%` }}
                  transition={{ duration: 0.8, delay: 0.1 + i * 0.06, ease: [0.22, 1, 0.36, 1] }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

function Timeline({ data }) {
  const days = lastDays(30);
  const values = days.map((d) => data[d] ?? 0);
  const max = Math.max(1, ...values);
  return (
    <Card className="p-6">
      <div className="mb-5 flex items-baseline justify-between">
        <h3 className="font-display text-2xl">Last 30 days</h3>
        <span className="text-sm text-ink-3">{values.reduce((a, b) => a + b, 0)} announcements</span>
      </div>
      <div className="flex h-44 items-end gap-1">
        {values.map((v, i) => (
          <div key={days[i]} className="group relative flex h-full flex-1 items-end" title={`${days[i]}: ${v}`}>
            <motion.div
              className={v > 0 ? "w-full rounded-t-md bg-clay" : "w-full rounded-t-md bg-paper-2"}
              initial={{ height: 0 }}
              animate={{ height: `${Math.max(v > 0 ? 8 : 3, (v / max) * 100)}%` }}
              transition={{ duration: 0.7, delay: i * 0.015, ease: [0.22, 1, 0.36, 1] }}
            />
          </div>
        ))}
      </div>
      <div className="mt-2 flex justify-between text-xs text-ink-3">
        <span>{days[0]}</span>
        <span>{days[days.length - 1]}</span>
      </div>
    </Card>
  );
}

export default function Analytics() {
  const { data, isLoading } = useQuery({ queryKey: ["analytics"], queryFn: async () => (await api.get("/admin/analytics")).data });

  return (
    <>
      <PageHeader eyebrow="Analytics" title="What's happening." text="A snapshot of what the bot has pinned for your groups." />

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-28" />)}</div>
      ) : !data ? (
        <EmptyState icon={Activity} title="No data yet" />
      ) : (
        <div className="space-y-6">
          <motion.div variants={stagger} initial="hidden" animate="show" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {STATS.map(([key, label]) => (
              <motion.div key={key} variants={fadeUp}>
                <Card className="p-6">
                  <p className="font-display text-5xl tracking-tight text-moss"><AnimatedNumber value={data.totals[key]} /></p>
                  <p className="mt-2 text-sm text-ink-3">{label}</p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
          <Timeline data={data.over_time} />
          <div className="grid gap-6 lg:grid-cols-2">
            <BarList title="By category" data={data.per_category} />
            <BarList title="By group" data={data.per_group} />
          </div>
        </div>
      )}
    </>
  );
}
