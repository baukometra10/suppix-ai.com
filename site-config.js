const SITE_CONFIG = {
  company: "Suppix AI UG",
  brand: "SUPPIX AI",
  platform: "WorkPass",
  product: "WorkPass",
  tagline: "Identität · Zutritt · Team · Sicherheit · White-Label",
  email: "info@suppix-ai.com",
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
  liveUrl: "https://suppix-ai.com",

  /**
   * Sichtbarer Domain-Name auf Flyer/Marketing (ohne https://).
   * Marketing: suppix-ai.com · Plattform-Login bleibt appLoginUrl.
   */
  marketingDisplayHost: "suppix-ai.com",

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

  formEndpoint: "https://formsubmit.co/ajax/info@suppix-ai.com",
  /** Klassisches FormSubmit (nicht AJAX) – nötig für Auto-Antwort an den Kunden. */
  formAction: "https://formsubmit.co/info@suppix-ai.com",
};
