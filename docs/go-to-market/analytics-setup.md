# Analytics & Ads Conversion Setup

1. Google Analytics 4 Property anlegen → Measurement ID `G-…`
2. Optional Google Ads → Conversion-Aktion „Demo-Buchung“ → `send_to` wie `AW-123456789/AbCdEfGh`
3. In `site-config.js`:

```js
analytics: {
  gtagId: "G-XXXXXXXX,AW-123456789", // kommasepariert ok
  adsSendTo: "AW-123456789/AbCdEfGh",
},
```

4. Deploy / Push der Website
5. Test: Demo buchen → in GA4 DebugView Event `demo_booking` prüfen
6. In Google Ads Conversion mit Event `conversion` / `send_to` verknüpfen

Ohne IDs lädt die Seite **kein** gtag-Skript (Privacy-by-default).
