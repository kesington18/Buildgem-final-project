import { useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "motion/react";
import { useQuery } from "@tanstack/react-query";
import { Activity, Bell, Link2, LogOut, Menu, Newspaper, Rss, ShieldCheck, Users, X } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { initials } from "../lib/format";
import { Logo } from "./Logo";
import { cx } from "./ui";

const MANAGE_NAV = [
  { to: "/app/manage/groups", label: "Groups & keywords", icon: Users },
  { to: "/app/manage/announcements", label: "Moderation", icon: ShieldCheck },
  { to: "/app/manage/analytics", label: "Analytics", icon: Activity },
];

function roleLabel(user) {
  if (user.role === "admin") return "Site admin";
  if (user.is_group_owner) return "Group owner";
  return "Student";
}

function NavItem({ to, label, icon: Icon, end, badge, onNavigate }) {
  return (
    <NavLink to={to} end={end} onClick={onNavigate} className="relative block rounded-xl">
      {({ isActive }) => (
        <>
          {isActive && (
            // layoutId makes this pill glide from the old item to the new one.
            <motion.span
              layoutId="nav-pill"
              className="absolute inset-0 rounded-xl bg-moss"
              transition={{ type: "spring", stiffness: 420, damping: 36 }}
            />
          )}
          <span
            className={cx(
              "relative z-10 flex items-center gap-3 px-3.5 py-2.5 text-[15px] font-medium transition-colors",
              isActive ? "text-paper" : "text-ink-2 hover:text-ink"
            )}
          >
            <Icon className="size-[18px]" />
            {label}
            {badge > 0 && (
              <span className="ml-auto grid min-w-5 place-items-center rounded-full bg-clay px-1.5 text-xs font-semibold text-paper">
                {badge > 99 ? "99+" : badge}
              </span>
            )}
          </span>
        </>
      )}
    </NavLink>
  );
}

function SidebarBody({ onNavigate }) {
  const { user, canManage, logout } = useAuth();
  const navigate = useNavigate();

  // Unread count for the bell badge; re-checked every 30 seconds.
  const { data: unread = 0 } = useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: async () => (await api.get("/notifications", { params: { unread_only: true, limit: 200 } })).data.length,
    refetchInterval: 30000,
  });

  const studentNav = [
    { to: "/app", label: "Feed", icon: Newspaper, end: true },
    { to: "/app/notifications", label: "Notifications", icon: Bell, badge: unread },
    { to: "/app/groups", label: "Following", icon: Rss },
    { to: "/app/claim", label: user.is_group_owner ? "Add another group" : "Own a group", icon: Link2 },
  ];

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <div className="flex h-full flex-col">
      <div className="px-6 pb-6 pt-7">
        <Logo />
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-4">
        {studentNav.map((item) => (
          <NavItem key={item.to} {...item} onNavigate={onNavigate} />
        ))}

        {canManage && (
          <>
            <p className="px-3.5 pb-2 pt-7 text-xs font-semibold uppercase tracking-[0.16em] text-ink-3">Manage</p>
            {MANAGE_NAV.map((item) => (
              <NavItem key={item.to} {...item} onNavigate={onNavigate} />
            ))}
          </>
        )}
      </nav>

      <div className="m-4 flex items-center gap-3 rounded-2xl border border-line bg-card p-3">
        <div className="grid size-10 shrink-0 place-items-center rounded-full bg-ochre/25 font-display text-[15px] text-ink">
          {initials(user.name)}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-ink">{user.name}</p>
          <p className="text-xs text-ink-3">{roleLabel(user)}</p>
        </div>
        <button
          onClick={handleLogout}
          aria-label="Log out"
          title="Log out"
          className="cursor-pointer rounded-full p-2 text-ink-3 transition hover:bg-paper-2 hover:text-clay"
        >
          <LogOut className="size-[18px]" />
        </button>
      </div>
    </div>
  );
}

export function AppShell() {
  const [drawer, setDrawer] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-line bg-paper lg:block">
        <SidebarBody />
      </aside>

      {/* Mobile top bar */}
      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-line bg-paper/90 px-5 py-3 backdrop-blur lg:hidden">
        <Logo />
        <button onClick={() => setDrawer(true)} aria-label="Open menu" className="rounded-full p-2 hover:bg-paper-2">
          <Menu className="size-6" />
        </button>
      </header>

      {/* Mobile drawer */}
      <AnimatePresence>
        {drawer && (
          <motion.div className="fixed inset-0 z-40 lg:hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="absolute inset-0 bg-ink/40" onClick={() => setDrawer(false)} />
            <motion.aside
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: "spring", stiffness: 380, damping: 38 }}
              className="absolute inset-y-0 left-0 w-72 bg-paper shadow-2xl"
            >
              <button onClick={() => setDrawer(false)} aria-label="Close menu" className="absolute right-3 top-4 rounded-full p-2 hover:bg-paper-2">
                <X className="size-5" />
              </button>
              <SidebarBody onNavigate={() => setDrawer(false)} />
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Page content; re-animates on every route change */}
      <motion.main
        key={location.pathname}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="lg:pl-72"
      >
        <div className="mx-auto max-w-5xl px-5 py-8 sm:px-10 sm:py-12">
          <Outlet />
        </div>
      </motion.main>
    </div>
  );
}
