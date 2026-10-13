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

## SMS (optional, Twilio)

Secrets:

```bash
npx wrangler secret put TWILIO_ACCOUNT_SID
npx wrangler secret put TWILIO_AUTH_TOKEN
npx wrangler secret put TWILIO_FROM_NUMBER
```

Phone-Spalte:

```bash
npx wrangler d1 execute suppixai-bookings --remote --file=./schema-phone.sql
```

Kunde trägt optional Telefon im Buchungsformular ein → Reminder per SMS + E-Mail.

## Angebot

- UI: https://suppixai.com/angebot.html (drucken = PDF)
- API: `POST /offer` (E-Mail an Kunde + Owner)
- Query-Params: `?name=&email=&company=&paket=&employees=`
