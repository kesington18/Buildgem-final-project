import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AnimatePresence, motion } from "motion/react";
import { ArrowRight, Bell, Link2, Newspaper, Search, ShieldCheck, Tag, Users } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { Logo } from "../components/Logo";
import { Reveal, fadeUp, stagger } from "../components/Reveal";
import { buttonClass } from "../components/ui";

/* ------------------------------------------------------------------ */
/* Hero demo: a class chat on the left, the pinned feed on the right.   */
/* ------------------------------------------------------------------ */
const MESSAGES = [
  { from: "Tolu", text: "Reminder: the CSC 201 exam holds on Monday at 9am, Hall B.", keyword: "exam", category: "academic" },
  { from: "Amaka", text: "Who's bringing snacks to the study group tonight? 😅", keyword: null },
  { from: "Class rep", text: "Course registration closes Friday at midnight. Don't wait!", keyword: "registration", category: "academic" },
  { from: "Seyi", text: "Lecture venue changed to LT2 for tomorrow's class.", keyword: "venue", category: "general" },
];

function Highlight({ text, word, on }) {
  if (!word) return text;
  const i = text.toLowerCase().indexOf(word);
  if (i < 0) return text;
  return (
    <>
      {text.slice(0, i)}
      <span className={on ? "rounded bg-ochre/50 px-0.5 transition-colors" : ""}>{text.slice(i, i + word.length)}</span>
      {text.slice(i + word.length)}
    </>
  );
}

function HeroDemo() {
  const [step, setStep] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => setStep((s) => s + 1), 3200);
    return () => clearInterval(timer);
  }, []);

  const active = step % MESSAGES.length;

  // The three most recent messages that matched a keyword become cards on the right.
  const captured = [];
  for (let s = step; s >= 0 && captured.length < 3; s--) {
    const m = MESSAGES[s % MESSAGES.length];
    if (m.keyword) captured.push({ ...m, id: s });
  }

  return (
    <div className="relative mx-auto grid w-full max-w-[560px] gap-4 sm:grid-cols-2">
      <div className="absolute -inset-4 -z-10 rotate-2 rounded-[2rem] bg-paper-2" />

      {/* Chat */}
      <div className="rounded-3xl border border-line bg-card p-4 shadow-xl shadow-ink/5">
        <div className="mb-3 flex items-center gap-2 border-b border-line pb-3">
          <span className="grid size-7 place-items-center rounded-full bg-moss text-xs font-semibold text-paper">C</span>
          <div>
            <p className="text-sm font-semibold leading-none">CSC 200L · Class group</p>
            <p className="mt-1 text-[11px] text-ink-3">Telegram</p>
          </div>
        </div>
        <div className="space-y-2">
          {MESSAGES.map((m, i) => (
            <motion.div
              key={m.text}
              animate={{ opacity: i === active ? 1 : 0.45, scale: i === active ? 1 : 0.98 }}
              transition={{ duration: 0.35 }}
              className={`rounded-2xl rounded-tl-md px-3 py-2 text-[13px] leading-snug ${i === active ? "bg-sage" : "bg-paper"}`}
            >
              <p className="mb-0.5 text-[11px] font-semibold text-moss">{m.from}</p>
              <Highlight text={m.text} word={m.keyword} on={i === active} />
            </motion.div>
          ))}
        </div>
        <AnimatePresence mode="wait">
          <motion.p
            key={active}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 text-[11px] font-medium text-ink-3"
          >
            {MESSAGES[active].keyword ? `Keyword found: #${MESSAGES[active].keyword}` : "No keyword, so it's ignored"}
          </motion.p>
        </AnimatePresence>
      </div>

      {/* Feed */}
      <div className="rounded-3xl border border-line bg-card p-4 shadow-xl shadow-ink/5">
        <div className="mb-3 flex items-center justify-between border-b border-line pb-3">
          <p className="text-sm font-semibold">Your feed</p>
          <span className="rounded-full bg-clay/10 px-2 py-0.5 text-[11px] font-semibold text-clay">Live</span>
        </div>
        <div className="space-y-2">
          <AnimatePresence initial={false} mode="popLayout">
            {captured.map((c) => (
              <motion.div
                key={c.id}
                layout
                initial={{ opacity: 0, y: -28, scale: 0.94 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.94 }}
                transition={{ type: "spring", stiffness: 380, damping: 30 }}
                className="rounded-2xl border border-line bg-paper px-3 py-2.5"
              >
                <span className={`mb-1 inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold ${c.category === "academic" ? "bg-sage text-moss" : "bg-ochre/20 text-[#7a5a14]"}`}>
                  #{c.keyword}
                </span>
                <p className="text-[12.5px] leading-snug text-ink-2">{c.text}</p>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Page sections                                                        */
/* ------------------------------------------------------------------ */
const WORDS = ["exam", "deadline", "venue", "registration", "timetable", "assignment", "results", "orientation", "fees", "workshop"];

const STEPS = [
  { n: "01", title: "Add the bot", text: "Add the Noticeboard bot to your class Telegram group. That's the only thing your classmates have to see." },
  { n: "02", title: "Claim your group", text: "Send a one-time code in the group. The bot checks you really are a group admin, then hands you the keys." },
  { n: "03", title: "Pick your keywords", text: "Choose the words that matter. Only messages containing them are pinned. Everything else stays in the chat." },
];

const FEATURES = [
  { icon: Tag, title: "Keyword-smart capture", text: "The bot reads quietly and pins only what matches your list. No digest of noise." },
  { icon: Users, title: "Your group, your rules", text: "Every class governor controls their own keywords. Nobody else can change them." },
  { icon: Search, title: "Search that finds it", text: "Filter by group, category, keyword or date. Or just type a word and go." },
  { icon: Bell, title: "Notified, not nagged", text: "Follow the groups you care about and get a notification only for those." },
  { icon: ShieldCheck, title: "Verified ownership", text: "Only a real Telegram group admin can claim a group, checked with Telegram itself." },
  { icon: Newspaper, title: "One clean feed", text: "All your classes in one calm place, newest first, with the original wording intact." },
];

function Nav() {
  const { user } = useAuth();
  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-paper/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-3.5 sm:px-8">
        <Link to="/"><Logo /></Link>
        <nav className="hidden items-center gap-8 text-[15px] font-medium text-ink-2 md:flex">
          <a href="#how" className="hover:text-ink">How it works</a>
          <a href="#features" className="hover:text-ink">Features</a>
          <a href="#who" className="hover:text-ink">Who it's for</a>
        </nav>
        <div className="flex items-center gap-2">
          {user ? (
            <Link to="/app" className={buttonClass("primary", "sm")}>Open app <ArrowRight className="size-4" /></Link>
          ) : (
            <>
              <Link to="/login" className={buttonClass("ghost", "sm", "hidden sm:inline-flex")}>Sign in</Link>
              <Link to="/register" className={buttonClass("primary", "sm")}>Get started</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="mx-auto grid max-w-6xl items-center gap-14 px-5 pb-20 pt-14 sm:px-8 lg:grid-cols-[1.05fr_1fr] lg:pt-24">
      <motion.div variants={stagger} initial="hidden" animate="show">
        <motion.p variants={fadeUp} className="mb-6 inline-flex items-center gap-2 rounded-full border border-line bg-card px-3.5 py-1.5 text-[13px] font-medium text-ink-2">
          <span className="size-1.5 rounded-full bg-clay" /> Built for campus group chats
        </motion.p>
        <motion.h1 variants={fadeUp} className="font-display text-[44px] leading-[1.02] tracking-tight sm:text-[68px]">
          Every announcement, <em className="text-clay">exactly</em> where you'll find it.
        </motion.h1>
        <motion.p variants={fadeUp} className="mt-6 max-w-lg text-lg leading-relaxed text-ink-2">
          Add our Telegram bot to your class group. It listens for the words your class cares about (exam, deadline, venue) and pins every matching message to one tidy feed.
        </motion.p>
        <motion.div variants={fadeUp} className="mt-9 flex flex-wrap items-center gap-3">
          <Link to="/register" className={buttonClass("primary", "lg")}>Start free <ArrowRight className="size-5" /></Link>
          <Link to="/login" className={buttonClass("outline", "lg")}>I have an account</Link>
        </motion.div>
        <motion.p variants={fadeUp} className="mt-5 text-sm text-ink-3">Free for students. Works with any Telegram group.</motion.p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}>
        <HeroDemo />
      </motion.div>
    </section>
  );
}

function Marquee() {
  const row = [...WORDS, ...WORDS];
  return (
    <div className="overflow-hidden border-y border-line bg-card py-5" aria-hidden>
      <div className="flex w-max animate-marquee gap-4">
        {row.map((w, i) => (
          <span key={i} className="whitespace-nowrap rounded-full border border-line px-5 py-2 font-display text-xl italic text-ink-2">
            #{w}
          </span>
        ))}
      </div>
    </div>
  );
}

function HowItWorks() {
  return (
    <section id="how" className="mx-auto max-w-6xl px-5 py-24 sm:px-8">
      <Reveal>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-clay">How it works</p>
        <h2 className="mt-3 max-w-xl font-display text-4xl tracking-tight sm:text-5xl">Three steps, then it runs itself.</h2>
      </Reveal>
      <div className="mt-14 grid gap-5 md:grid-cols-3">
        {STEPS.map((s, i) => (
          <Reveal key={s.n} delay={i * 0.1}>
            <motion.div whileHover={{ y: -6 }} transition={{ type: "spring", stiffness: 300, damping: 20 }} className="h-full rounded-3xl border border-line bg-card p-7">
              <p className="font-display text-6xl italic text-ochre">{s.n}</p>
              <h3 className="mt-6 font-display text-2xl">{s.title}</h3>
              <p className="mt-2 text-[15px] leading-relaxed text-ink-3">{s.text}</p>
            </motion.div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

function Features() {
  return (
    <section id="features" className="bg-paper-2/70 py-24">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <Reveal>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-clay">Features</p>
          <h2 className="mt-3 max-w-2xl font-display text-4xl tracking-tight sm:text-5xl">Small on noise. Big on the thing you actually needed.</h2>
        </Reveal>
        <div className="mt-14 grid gap-x-10 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f, i) => (
            <Reveal key={f.title} delay={(i % 3) * 0.08}>
              <div className="mb-4 grid size-11 place-items-center rounded-2xl bg-moss text-paper">
                <f.icon className="size-5" />
              </div>
              <h3 className="font-display text-xl">{f.title}</h3>
              <p className="mt-1.5 text-[15px] leading-relaxed text-ink-3">{f.text}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

function Audience() {
  return (
    <section id="who" className="mx-auto max-w-6xl px-5 py-24 sm:px-8">
      <div className="grid gap-5 lg:grid-cols-2">
        <Reveal>
          <div className="h-full rounded-3xl bg-sage p-9 sm:p-12">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-moss">For students</p>
            <h3 className="mt-3 font-display text-4xl tracking-tight">Stop scrolling. Start knowing.</h3>
            <ul className="mt-6 space-y-3 text-[16px] text-ink-2">
              <li>· One feed for every class you follow</li>
              <li>· Search any word, filter by date or group</li>
              <li>· Notifications only for the groups you choose</li>
            </ul>
            <Link to="/register" className={buttonClass("primary", "md", "mt-9")}>Join as a student</Link>
          </div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="h-full rounded-3xl bg-ink p-9 text-paper sm:p-12">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ochre">For class governors</p>
            <h3 className="mt-3 font-display text-4xl tracking-tight">Your group. Your keywords. Your call.</h3>
            <ul className="mt-6 space-y-3 text-[16px] text-paper/75">
              <li>· Claim your group in under a minute</li>
              <li>· Add, edit and remove keywords any time</li>
              <li>· Archive or delete announcements, and see what's trending</li>
            </ul>
            <Link to="/register" className={buttonClass("clay", "md", "mt-9")}><Link2 className="size-4" /> Claim your group</Link>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

function Closing() {
  return (
    <section className="mx-auto max-w-6xl px-5 pb-24 sm:px-8">
      <Reveal>
        <div className="relative overflow-hidden rounded-[2rem] border border-line bg-card px-8 py-16 text-center sm:py-20">
          <motion.div
            className="absolute -right-10 -top-10 size-44 rounded-full bg-ochre/25"
            animate={{ scale: [1, 1.12, 1] }}
            transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
          />
          <h2 className="relative mx-auto max-w-2xl font-display text-4xl tracking-tight sm:text-5xl">
            Your next deadline shouldn't be a surprise.
          </h2>
          <p className="relative mx-auto mt-4 max-w-md text-ink-3">Set it up once. It keeps working while you study.</p>
          <div className="relative mt-9 flex justify-center gap-3">
            <Link to="/register" className={buttonClass("primary", "lg")}>Create your account <ArrowRight className="size-5" /></Link>
          </div>
        </div>
      </Reveal>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-5 py-8 text-sm text-ink-3 sm:px-8">
        <Logo />
        <p>© {new Date().getFullYear()} Noticeboard. Made for campus life.</p>
      </div>
    </footer>
  );
}

export default function Landing() {
  return (
    <div className="overflow-x-clip">
      <Nav />
      <Hero />
      <Marquee />
      <HowItWorks />
      <Features />
      <Audience />
      <Closing />
      <Footer />
    </div>
  );
}
