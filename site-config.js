const SITE_CONFIG = {
  company: "Suppix AI UG",
  brand: "SUPPIX AI",
  platform: "WorkPass",
  product: "WorkPass",
  tagline: "Identität · Zutritt · Team · Sicherheit · White-Label",
  email: "support@suppix-ai.com",
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

  /** Technisch erreichbare Website-URL (QR, Formulare, Danke-Seiten). */
  liveUrl: "https://baukometra10.github.io/suppix-ai.com",

  /**
   * Sichtbarer Domain-Name auf Flyer/Marketing (ohne https://).
   * Leer = auf dem Flyer keine Domain anzeigen (nur QR).
   * Später z. B. "suppix-ai.com" setzen, sobald das Marketing-Domain live ist.
   */
  marketingDisplayHost: "",

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

  domain: "suppix-ai-workpass.com",
  url: "https://suppix-ai-workpass.com",

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

  formEndpoint: "https://formsubmit.co/ajax/support@suppix-ai.com",
  /** Klassisches FormSubmit (nicht AJAX) – nötig für Auto-Antwort an den Kunden. */
  formAction: "https://formsubmit.co/support@suppix-ai.com",
};
