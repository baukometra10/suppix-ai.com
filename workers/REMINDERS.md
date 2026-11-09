# Demo-Reminder & Angebot

## Zwei Reminder-Stufen

Cron: alle **15 Minuten** (`*/15 * * * *` in `wrangler.toml`)

| Stufe | Fenster | Kunde | Owner | Spalte |
|-------|---------|-------|-------|--------|
| ~24h | Termin in **20–28 Stunden** | E-Mail + SMS (wenn Telefon) | E-Mail + WhatsApp-Vorlage an Kunde | `reminder_sent_at` |
| ~1h | Termin in **45–90 Minuten** | E-Mail + **SMS** | E-Mail + SMS an Owner-Nummer + WhatsApp-Vorlage | `reminder_1h_sent_at` |

Migrationen (einmalig remote):

```bash
cd workers
npx wrangler d1 execute suppixai-bookings --remote --file=./schema-reminders.sql
npx wrangler d1 execute suppixai-bookings --remote --file=./schema-reminders-1h.sql
```

Manuell testen:

```bash
curl -X POST https://suppixai-contact.suppix-ai.workers.dev/cron/reminders \
  -H "X-Cron-Key: $MARKETING_BOOKING_WEBHOOK_KEY"
```

## Reminder- & Storno-Mails

- Kunden-Erinnerung (~24h / ~1h): HTML mit Logo, Termin-Box, Buttons (Teams / Verwalten)
- Absage (`termin.html` → POST cancel): Status `cancelled` in D1, Slot frei, HTML-Mail an Kunde + Owner (`STORNIERT:…` an OWNER_EMAIL und TO_EMAIL)
- Vergangene Termine können nicht storniert werden (API + UI)

## Microsoft Teams (kostenlos möglich)

1. In Teams (App oder teams.microsoft.com) Meeting erstellen bzw. „Jetzt besprechen“ → Link kopieren  
2. In `wrangler.toml` setzen: `TEAMS_MEETING_URL = "https://teams.microsoft.com/l/meetup-join/…"`  
3. Worker neu deployen  

Der Link erscheint in Bestätigung, Reminder und ICS. Ohne URL kein Teams-Button (Demo bleibt per Termin-Absprache).

## SMS (Twilio)

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

Kunde trägt Telefon im Buchungsformular ein → Reminder per SMS + E-Mail.
Ohne Telefon: nur E-Mail (1h-SMS entfällt für den Kunden).

## WhatsApp-Vorlage (Owner → Kunde)

In der Owner-Mail steht ein Link **WhatsApp an Kunde** (`wa.me/<Kundentelefon>?text=…`) mit professionellem DE/EN/AR-Text (Bestätigung bzw. Erinnerung).  
Voraussetzung: Telefonnummer bei der Buchung.

## Angebot

- UI: https://suppixai.com/angebot.html (drucken = PDF)
- API: `POST /offer` (E-Mail an Kunde + Owner)
- Query-Params: `?name=&email=&company=&paket=&employees=`


## Twilio: SMS nach Deutschland

Absender ist oft eine US-Nummer (`TWILIO_FROM_NUMBER`). In der Twilio Console unter
**Messaging → Settings → Geo permissions** Deutschland (Germany) freischalten,
sonst schlagen Reminder-SMS an DE-Nummern fehl. Trial-Konten senden oft nur an
verifizierte Nummern.
