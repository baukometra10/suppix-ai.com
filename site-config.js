const SITE_CONFIG = {
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
   * Öffentliche Bewertungs-API (JSON).
   * Leer lassen oder korrigieren, sobald die API öffentlich/CORS-fähig ist.
   */
  reviewsApiUrl: "https://suppix-workpass-ai.up.railway.app/api/reviews",
  reviewsLimit: 6,

  /** Öffentliche Marketing-Website (eigene Domain). */
  liveUrl: "https://suppixai.com",

  /**
   * Sichtbarer Domain-Name auf Flyer/Marketing (ohne https://).
   * Marketing: suppixai.com · Plattform-Login bleibt appLoginUrl.
   */
  marketingDisplayHost: "suppixai.com",

  /**
   * Demo-Video: z. B. "assets/suppix-demo.mp4"
   * Leer = Platzhalter „Demo-Video folgt“.
   */
  demoVideoSrc: "",

  /**
   * Terminbuchung (Calendly / Cal.com / eigener Link).
   * Leer = WhatsApp/Telefon als Buchungsweg.
   */
  bookingUrl: "",

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
  formApiUrl: "",

  formEndpoint: "https://formsubmit.co/ajax/e007ddb21463c6f3cc39a02e5fc908d9",
  /** Klassisches FormSubmit (Fallback, wenn formApiUrl leer). */
  formAction: "https://formsubmit.co/e007ddb21463c6f3cc39a02e5fc908d9",
};
