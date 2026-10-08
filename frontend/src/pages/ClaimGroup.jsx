import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "motion/react";
import { ArrowRight, Check, Copy } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { api, errorMessage } from "../lib/api";
import { useToast } from "../components/Toast";
import { Badge, Button, Card, PageHeader, buttonClass } from "../components/ui";

const BOT = import.meta.env.VITE_BOT_USERNAME;

export default function ClaimGroup() {
  const { refreshUser } = useAuth();
  const toast = useToast();
  const qc = useQueryClient();

  const [claim, setClaim] = useState(null); // { code, command, expires_at } while a code is live
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [copied, setCopied] = useState(false);
  const baseline = useRef(0); // how many groups you owned when the code was made

  // While a code is live, poll every 4s to notice the moment the bot links your group.
  const mine = useQuery({
    queryKey: ["groups", "mine"],
    queryFn: async () => (await api.get("/groups/mine")).data,
    refetchInterval: claim ? 4000 : false,
  });

  const generate = useMutation({
    mutationFn: async () => (await api.post("/groups/claim-code")).data,
    onSuccess: (data) => {
      baseline.current = mine.data?.length ?? 0;
      setClaim(data);
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  // Countdown
  useEffect(() => {
    if (!claim) return;
    const tick = () => setSecondsLeft(Math.max(0, Math.round((new Date(claim.expires_at) - Date.now()) / 1000)));
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [claim]);

  // Success: a new owned group appeared.
  useEffect(() => {
    if (claim && mine.data && mine.data.length > baseline.current) {
      setClaim(null);
      refreshUser(); // so the sidebar gains the "Manage" section
      qc.invalidateQueries({ queryKey: ["groups"] });
      toast.success("Group linked. You're now its owner.");
    }
  }, [mine.data, claim, refreshUser, qc, toast]);

  const copy = async () => {
    await navigator.clipboard.writeText(claim.command);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const expired = claim && secondsLeft === 0;
  const mm = String(Math.floor(secondsLeft / 60)).padStart(2, "0");
  const ss = String(secondsLeft % 60).padStart(2, "0");

  return (
    <>
      <PageHeader
        eyebrow="Group owners"
        title="Claim your class group."
        text="Prove you run the Telegram group and you'll control its keywords, announcements and insights."
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
        <ol className="space-y-4">
          {[
            ["Add the bot", BOT ? <>Add <b>@{BOT}</b> to your Telegram group.</> : "Add the Noticeboard bot to your Telegram group."],
            ["Generate a code", "It's single-use and lasts 15 minutes."],
            ["Send it in the group", "Post the command exactly as shown. The bot confirms you're a group admin, then links the group."],
          ].map(([title, text], i) => (
            <motion.li key={title} initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className="flex gap-4">
              <span className="grid size-9 shrink-0 place-items-center rounded-full bg-moss font-display text-paper">{i + 1}</span>
              <div>
                <p className="font-semibold">{title}</p>
                <p className="mt-0.5 text-[15px] text-ink-3">{text}</p>
              </div>
            </motion.li>
          ))}
          <li className="rounded-2xl bg-ochre/15 p-4 text-sm text-ink-2">
            If you post as "Remain anonymous" in Telegram, the bot can't tell who you are. Turn that off for your admin account first.
          </li>
        </ol>

        <Card className="p-7">
          <AnimatePresence mode="wait">
            {!claim ? (
              <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="py-6 text-center">
                <p className="font-display text-2xl">Ready when you are.</p>
                <p className="mx-auto mt-2 max-w-xs text-[15px] text-ink-3">Make sure the bot is already in your group, then generate a code.</p>
                <Button size="lg" className="mt-6" loading={generate.isPending} onClick={() => generate.mutate()}>
                  Generate code
                </Button>
              </motion.div>
            ) : (
              <motion.div key="code" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <p className="text-sm font-medium text-ink-3">Send this in your group</p>
                <div className="mt-3 rounded-2xl bg-ink px-5 py-6 text-center">
                  <p className="select-all break-all font-mono text-[22px] font-semibold tracking-wider text-paper sm:text-[26px]">{claim.command}</p>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <Button variant="outline" size="sm" onClick={copy}>
                    {copied ? <Check className="size-4" /> : <Copy className="size-4" />} {copied ? "Copied" : "Copy"}
                  </Button>
                  {expired ? (
                    <Badge tone="clay">Expired</Badge>
                  ) : (
                    <span className="font-mono text-sm text-ink-2">Expires in {mm}:{ss}</span>
                  )}
                </div>
                <p className="mt-5 flex items-center gap-2 text-sm text-ink-3">
                  <span className="size-2 animate-pulse rounded-full bg-clay" /> Waiting for the bot to confirm…
                </p>
                {expired && (
                  <Button className="mt-4" onClick={() => generate.mutate()} loading={generate.isPending}>Get a new code</Button>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </div>

      {mine.data?.length > 0 && (
        <div className="mt-12">
          <h2 className="mb-4 font-display text-2xl">Groups you own</h2>
          <div className="space-y-3">
            {mine.data.map((g) => (
              <Card key={g.id} className="flex items-center justify-between gap-4 p-5">
                <div className="min-w-0">
                  <p className="truncate font-semibold">{g.name}</p>
                  <Badge tone={g.is_active ? "moss" : "ochre"} className="mt-1.5">{g.is_active ? "Active" : "Paused"}</Badge>
                </div>
                <Link to={`/app/manage/groups/${g.id}`} className={buttonClass("outline", "sm")}>
                  Manage <ArrowRight className="size-4" />
                </Link>
              </Card>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
