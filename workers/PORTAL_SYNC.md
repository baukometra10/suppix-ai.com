# Demo-Buchungen → WorkPass-Portal

Nach einer Buchung/Absage auf der Marketing-Website pusht der Worker (fire-and-forget) an:

`POST https://suppix-ai-workpass.com/api/webhooks/marketing/demo-booking`

## Secrets (identischer Key auf beiden Seiten)

**Cloudflare Worker**

```bash
cd workers
npx wrangler secret put MARKETING_BOOKING_WEBHOOK_KEY
npx wrangler deploy
```

`WORKPASS_BOOKING_WEBHOOK_URL` steht in `wrangler.toml` (vars).

**WorkPass / baustelle (Produktion)**

```env
MARKETING_BOOKING_WEBHOOK_KEY=<derselbe-wert>
```

## Portal-UI

Superadmin → Betrieb (admin-v2) → Tab **Nutzung & Bewertung** → Abschnitt **Website Demo-Termine**.
