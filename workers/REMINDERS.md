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

## Reminder- & Storno-Mails

- Kunden-Erinnerung (~24h vorher): HTML mit Logo, Termin-Box, Buttons (Teams / Verwalten / Demo)
- Absage (`termin.html` → POST cancel): Status `cancelled` in D1, Slot frei, HTML-Mail an Kunde + Owner (`STORNIERT:…` an OWNER_EMAIL und TO_EMAIL)

## Microsoft Teams (kostenlos möglich)

1. In Teams (App oder teams.microsoft.com) Meeting erstellen bzw. „Jetzt besprechen“ → Link kopieren  
2. In `wrangler.toml` setzen: `TEAMS_MEETING_URL = "https://teams.microsoft.com/l/meetup-join/…"`  
3. Worker neu deployen  

Der Link erscheint in Bestätigung, Reminder und ICS. Ohne URL kein Teams-Button (Demo bleibt per Termin-Absprache).

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


## Twilio: SMS nach Deutschland

Absender ist oft eine US-Nummer (`TWILIO_FROM_NUMBER`). In der Twilio Console unter
**Messaging → Settings → Geo permissions** Deutschland (Germany) freischalten,
sonst schlagen Reminder-SMS an DE-Nummern fehl. Trial-Konten senden oft nur an
verifizierte Nummern.
