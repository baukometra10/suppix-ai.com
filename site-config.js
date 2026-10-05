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

  /** Technisch erreichbare Website-URL (QR, Formulare, Danke-Seiten). */
  liveUrl: "https://baukometra10.github.io/suppix-ai.com",

  /**
   * Sichtbarer Domain-Name auf Flyer/Marketing (ohne https://).
   * Produkt-Domain der Plattform (Login). Marketing-Website bleibt liveUrl (GitHub Pages),
   * bis eine eigene Domain (z. B. suppix-ai.com) verdrahtet ist.
   */
  marketingDisplayHost: "suppix-ai-workpass.com",

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

  /**
   * Pflichtangaben Impressum (§ 5 TMG) – echte Werte eintragen, z. B.:
   * street: "Musterstraße 1", city: "12345 Berlin",
   * ceo: "Max Mustermann", vatId: "DE…",
   * registerCourt: "Amtsgericht …", registerNumber: "HRB …"
   * Solange Klammern [] stehen, bleiben diese Blöcke auf der Impressum-Seite verborgen.
   */
  address: {
    street: "[Straße und Hausnummer]",
    city: "[PLZ Ort]",
    country: "Deutschland",
  },
  ceo: "[Name des Geschäftsführers]",
  vatId: "[USt-IdNr.]",
  registerCourt: "[Amtsgericht]",
  registerNumber: "[HRB-Nummer]",

  formEndpoint: "https://formsubmit.co/ajax/info@suppix-ai.com",
  /** Klassisches FormSubmit (nicht AJAX) – nötig für Auto-Antwort an den Kunden. */
  formAction: "https://formsubmit.co/info@suppix-ai.com",
};
