# automotAI Landing Page

Standalone landing page for `automotai.com` — separate from the main app at `app.automotai.com`.

## Structure

- `index.html` — Landing page (hero, features, email waitlist form)
- `server.js` — Simple Node.js server (serves static files + waitlist API)
- `waitlist.json` — Local email storage (swap for Supabase in production)

## Run Locally

```bash
node server.js
# → http://localhost:3001
```

## Deploy

Serve on the root domain (`automotai.com`) via Cloudflare or any static host. The app runs on `app.automotai.com`.
