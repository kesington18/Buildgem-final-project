import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Bell, BellOff } from "lucide-react";
import { errorMessage } from "../lib/api";
import { currentSubscription, disablePush, enablePush, isIOS, pushSupported } from "../lib/push";
import { useToast } from "./Toast";
import { Button, Card } from "./ui";

// Card that turns instant push alerts on/off for THIS device.
// `hideWhenOn` lets other pages show it only as a nudge.
export function PushCard({ hideWhenOn = false }) {
  const toast = useToast();
  const [status, setStatus] = useState("loading"); // loading | unsupported | blocked | off | on
  const [busy, setBusy] = useState(false);

  const check = async () => {
    if (!pushSupported()) return setStatus("unsupported");
    if (Notification.permission === "denied") return setStatus("blocked");
    setStatus((await currentSubscription()) ? "on" : "off");
  };

  useEffect(() => {
    check();
  }, []);

  const turnOn = async () => {
    setBusy(true);
    try {
      await enablePush();
      toast.success("Instant alerts are on for this device.");
    } catch (err) {
      toast.error(err.response ? errorMessage(err) : err.message);
    } finally {
      await check();
      setBusy(false);
    }
  };

  const turnOff = async () => {
    setBusy(true);
    try {
      await disablePush();
      toast.success("Instant alerts are off for this device.");
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      await check();
      setBusy(false);
    }
  };

  if (status === "loading" || (hideWhenOn && status === "on")) return null;

  const copy = {
    unsupported: isIOS()
      ? "On iPhone or iPad, tap Share → Add to Home Screen, then open Noticeboard from your Home Screen and turn this on."
      : "This browser doesn't support push notifications. Try Chrome, Edge, Firefox or Safari.",
    blocked: "Notifications are blocked for this site. Allow them in your browser's site settings, then come back.",
    off: "Get a notification the moment a group you follow gets a new announcement, even when this tab is closed.",
    on: "You'll be alerted instantly on this device when a group you follow gets a new announcement.",
  }[status];

  return (
    <AnimatePresence>
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mb-6">
        <Card className="flex flex-wrap items-center gap-4 p-5">
          <span className={`grid size-11 shrink-0 place-items-center rounded-full ${status === "on" ? "bg-moss text-paper" : "bg-paper-2 text-ink-2"}`}>
            {status === "on" ? <Bell className="size-5" /> : <BellOff className="size-5" />}
          </span>
          <div className="min-w-0 flex-1 basis-60">
            <p className="font-semibold">Instant alerts on this device</p>
            <p className="mt-0.5 text-[14.5px] text-ink-3">{copy}</p>
          </div>
          {status === "off" && <Button loading={busy} onClick={turnOn}>Turn on</Button>}
          {status === "on" && <Button variant="outline" loading={busy} onClick={turnOff}>Turn off</Button>}
        </Card>
      </motion.div>
    </AnimatePresence>
  );
}
