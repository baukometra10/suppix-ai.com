// Muss an window hängen – script.js liest window.SITE_CONFIG (const allein reicht nicht).
window.SITE_CONFIG = {
  company: "Suppix AI UG",
  brand: "SUPPIX AI",
  platform: "WorkPass",
  product: "WorkPass",
  tagline: "Identität · Zutritt · Team · Sicherheit · White-Label",
  email: "info@suppixai.com",
  phone: "017631676589",
  phoneRaw: "4917631676589",
  whatsapp: "4917631676589",
  appLoginUrl: "https://suppix-ai-workpass.com",

  /**
   * Social Profiles (leere URLs werden nicht angezeigt).
   * YouTube / X bitte ergänzen, sobald Links feststehen.
   */
  social: {
    facebook: "https://www.facebook.com/profile.php?id=61594787245415",
    instagram: "https://www.instagram.com/suppix.workpass.ai/",
    linkedin: "https://www.linkedin.com/in/suppix-ai-8b1758443",
    /** Kanäle ergänzen, sobald URLs feststehen – leer = ausgeblendet */
    youtube: "", // https://www.youtube.com/@…
    x: "", // https://x.com/…
    tiktok: "",
    /** Öffentlicher Google-Business / Maps-Link (auch Bewertungsseite) */
    googleBusiness:
      "https://www.google.com/maps/place/Suppix+AI+UG/@52.535222,13.404971,17z/data=!4m6!3m5!1s0x47a8514752d130e9:0x121f76063e00f284!8m2!3d52.535221972065116!4d13.404971276502327",
  },

  /** Google Maps Embed (Kontaktseite). */
  googleMapsEmbed:
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2426.9011868580797!2d13.404971276502327!3d52.535221972065116!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47a8514752d130e9%3A0x121f76063e00f284!2sSuppix%20AI%20UG!5e0!3m2!1sde!2sde!4v1791956936213!5m2!1sde!2sde",

  /**
   * Öffentliche Bewertungs-API (JSON, ohne Login).
   * Erwartet Array oder { reviews: [...] } mit name/text/rating (oder Aliase).
   * CORS muss https://suppixai.com erlauben.
   * Keine Fake-Fallback-Stimmen: leer = leerer Zustand auf der Website.
   */
  reviewsApiUrl: "https://suppix-ai-workpass.com/api/public/reviews?limit=50",
  /** Max. Karten auf Startseite (Teaser). */
  reviewsHomeLimit: 3,
  /** Max. Karten auf der Bewertungsseite. */
  reviewsPageLimit: 48,
  reviewsLimit: 48,

  /**
   * Dedizierte Bewertungsseiten (relativ zur jeweiligen HTML-Datei).
   * Startseite zeigt Teaser + Button → diese Seiten.
   */
  reviewsPage: {
    de: "bewertungen.html",
    en: "reviews.html",
    ar: "reviews.html",
  },

  /** Optional: echte freigegebene Stimmen. Leer lassen = nur Live-API. */
  reviewsFallback: [],

  /** Öffentliche Marketing-Website (eigene Domain). */
  liveUrl: "https://suppixai.com",

  /**
   * Analytics / Ads (Conversion bei Demo-Buchung).
   * gtagId: GA4 (G-…) und/oder Google Ads (AW-…) – kommasepariert möglich.
   * adsSendTo: optional Google Ads Conversion-Label, z. B. "AW-123/AbCdef".
   * Leer lassen = kein Tracking-Skript (erst IDs eintragen, dann live).
   * Events: demo_booking + optional conversion.
   */
  analytics: {
    // Sobald IDs da sind eintragen – Demo-Buchungen feuern dann automatisch Events.
    gtagId: "", // z. B. "G-XXXXXXXXXX" oder "G-XXX,AW-YYYY"
    adsSendTo: "", // z. B. "AW-YYYY/AbCdef"
  },

  /**
   * Hinweisleiste „Firma/Website in Bearbeitung“.
   * enabled: false → Banner ausblenden (wenn alles final ist).
   */
  siteNotice: {
    enabled: true,
    dismissible: true,
  },

  /** Footer-Zusatz (Markenschutz). */
  copyrightNote:
    "© Suppix AI UG. Logo, Marke und Design geschützt – Nutzung nur mit schriftlicher Erlaubnis.",

  /**
   * Sichtbarer Domain-Name auf Flyer/Marketing (ohne https://).
   * Marketing: suppixai.com · Plattform-Login bleibt appLoginUrl.
   */
  marketingDisplayHost: "suppixai.com",

  /**
   * Demo-/Produktvideo (Fallback). Sprachvarianten: demoVideoByLang.
   */
  demoVideoSrc: "assets/workpass-lohn-bridge-de.mp4",
  demoVideoByLang: {
    de: "assets/workpass-lohn-bridge-de.mp4",
    en: "assets/workpass-lohn-bridge-en.mp4",
    ar: "assets/workpass-lohn-bridge-ar.mp4",
  },

  /**
   * Eigene Demo-Buchung (Cloudflare Worker).
   * Leer = Termin-Links nutzen WhatsApp als Fallback.
   * Gleicher Host wie formApiUrl, Pfade: /booking/slots und /booking
   */
  bookingApiUrl: "https://suppixai-contact.suppix-ai.workers.dev",

  /** Legacy: externe URL (z. B. altes Calendly). Leer = eigene Buchung / WhatsApp. */
  bookingUrl: "",

  media: {
    demoPoster: "assets/video-poster.jpg?v=20261026h",
    /** Logo-Intro vor dem ersten Abspielen (ms), Skip-Button inklusive */
    videoIntroMs: 6500,
    heroCards: true,
  },

  /** Plattform-Login-Domain (App), nicht die Marketing-Website. */
  domain: "suppix-ai-workpass.com",
  url: "https://suppix-ai-workpass.com",

  /**
   * Pflichtangaben Impressum (§ 5 TMG) – VORLÄUFIG, später korrigieren.
   * (Keine Klammern [] verwenden, sonst bleiben die Blöcke verborgen.)
   */
  address: {
    street: "Anschrift folgt (vorläufig)",
    city: "Deutschland",
    country: "Deutschland",
  },
  ceo: "Geschäftsführung – Angaben folgen",
  vatId: "USt-IdNr. folgt",
  registerCourt: "Amtsgericht – Angaben folgen",
  registerNumber: "HRB – Angaben folgen",

  /**
   * Kontaktformular über Resend (eigene Domain) – Cloudflare Worker URL.
   * Leer = Fallback auf FormSubmit.
   * Beispiel: "https://suppixai-contact.XXXX.workers.dev"
   */
  formApiUrl: "https://suppixai-contact.suppix-ai.workers.dev",

  formEndpoint: "https://formsubmit.co/ajax/e007ddb21463c6f3cc39a02e5fc908d9",
  /** Klassisches FormSubmit (Fallback, wenn formApiUrl leer). */
  formAction: "https://formsubmit.co/e007ddb21463c6f3cc39a02e5fc908d9",
};
