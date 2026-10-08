import { useState } from "react";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Inbox, Search, X } from "lucide-react";
import { api } from "../lib/api";
import { timeAgo } from "../lib/format";
import { useDebounce } from "../hooks/useDebounce";
import { Pagination } from "../components/Pagination";
import { fadeUp, stagger } from "../components/Reveal";
import { Button, Card, EmptyState, Field, Input, KeywordChip, PageHeader, Select, Skeleton } from "../components/ui";

const PAGE_SIZE = 10;
const EMPTY_FILTERS = { q: "", group: "", category: "", keyword: "", from: "", to: "" };

function AnnouncementCard({ item, groupName }) {
  const [open, setOpen] = useState(false);
  const long = item.message_content.length > 280;
  return (
    <motion.article variants={fadeUp}>
      <Card className="p-5 transition-shadow hover:shadow-lg hover:shadow-ink/5 sm:p-6">
        <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-ink-3">
          <span className="font-semibold text-ink-2">{groupName || "Class group"}</span>
          <span>·</span>
          <span>{timeAgo(item.message_timestamp)}</span>
          {item.sender_info && (<><span>·</span><span>from {item.sender_info}</span></>)}
        </div>
        <p className={`whitespace-pre-wrap text-[16px] leading-relaxed text-ink ${long && !open ? "line-clamp-5" : ""}`}>
          {item.message_content}
        </p>
        {long && (
          <button onClick={() => setOpen((o) => !o)} className="mt-2 cursor-pointer text-sm font-semibold text-moss hover:underline">
            {open ? "Show less" : "Read more"}
          </button>
        )}
        {item.keywords?.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {item.keywords.map((k) => <KeywordChip key={k.id} keyword={k} />)}
          </div>
        )}
      </Card>
    </motion.article>
  );
}

export default function Feed() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const debouncedQ = useDebounce(filters.q);

  // Changing any filter sends you back to page 1.
  const update = (patch) => {
    setFilters((f) => ({ ...f, ...patch }));
    setPage(1);
  };
  const hasFilters = Object.values(filters).some(Boolean);

  const { data: groups = [] } = useQuery({ queryKey: ["groups"], queryFn: async () => (await api.get("/groups")).data });
  const { data: options = { categories: [], keywords: [] } } = useQuery({
    queryKey: ["announcement-filters"],
    queryFn: async () => (await api.get("/announcements/filters")).data,
  });
  const groupNames = Object.fromEntries(groups.map((g) => [g.id, g.name]));

  const params = {
    page,
    page_size: PAGE_SIZE,
    q: debouncedQ || undefined,
    group_id: filters.group || undefined,
    category: filters.category || undefined,
    keyword: filters.keyword || undefined,
    date_from: filters.from ? new Date(`${filters.from}T00:00:00`).toISOString() : undefined,
    date_to: filters.to ? new Date(`${filters.to}T23:59:59`).toISOString() : undefined,
  };

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["announcements", params],
    queryFn: async () => {
      const res = await api.get("/announcements", { params });
      return { items: res.data, total: Number(res.headers["x-total-count"] ?? res.data.length) };
    },
    placeholderData: keepPreviousData, // keep showing the old page while the new one loads
  });

  return (
    <>
      <PageHeader eyebrow="Your feed" title="What's been pinned." text="Every announcement from the groups you're in, newest first." />

      <Card className="mb-8 p-4 sm:p-5">
        <div className="relative">
          <Search className="pointer-events-none absolute left-4 top-1/2 size-[18px] -translate-y-1/2 text-ink-3" />
          <Input
            value={filters.q}
            onChange={(e) => update({ q: e.target.value })}
            placeholder="Search announcements…"
            className="pl-11"
            aria-label="Search announcements"
          />
        </div>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Field label="Group">
            <Select value={filters.group} onChange={(e) => update({ group: e.target.value })}>
              <option value="">All groups</option>
              {groups.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
            </Select>
          </Field>
          <Field label="Category">
            <Select value={filters.category} onChange={(e) => update({ category: e.target.value })}>
              <option value="">All categories</option>
              {options.categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </Select>
          </Field>
          <Field label="Keyword">
            <Select value={filters.keyword} onChange={(e) => update({ keyword: e.target.value })}>
              <option value="">Any keyword</option>
              {options.keywords.map((k) => <option key={k} value={k}>{k}</option>)}
            </Select>
          </Field>
          <Field label="From">
            <Input type="date" value={filters.from} onChange={(e) => update({ from: e.target.value })} />
          </Field>
          <Field label="To">
            <Input type="date" value={filters.to} onChange={(e) => update({ to: e.target.value })} />
          </Field>
          {hasFilters && (
            <div className="flex items-end">
              <Button variant="ghost" onClick={() => { setFilters(EMPTY_FILTERS); setPage(1); }}>
                <X className="size-4" /> Clear filters
              </Button>
            </div>
          )}
        </div>
      </Card>

      {isLoading ? (
        <div className="space-y-4">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-36" />)}</div>
      ) : isError ? (
        <EmptyState icon={Inbox} title="Couldn't load the feed" text="Check your connection and try again." action={<Button onClick={() => refetch()}>Retry</Button>} />
      ) : data.items.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title={hasFilters ? "Nothing matches those filters" : "No announcements yet"}
          text={hasFilters ? "Try loosening a filter or clearing them all." : "When a message with a tracked keyword appears in an approved group, it'll show up here."}
        />
      ) : (
        <>
          <motion.div key={`${page}-${JSON.stringify(params)}`} variants={stagger} initial="hidden" animate="show" className="space-y-4">
            {data.items.map((item) => (
              <AnnouncementCard key={item.id} item={item} groupName={groupNames[item.source_group_id]} />
            ))}
          </motion.div>
          <Pagination page={page} pageSize={PAGE_SIZE} total={data.total} onChange={(p) => { setPage(p); window.scrollTo({ top: 0, behavior: "smooth" }); }} />
        </>
      )}
    </>
  );
}
