# Noticeboard (frontend)

React 19 + Vite + Tailwind CSS v4 + Motion (animations) + TanStack Query + React Router.

## Run it

```bash
cd frontend
cp .env.example .env        # then edit VITE_API_URL if needed
npm install
npm run dev                 # http://localhost:5173
```

Build for production: `npm run build` (output in `dist/`), preview with `npm run preview`.

## IMPORTANT: allow the frontend in the backend (CORS)

The browser blocks API calls from origins the backend doesn't list. On your backend host (Pxxl),
set this environment variable and redeploy the API:

```
CORS_ORIGINS=http://localhost:5173,https://YOUR-FRONTEND-DOMAIN
```

(comma-separated, no trailing slashes). Without it every request fails with a CORS error.

## Pages

| URL | Who | What |
|---|---|---|
| `/` | everyone | Landing page |
| `/login`, `/register` | guests | Auth |
| `/app` | signed in | Feed: search + filter + pagination |
| `/app/notifications` | signed in | In-app notifications, mark read |
| `/app/groups` | signed in | Choose which groups to follow |
| `/app/claim` | signed in | Claim a Telegram group with a one-time code |
| `/app/manage/groups` | admin / group owner | Groups, activate/pause/remove |
| `/app/manage/groups/:id` | admin / group owner | Keyword manager + student suggestions |
| `/app/manage/announcements` | admin / group owner | Archive / restore / delete |
| `/app/manage/analytics` | admin / group owner | Totals, timeline, breakdowns |

The "Manage" menu only shows for site admins and for students who own a group. The backend enforces
the same rules, so hiding a link is a convenience, never the security.

## Folder map

```
src/
  main.jsx            entry: Router + React Query
  App.jsx             all routes
  index.css           Tailwind + design tokens (colours, fonts)
  lib/                api client (tokens, auto-refresh), formatting helpers, brand name
  auth/               AuthContext (login/logout/session) + route guards
  hooks/              useDebounce
  components/         ui kit, app shell/sidebar, toasts, animation helpers
  pages/              one file per screen (pages/manage = owner/admin screens)
public/_redirects     makes deep links work on Netlify-style static hosts
```

## Deploying

It's a static site: any static host works (Netlify, Vercel, Cloudflare Pages, Pxxl static).
Set `VITE_API_URL` in the host's build environment. Make sure the host rewrites unknown paths to
`index.html` (`public/_redirects` handles Netlify/Cloudflare; Vercel needs a rewrite rule).

## Rename the product

Edit `src/lib/brand.js` (name + tagline) and the wordmark in `index.html`'s `<title>`.
