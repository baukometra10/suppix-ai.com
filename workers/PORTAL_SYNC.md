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

---

# Kundenbewertungen → Marketing-Website

## Sync (Stand 2026-10-16)

Jede System-Bewertung (E-Mail-Link **oder** In-App-Umfrage) landet automatisch in `customer_reviews` und damit auf `GET /api/public/reviews` → Marketing-Website.

| Aktion | Portal | Website |
|--------|--------|---------|
| Umfrage absenden | `POST /api/v2/satisfaction-survey` | erscheint in Testimonials |
| Bewertung löschen | `DELETE /api/v2/admin/satisfaction-surveys/<id>` (Button **Entfernen**) | verschwindet |
| Token-Bewertung | `POST /api/public/review/submit` | erscheint ebenfalls |
| Public Review löschen | `DELETE /api/v2/admin/customer-reviews/<id>` | verschwindet (+ verknüpfte Umfrage) |

Score-Mapping: Umfrage **1 = sehr gut** → Website **5 Sterne**. Öffentlicher Name = Firmenname (kein Username/E-Mail).

Historische Umfragen werden beim nächsten `GET /api/public/reviews` per Backfill nachgezogen.

Marketing: `site-config.js` → `reviewsApiUrl` → `script.js` `initLiveReviews()` (parst `text`/`review_text`, `stars`/`rating`).
