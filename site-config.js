const SITE_CONFIG = {
  company: "Suppix Technologie UG",
  brand: "SUPPIX AI",
  platform: "SUPPIX",
  product: "WorkPass",
  tagline: "Identität · Zutritt · Team · Sicherheit · White-Label",
  email: "baupass-control@outlook.de",
  phone: "017631676589",
  phoneRaw: "4917631676589",
  whatsapp: "4917631676589",
  appLoginUrl: "https://suppix-workpass-ai.up.railway.app/",

  /**
   * Öffentliche Bewertungs-API (JSON).
   * Leer lassen oder korrigieren, sobald die API öffentlich/CORS-fähig ist.
   */
  reviewsApiUrl: "https://suppix-workpass-ai.up.railway.app/api/reviews",
  reviewsLimit: 6,

  /** Später: öffentliche Website-URL (ohne trailing slash). */
  liveUrl: "",

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

  domain: "baupass-controll.de",
  url: "https://baupass-controll.de",

  /** Pflichtangaben Impressum – vor Go-live ersetzen. */
  address: {
    street: "[Straße und Hausnummer]",
    city: "[PLZ Ort]",
    country: "Deutschland",
  },
  ceo: "[Name des Geschäftsführers]",
  vatId: "[USt-IdNr.]",
  registerCourt: "[Amtsgericht]",
  registerNumber: "[HRB-Nummer]",

  formEndpoint: "https://formsubmit.co/ajax/baupass-control@outlook.de",
};
