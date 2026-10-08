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
   * Öffentliche Bewertungs-API (JSON, ohne Login).
   * Erwartet Array oder { reviews: [...] } mit name/text/rating (oder Aliase).
   * CORS muss https://suppixai.com erlauben.
   */
  reviewsApiUrl: "https://suppix-ai-workpass.com/api/public/reviews?limit=12&min_stars=4",
  reviewsLimit: 12,

  /** Öffentliche Marketing-Website (eigene Domain). */
  liveUrl: "https://suppixai.com",

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
   * Terminbuchung: WhatsApp-Deep-Link (später Calendly/Cal.com möglich).
   */
  bookingUrl:
    "https://wa.me/4917631676589?text=" +
    encodeURIComponent("Hallo, ich möchte einen Demo-Termin für WorkPass vereinbaren."),

  media: {
    demoPoster: "assets/video-poster.jpg",
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
