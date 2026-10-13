# Demo-Reminder & Angebot

## 24h-Reminder

- Cron: stündlich (`0 * * * *` in `wrangler.toml`)
- Fenster: Termin in **20–28 Stunden**
- Kunde: Erinnerungs-E-Mail (Resend)
- Owner: E-Mail mit WhatsApp-Vorlage-Link + Link zu `angebot.html`
- Spalte: `demo_bookings.reminder_sent_at`

Migration (einmalig remote):

```bash
cd workers
npx wrangler d1 execute suppixai-bookings --remote --file=./schema-reminders.sql
```

Manuell testen:

```bash
curl -X POST https://suppixai-contact.suppix-ai.workers.dev/cron/reminders \
  -H "X-Cron-Key: $MARKETING_BOOKING_WEBHOOK_KEY"
```

## Angebot

- UI: https://suppixai.com/angebot.html (drucken = PDF)
- API: `POST /offer` (E-Mail an Kunde + Owner)
- Query-Params: `?name=&email=&company=&paket=&employees=`
