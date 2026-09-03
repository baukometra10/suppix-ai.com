document.addEventListener("DOMContentLoaded", () => {
  const cfg = window.SITE_CONFIG || {};

  applySiteConfig();
  initDemoVideo();
  initHeader();
  initSmoothScroll();
  initContactForm();
  initNewsletterForm();
  initFaq();
  initPriceCalculator();
  initCookieBanner();
  initWhatsApp();
  initContactWhatsApp();
  initHeroWhatsApp();
  initBookingLinks();
  initOutboundThanks();
  initStickyMobileCta();
  initScrollReveal();
  initFooterYear();
  initFlyerQr();
  initLiveReviews();
  initImpressumPending();

  function sitePublicUrl() {
    if (cfg.liveUrl) return cfg.liveUrl;
    if (cfg.url && !cfg.url.includes("[") && cfg.url.startsWith("http")) return cfg.url;
    if (typeof window !== "undefined" && window.location?.origin && window.location.origin !== "null") {
      return window.location.origin.replace(/\/$/, "");
    }
    return "";
  }

  function pageLang() {
    return String(document.documentElement.lang || "de").toLowerCase().slice(0, 2);
  }

  function isEnglish() {
    return pageLang() === "en";
  }

  function isArabic() {
    return pageLang() === "ar";
  }

  function t(de, en, ar) {
    const lang = pageLang();
    if (lang === "en") return en;
    if (lang === "ar") return ar != null ? ar : en;
    return de;
  }

  function whatsappUrl(message) {
    const phone = String(cfg.whatsapp || cfg.phoneRaw || "4917631676589").replace(/\D/g, "");
    return `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
  }

  function setWhatsAppLink(link, message) {
    if (!link) return;
    link.href = whatsappUrl(message);
    link.removeAttribute("target");
    link.removeAttribute("rel");
  }

  function platformName() {
    return cfg.platform || cfg.product || "WorkPass";
  }

  function initContactWhatsApp() {
    const link = document.getElementById("contactWhatsApp");
    setWhatsAppLink(
      link,
      t(
        `Hallo, ich interessiere mich für ${platformName()}.`,
        `Hello, I am interested in ${platformName()}.`,
        `مرحبا، أهتم بـ ${platformName()}.`
      )
    );
  }

  function initBookingLinks() {
    const booking = String(cfg.bookingUrl || "").trim();
    document.querySelectorAll("[data-booking]").forEach((el) => {
      if (booking) {
        el.href = booking;
        el.hidden = false;
        el.target = "_blank";
        el.rel = "noopener noreferrer";
        if (!el.textContent.trim()) {
          el.textContent = t("Termin online buchen", "Book a time online", "احجز موعداً أونلاين");
        }
      } else {
        // Fallback: WhatsApp demo request
        setWhatsAppLink(
          el,
          t(
            `Hallo, ich möchte einen Demo-Termin für ${platformName()} vereinbaren.`,
            `Hello, I would like to schedule a ${platformName()} demo.`,
            `مرحبا، أود حجز موعد عرض لـ ${platformName()}.`
          )
        );
        el.hidden = false;
        if (el.dataset.bookingLabel === "auto" || !el.textContent.trim()) {
          el.textContent = t(
            "Termin per WhatsApp anfragen",
            "Request a time via WhatsApp",
            "اطلب موعداً عبر واتساب"
          );
        }
      }
    });

    document.querySelectorAll("[data-booking-only]").forEach((el) => {
      el.hidden = !booking;
    });
  }

  function isPlaceholderValue(value) {
    const v = String(value || "").trim();
    return !v || v.includes("[") || v.includes("]");
  }

  function initImpressumPending() {
    const pending = document.getElementById("impressumPending");
    if (!pending) return;
    const incomplete =
      isPlaceholderValue(cfg.address?.street) ||
      isPlaceholderValue(cfg.address?.city) ||
      isPlaceholderValue(cfg.ceo) ||
      isPlaceholderValue(cfg.vatId) ||
      isPlaceholderValue(cfg.registerCourt) ||
      isPlaceholderValue(cfg.registerNumber);
    pending.hidden = !incomplete;
  }

  function initHeroWhatsApp() {
    const link = document.getElementById("heroWhatsApp");
    setWhatsAppLink(
      link,
      t(
        `Hallo, ich interessiere mich für ${platformName()}.`,
        `Hello, I am interested in ${platformName()}.`,
        `مرحبا، أهتم بـ ${platformName()}.`
      )
    );
  }

  function applyBranding() {
    document.querySelectorAll("[data-brand-platform]").forEach((el) => {
      if (cfg.platform) el.textContent = cfg.platform;
    });
    document.querySelectorAll("[data-brand-product]").forEach((el) => {
      if (cfg.product) el.textContent = cfg.product;
    });
    document.querySelectorAll("[data-brand-company]").forEach((el) => {
      if (cfg.company) el.textContent = cfg.company;
    });
    document.querySelectorAll("[data-brand-name]").forEach((el) => {
      if (cfg.brand || cfg.company) el.textContent = cfg.brand || cfg.company;
    });
    document.querySelectorAll("[data-brand-tagline]").forEach((el) => {
      if (cfg.tagline) el.textContent = cfg.tagline;
    });
    if (cfg.company && cfg.platform) {
      document.title = document.title
        .replace(
          /Baupass Controll|Baukometra|Suppix AI UG|Suppix Technologie UG|Suppix AI|SUPPIX|WorkPass/g,
          (m) => {
            if (m === "Baupass Controll" || m === "SUPPIX" || m === "WorkPass") {
              return cfg.platform || cfg.product || "WorkPass";
            }
            if (
              m === "Baukometra" ||
              m === "Suppix AI UG" ||
              m === "Suppix AI" ||
              m === "Suppix Technologie UG"
            ) {
              return cfg.company || cfg.brand || m;
            }
            return m;
          }
        );
    }
  }

  function initDemoVideo() {
    const video = document.getElementById("demoVideo");
    const stage = document.getElementById("demoVideoStage");
    const soon = document.getElementById("demoVideoSoon");
    const src = cfg.demoVideoSrc || "";
    if (!video || !stage) return;
    if (src) {
      stage.classList.remove("is-soon");
      video.querySelector("source")?.setAttribute("src", src);
      video.load();
      if (soon) soon.hidden = true;
      video.hidden = false;
    } else {
      stage.classList.add("is-soon");
      video.hidden = true;
      if (soon) soon.hidden = false;
    }
  }

  function applySiteConfig() {
    applyBranding();

    document.querySelectorAll("[data-email]").forEach((el) => {
      if (cfg.email) {
        el.textContent = cfg.email;
        if (el.tagName === "A") el.href = `mailto:${cfg.email}`;
      }
    });
    document.querySelectorAll("[data-phone]").forEach((el) => {
      if (cfg.phone) el.textContent = cfg.phone;
    });
    document.querySelectorAll("[data-phone-link]").forEach((el) => {
      if (cfg.phoneRaw) {
        el.href = `tel:+${cfg.phoneRaw}`;
        if (cfg.phone) el.textContent = cfg.phone;
      }
    });
    document.querySelectorAll("[data-login]").forEach((el) => {
      const url = cfg.appLoginUrl || "index.html#vorschau";
      el.href = url;
      if (/^https?:\/\//i.test(url)) {
        el.target = "_blank";
        el.rel = "noopener noreferrer";
      }
    });
    document.querySelectorAll("[data-site-url]").forEach((el) => {
      const url = sitePublicUrl();
      if (url) el.textContent = url.replace(/^https?:\/\//, "");
    });
    document.querySelectorAll("[data-browser-url]").forEach((el) => {
      const host = String(cfg.domain || cfg.url || "suppix-ai-workpass.com")
        .replace(/^https?:\/\//, "")
        .replace(/\/$/, "");
      if (host) el.textContent = `🔒 https://${host}`;
    });
    document.querySelectorAll("form.contact-form").forEach((form) => {
      if (cfg.formAction) form.setAttribute("action", cfg.formAction);
    });
    document.querySelectorAll("[data-address-street]").forEach((el) => {
      if (cfg.address?.street) el.textContent = cfg.address.street;
    });
    document.querySelectorAll("[data-address-city]").forEach((el) => {
      if (cfg.address?.city) el.textContent = cfg.address.city;
    });
    document.querySelectorAll("[data-ceo]").forEach((el) => {
      if (cfg.ceo) el.textContent = cfg.ceo;
    });
    document.querySelectorAll("[data-vat]").forEach((el) => {
      if (cfg.vatId) el.textContent = cfg.vatId;
    });
    document.querySelectorAll("[data-register-court]").forEach((el) => {
      if (cfg.registerCourt) el.textContent = cfg.registerCourt;
    });
    document.querySelectorAll("[data-register-number]").forEach((el) => {
      if (cfg.registerNumber) el.textContent = cfg.registerNumber;
    });
    document.querySelectorAll("[data-register]").forEach((el) => {
      if (cfg.registerCourt && cfg.registerNumber) {
        el.textContent = `${cfg.registerCourt}, ${cfg.registerNumber}`;
      }
    });
  }

  function initHeader() {
    const header = document.getElementById("header");
    const hamburgerBtn = document.getElementById("hamburgerBtn");
    const mobileNav = document.getElementById("mobileNav");

    if (header) {
      window.addEventListener("scroll", () => {
        header.classList.toggle("scrolled", window.scrollY > 20);
      });
    }

    if (hamburgerBtn && mobileNav) {
      const setMenuOpen = (open) => {
        mobileNav.classList.toggle("open", open);
        document.body.classList.toggle("nav-open", open);
        hamburgerBtn.setAttribute("aria-expanded", open ? "true" : "false");
        hamburgerBtn.setAttribute(
          "aria-label",
          open
            ? t("Menü schließen", "Close menu", "إغلاق القائمة")
            : t("Menü öffnen", "Open menu", "فتح القائمة")
        );
      };

      const syncHeaderOffset = () => {
        const header = document.getElementById("header");
        if (!header) return;
        document.documentElement.style.setProperty("--header-offset", `${header.offsetHeight}px`);
      };
      syncHeaderOffset();
      window.addEventListener("resize", syncHeaderOffset);

      hamburgerBtn.addEventListener("click", () => {
        setMenuOpen(!mobileNav.classList.contains("open"));
        syncHeaderOffset();
      });
      mobileNav.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => setMenuOpen(false));
      });
    }
  }

  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", (e) => {
        const targetId = anchor.getAttribute("href");
        if (targetId === "#") return;
        const target = document.querySelector(targetId);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });
  }

  async function submitToFormSubmit(data, statusEl) {
    const endpoint = cfg.formEndpoint;
    if (!endpoint) return false;

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          ...data,
          _subject: data._subject || `${platformName()} Anfrage`,
          _captcha: "false",
          _template: "table",
        }),
      });
      return res.ok;
    } catch {
      return false;
    }
  }

  function thanksTitle() {
    return t(
      "Vielen Dank für Ihre Anfrage!",
      "Thank you for your request!",
      "شكراً لك على طلبك!"
    );
  }

  function thanksBody() {
    return t(
      "Ihre Nachricht ist bei uns eingegangen. Wir melden uns so schnell wie möglich bei Ihnen – in der Regel innerhalb kurzer Zeit.",
      "We have received your message. We will contact you as soon as possible – usually within a short time.",
      "استلمنا رسالتك وسنتواصل معك في أقرب وقت ممكن."
    );
  }

  function thanksOutboundBody() {
    return t(
      "Vielen Dank! Bitte senden Sie Ihre Nachricht ab – danach melden wir uns so schnell wie möglich bei Ihnen.",
      "Thank you! Please send your message – then we will contact you as soon as possible.",
      "شكراً لك! بعد إرسال رسالتك سنتواصل معك في أقرب وقت ممكن."
    );
  }

  function ensureThanksToast() {
    let toast = document.getElementById("thanksToast");
    if (toast) return toast;
    toast = document.createElement("div");
    toast.id = "thanksToast";
    toast.className = "thanks-toast";
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    toast.hidden = true;
    document.body.appendChild(toast);
    return toast;
  }

  function showThanksToast(message) {
    const toast = ensureThanksToast();
    toast.innerHTML = `<strong>${thanksTitle()}</strong><p>${message || thanksOutboundBody()}</p>`;
    toast.hidden = false;
    toast.classList.add("is-visible");
    clearTimeout(showThanksToast._timer);
    showThanksToast._timer = setTimeout(() => {
      toast.classList.remove("is-visible");
      toast.hidden = true;
    }, 7000);
  }

  function showContactFormThanks(form, statusEl) {
    const title = thanksTitle();
    const body = thanksBody();

    let panel = document.getElementById("contactThanks");
    if (!panel) {
      panel = document.createElement("div");
      panel.id = "contactThanks";
      panel.className = "contact-thanks";
      panel.setAttribute("role", "status");
      panel.setAttribute("aria-live", "polite");
      form.insertAdjacentElement("beforebegin", panel);
    }

    panel.innerHTML = `
      <div class="contact-thanks-icon" aria-hidden="true">✓</div>
      <h3>${title}</h3>
      <p>${body}</p>
      <p class="contact-thanks-note">${t(
        "Sie können die Seite schließen oder weiter stöbern – wir melden uns bei Ihnen.",
        "You can close this page or keep browsing – we will get in touch.",
        "يمكنك إغلاق الصفحة أو متابعة التصفح – سنتواصل معك."
      )}</p>
    `;
    panel.hidden = false;
    form.hidden = true;

    if (statusEl) {
      statusEl.className = "form-status success";
      statusEl.textContent = `${title} ${body}`;
    }

    panel.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function initOutboundThanks() {
    const mark = (el) => {
      if (!el || el.dataset.thanksBound === "1") return;
      el.dataset.thanksBound = "1";
      el.addEventListener("click", () => {
        showThanksToast(thanksOutboundBody());
      });
    };

    [
      "contactWhatsApp",
      "heroWhatsApp",
      "whatsappBtn",
      "mobileCtaWhatsapp",
      "thanksWhatsApp",
    ].forEach((id) => mark(document.getElementById(id)));

    document.querySelectorAll("[data-booking], a[href*='wa.me'], a[href^='mailto:']").forEach(mark);
  }

  function siteBaseUrl() {
    const configured = String(cfg.liveUrl || cfg.url || "").replace(/\/$/, "");
    if (configured) return configured;
    if (typeof window !== "undefined" && window.location?.origin && window.location.origin !== "null") {
      return window.location.origin;
    }
    return "https://baukometra10.github.io/suppix-ai.com";
  }

  function logoAbsoluteUrl() {
    return `${siteBaseUrl()}/assets/logo.png`;
  }

  function thankYouAbsoluteUrl() {
    const lang = (document.documentElement.lang || "de").toLowerCase();
    if (lang.startsWith("ar")) return `${siteBaseUrl()}/ar/thanks.html`;
    if (lang.startsWith("en")) return `${siteBaseUrl()}/en/thanks.html`;
    return `${siteBaseUrl()}/danke.html`;
  }

  function ensureHiddenInput(form, name, value) {
    let input = form.querySelector(`input[type="hidden"][name="${name}"]`);
    if (!input) {
      input = document.createElement("input");
      input.type = "hidden";
      input.name = name;
      form.prepend(input);
    }
    input.value = value;
    return input;
  }

  function buildCustomerAutoresponse(name) {
    const company = cfg.company || "Suppix AI UG";
    const platform = platformName();
    const brand = cfg.brand || "SUPPIX AI";
    const email = cfg.email || "support@suppix-ai.com";
    const phone = cfg.phone || "017631676589";
    const whatsapp = cfg.whatsapp || cfg.phoneRaw || "4917631676589";
    const logo = logoAbsoluteUrl();
    const website = siteBaseUrl();
    const who = (name || "").trim();

    const greeting = t(
      who ? `Hallo ${who},` : "Hallo,",
      who ? `Hello ${who},` : "Hello,",
      who ? `مرحباً ${who}،` : "مرحباً،"
    );
    const thanks = t(
      `vielen Dank für Ihre Anfrage zu <strong>${platform}</strong>. Wir haben Ihre Nachricht erhalten und melden uns <strong>so schnell wie möglich</strong> bei Ihnen.`,
      `thank you for your <strong>${platform}</strong> request. We have received your message and will contact you <strong>as soon as possible</strong>.`,
      `شكراً لطلبك بخصوص <strong>${platform}</strong>. استلمنا رسالتك وسنتواصل معك <strong>في أقرب وقت ممكن</strong>.`
    );
    const contactTitle = t("Unsere Kontaktdaten", "Our contact details", "بيانات التواصل الخاصة بنا");
    const closing = t(
      `Mit freundlichen Grüßen<br>Ihr Team von ${company}`,
      `Kind regards<br>Your team at ${company}`,
      `مع أطيب التحيات<br>فريق ${company}`
    );

    // HTML confirmation email (logo + contact). FormSubmit delivers this as the autoresponse body.
    return `
<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:0 auto;color:#0f172a;line-height:1.55">
  <div style="text-align:center;padding:16px 0 8px">
    <img src="${logo}" alt="${brand}" width="180" style="max-width:180px;height:auto;border:0" />
  </div>
  <p style="font-size:16px;margin:0 0 12px">${greeting}</p>
  <p style="font-size:15px;margin:0 0 16px">${thanks}</p>
  <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px 16px;margin:0 0 16px">
    <p style="margin:0 0 8px;font-weight:700">${contactTitle}</p>
    <p style="margin:0">${company} · ${platform}<br>
    E-Mail: <a href="mailto:${email}">${email}</a><br>
    Telefon: <a href="tel:+${String(whatsapp).replace(/\D/g, "")}">${phone}</a><br>
    WhatsApp: <a href="https://wa.me/${whatsapp}">https://wa.me/${whatsapp}</a><br>
    Web: <a href="${website}">${website}</a></p>
  </div>
  <p style="font-size:14px;margin:0;color:#334155">${closing}</p>
</div>`.trim();
  }

  function initContactForm() {
    const form = document.getElementById("contactForm");
    if (!form) return;

    const action =
      cfg.formAction ||
      (cfg.email ? `https://formsubmit.co/${cfg.email}` : "https://formsubmit.co/support@suppix-ai.com");
    form.setAttribute("action", action);
    form.setAttribute("method", "POST");
    form.setAttribute("accept-charset", "UTF-8");

    // Autoresponse requires classic POST + captcha (do NOT disable captcha).
    ensureHiddenInput(form, "_template", "table");
    ensureHiddenInput(form, "_next", thankYouAbsoluteUrl());
    ensureHiddenInput(form, "_autoresponse", buildCustomerAutoresponse(""));
    ensureHiddenInput(
      form,
      "_subject",
      t(`${platformName()} Anfrage`, `${platformName()} request`, `طلب ${platformName()}`)
    );

    const privacy = form.querySelector("#privacy");
    if (privacy && !privacy.name) privacy.name = "privacy";
    if (privacy && !privacy.value) privacy.value = "accepted";

    form.addEventListener("submit", () => {
      const btn = form.querySelector('button[type="submit"]');
      const name = (document.getElementById("name")?.value || "").trim();
      const email = (document.getElementById("email")?.value || "").trim();
      const statusEl = document.getElementById("contactStatus");

      ensureHiddenInput(
        form,
        "_subject",
        t(
          `Demo-Anfrage – ${name || "Kunde"}`,
          `Demo request – ${name || "Customer"}`,
          `طلب عرض – ${name || "عميل"}`
        )
      );
      ensureHiddenInput(form, "_autoresponse", buildCustomerAutoresponse(name));
      ensureHiddenInput(form, "_next", thankYouAbsoluteUrl());
      if (email) ensureHiddenInput(form, "_replyto", email);

      if (btn) {
        btn.disabled = true;
        btn.textContent = t("Wird gesendet…", "Sending…", "جاري الإرسال…");
      }
      if (statusEl) {
        statusEl.className = "form-status success";
        statusEl.textContent = t(
          "Einen Moment… Sie erhalten gleich eine Bestätigung per E-Mail.",
          "One moment… You will receive a confirmation email shortly.",
          "لحظة… ستصلك رسالة تأكيد على بريدك قريباً."
        );
      }
      // Native FormSubmit POST continues (no preventDefault) → customer autoresponse email.
    });
  }

  function initNewsletterForm() {
    const form = document.getElementById("newsletterForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("newsletterEmail").value.trim();
      const statusEl = document.getElementById("newsletterStatus");
      const btn = form.querySelector("button");

      btn.disabled = true;
      const ok = await submitToFormSubmit(
        { _subject: "Newsletter-Anmeldung", email, typ: "Newsletter" },
        statusEl
      );

      if (ok) {
        statusEl.className = "form-status success";
        statusEl.textContent = t(
          `Erfolgreich angemeldet! Willkommen bei ${platformName()}.`,
          `Successfully subscribed! Welcome to ${platformName()}.`
        );
        form.reset();
      } else {
        statusEl.className = "form-status error";
        statusEl.textContent = t(
          "Fehler – bitte versuchen Sie es später oder schreiben Sie uns direkt.",
          "Error – please try again later or email us directly."
        );
      }
      btn.disabled = false;
    });
  }

  function initFaq() {
    document.querySelectorAll(".faq-question").forEach((btn) => {
      btn.addEventListener("click", () => {
        const item = btn.closest(".faq-item");
        const isOpen = item.classList.contains("open");
        document.querySelectorAll(".faq-item.open").forEach((i) => i.classList.remove("open"));
        if (!isOpen) item.classList.add("open");
      });
    });
  }

  function initPriceCalculator() {
    const paketSelect = document.getElementById("calcPaket");
    const range = document.getElementById("calcEmployees");
    const rangeValue = document.getElementById("calcEmployeesValue");
    const resultPrice = document.getElementById("calcPrice");
    const resultNote = document.getElementById("calcNote");

    if (!paketSelect || !range) return;

    const plans = {
      besucherkarte: { base: 19, perEmployee: 0, threshold: Infinity, label: t("Besucherkarte", "Visitor Card", "بطاقة زائر") },
      starter: { base: 149, perEmployee: 0, threshold: Infinity, label: "Starter" },
      professional: { base: 999, perEmployee: 2.5, threshold: 10, label: "Professional" },
      enterprise: { base: 2490, perEmployee: 3, threshold: 0, label: "Enterprise" },
    };

    function calculate() {
      const plan = plans[paketSelect.value];
      const count = parseInt(range.value, 10);
      rangeValue.textContent = count;

      let total = plan.base;
      if (plan.perEmployee > 0 && count > plan.threshold) {
        total += (count - plan.threshold) * plan.perEmployee;
      }

      resultPrice.textContent = isEnglish()
        ? `€${total.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`
        : `${total.toLocaleString(isArabic() ? "ar-EG" : "de-DE", { minimumFractionDigits: 0, maximumFractionDigits: 2 })} €`;
      resultNote.textContent =
        plan.perEmployee > 0 && count > plan.threshold
          ? t(
              `${plan.label}: ${plan.base} € + ${count - plan.threshold} × ${plan.perEmployee} €`,
              `${plan.label}: €${plan.base} + ${count - plan.threshold} × €${plan.perEmployee}`,
              `${plan.label}: ${plan.base} € + ${count - plan.threshold} × ${plan.perEmployee} €`
            )
          : t(
              `${plan.label}: Alle Mitarbeiter inklusive`,
              `${plan.label}: All employees included`,
              `${plan.label}: جميع الموظفين مشمولون`
            );
    }

    paketSelect.addEventListener("change", calculate);
    range.addEventListener("input", calculate);
    calculate();

    const demoBtn = document.getElementById("calcDemoBtn");
    if (demoBtn) {
      demoBtn.addEventListener("click", () => {
        const contactPaket = document.getElementById("paket");
        const message = document.getElementById("message");
        const count = parseInt(range.value, 10);
        if (contactPaket) contactPaket.value = paketSelect.value;
        if (message) {
          message.value = t(
            `Anfrage über Preisrechner: ${count} Mitarbeiter, Paket „${plans[paketSelect.value].label}“, ca. ${resultPrice.textContent}/Monat.`,
            `Quote via calculator: ${count} employees, plan “${plans[paketSelect.value].label}”, approx. ${resultPrice.textContent}/month.`,
            `طلب عبر الحاسبة: ${count} موظف، الباقة «${plans[paketSelect.value].label}»، تقريباً ${resultPrice.textContent}/شهر.`
          );
        }
        document.getElementById("kontakt")?.scrollIntoView({ behavior: "smooth", block: "start" });
        document.getElementById("contact")?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }

  function initFlyerQr() {
    const img = document.getElementById("flyerQr");
    if (!img) return;
    const url = sitePublicUrl();
    if (!url) return;
    img.src = `https://api.qrserver.com/v1/create-qr-code/?size=176x176&margin=0&data=${encodeURIComponent(url)}`;
  }

  function starsFromRating(rating) {
    const n = Math.max(0, Math.min(5, Math.round(Number(rating) || 5)));
    return "★".repeat(n) + "☆".repeat(5 - n);
  }

  function normalizeReviews(payload) {
    const list = Array.isArray(payload)
      ? payload
      : payload?.reviews || payload?.items || payload?.data || payload?.feedback || payload?.results || [];
    if (!Array.isArray(list)) return [];
    return list
      .map((item) => {
        if (!item || typeof item !== "object") return null;
        const text =
          item.text || item.comment || item.message || item.body || item.review || item.content || "";
        const name =
          item.name || item.author || item.customer || item.company_name || item.display_name || item.user || "";
        const role =
          item.role || item.title || item.position || item.job_title || item.company || item.sector || "";
        const rating = item.rating ?? item.stars ?? item.score ?? 5;
        const published = item.published !== false && item.public !== false && item.approved !== false && item.visible !== false;
        if (!text || !published) return null;
        return {
          text: String(text).trim(),
          name: String(name || t("Kunde", "Customer")).trim(),
          role: String(role || "").trim(),
          rating: Number(rating) || 5,
        };
      })
      .filter(Boolean);
  }

  function renderReviews(reviews) {
    const grid = document.getElementById("testimonialsGrid");
    if (!grid || !reviews.length) return;
    const limit = Math.max(1, Number(cfg.reviewsLimit) || 6);
    grid.innerHTML = reviews
      .slice(0, limit)
      .map(
        (r) => `
      <article class="testimonial-card">
        <div class="testimonial-stars" aria-label="${r.rating} / 5">${starsFromRating(r.rating)}</div>
        <blockquote>${escapeHtml(r.text)}</blockquote>
        <div class="testimonial-author">
          <strong>${escapeHtml(r.name)}</strong>
          ${r.role ? `<span>${escapeHtml(r.role)}</span>` : ""}
        </div>
      </article>`
      )
      .join("");
    const note = document.getElementById("testimonialsNote");
    if (note) {
      note.textContent = t(
        "Echte Kundenstimmen aus der SUPPIX-Plattform.",
        "Real customer reviews from the SUPPIX platform."
      );
      note.classList.add("is-live");
    }
    grid.classList.add("is-live");
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  async function initLiveReviews() {
    const grid = document.getElementById("testimonialsGrid");
    const note = document.getElementById("testimonialsNote");
    const api = (cfg.reviewsApiUrl || "").trim();
    if (!grid || !api) return;

    grid.classList.add("is-loading");
    if (note) {
      note.textContent = t("Lade aktuelle Bewertungen…", "Loading latest reviews…");
    }

    try {
      const res = await fetch(api, {
        method: "GET",
        headers: { Accept: "application/json" },
        mode: "cors",
        credentials: "omit",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const reviews = normalizeReviews(data);
      if (!reviews.length) throw new Error("empty");
      renderReviews(reviews);
    } catch {
      if (note) {
        note.textContent = t(
          "Live-Bewertungen werden verbunden, sobald die öffentliche Reviews-API freigeschaltet ist. Bis dahin Platzhalter.",
          "Live reviews will appear once the public reviews API is enabled. Placeholders for now."
        );
      }
    } finally {
      grid.classList.remove("is-loading");
    }
  }

  function initCookieBanner() {
    const banner = document.getElementById("cookieBanner");
    if (!banner || localStorage.getItem("cookiesAccepted")) return;

    setTimeout(() => banner.classList.add("visible"), 800);

    document.getElementById("cookieAccept")?.addEventListener("click", () => {
      localStorage.setItem("cookiesAccepted", "true");
      banner.classList.remove("visible");
    });

    document.getElementById("cookieDecline")?.addEventListener("click", () => {
      localStorage.setItem("cookiesAccepted", "declined");
      banner.classList.remove("visible");
    });
  }

  function initWhatsApp() {
    const btn = document.getElementById("whatsappBtn");
    if (!btn) return;
    setWhatsAppLink(
      btn,
      t(
        `Hallo, ich interessiere mich für ${platformName()}. Können wir eine Demo vereinbaren?`,
        `Hello, I am interested in ${platformName()}. Can we schedule a demo?`,
        `مرحبا، أهتم بـ ${platformName()}. هل يمكننا حجز عرض تجريبي؟`
      )
    );
    btn.setAttribute("aria-label", t("Demo per WhatsApp anfragen", "Request demo via WhatsApp", "اطلب عرضاً عبر واتساب"));
    btn.setAttribute("data-tooltip", t("Demo per WhatsApp", "Demo via WhatsApp", "عرض عبر واتساب"));
  }

  function initStickyMobileCta() {
    const bar = document.getElementById("mobileCtaBar");
    const waBtn = document.getElementById("mobileCtaWhatsapp");
    if (!bar) return;

    document.body.classList.add("has-mobile-cta");

    if (waBtn) {
      setWhatsAppLink(
        waBtn,
        t(
          `Hallo, ich möchte eine Demo für ${platformName()} buchen.`,
          `Hello, I would like to book a ${platformName()} demo.`,
          `مرحبا، أريد حجز عرض لـ ${platformName()}.`
        )
      );
    }

    const contact = document.getElementById("kontakt") || document.getElementById("contact");
    let visible = false;

    function updateBar() {
      if (window.innerWidth > 768) {
        bar.classList.remove("visible");
        bar.setAttribute("aria-hidden", "true");
        return;
      }
      const scrollY = window.scrollY;
      const contactTop = contact ? contact.offsetTop : Infinity;
      const show = scrollY > 400 && scrollY < contactTop - window.innerHeight * 0.5;
      if (show !== visible) {
        visible = show;
        bar.classList.toggle("visible", show);
        bar.setAttribute("aria-hidden", show ? "false" : "true");
      }
    }

    window.addEventListener("scroll", updateBar, { passive: true });
    window.addEventListener("resize", updateBar);
    updateBar();
  }

  function initScrollReveal() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const els = document.querySelectorAll(".reveal");
    if (!els.length) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -30px 0px" }
    );
    els.forEach((el) => observer.observe(el));
  }

  function initFooterYear() {
    const year = String(new Date().getFullYear());
    document.querySelectorAll("[data-year]").forEach((el) => {
      el.textContent = year;
    });
  }
});
