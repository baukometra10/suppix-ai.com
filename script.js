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
    return cfg.platform || "SUPPIX";
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
        .replace(/Baupass Controll|Baukometra|SUPPIX|Suppix AI|Suppix Technologie UG/g, (m) => {
          if (m === "Baupass Controll" || m === "SUPPIX") return cfg.platform;
          if (m === "Baukometra" || m === "Suppix AI" || m === "Suppix Technologie UG") return cfg.brand || cfg.company;
          return m;
        });
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

  function initContactForm() {
    const form = document.getElementById("contactForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const statusEl = document.getElementById("contactStatus");
      const name = document.getElementById("name").value.trim();
      const companyEl = document.getElementById("company");
      const company = companyEl ? companyEl.value.trim() : "";
      const email = document.getElementById("email").value.trim();
      const paket = document.getElementById("paket");
      const paketText = paket ? paket.options[paket.selectedIndex].text : "–";
      const message = document.getElementById("message").value.trim();

      btn.disabled = true;
      btn.textContent = t("Wird gesendet…", "Sending…", "جاري الإرسال…");

      const ok = await submitToFormSubmit(
        {
          _subject: t(`Demo-Anfrage – ${name}`, `Demo request – ${name}`, `طلب عرض – ${name}`),
          name,
          company: company || "–",
          email,
          paket: paket ? paketText : "–",
          message: message || "–",
        },
        statusEl
      );

      if (ok) {
        if (statusEl) {
          statusEl.className = "form-status success";
          statusEl.textContent = t(
            "Vielen Dank! Ihre Anfrage wurde gesendet. Wir melden uns in Kürze.",
            "Thank you! Your request was sent. We will get back to you shortly.",
            "شكراً! تم إرسال طلبك. سنتواصل معك قريباً."
          );
        } else {
          alert(t("Vielen Dank! Ihre Anfrage wurde gesendet.", "Thank you! Your request was sent.", "شكراً! تم إرسال طلبك."));
        }
        form.reset();
      } else {
        const subject = encodeURIComponent(
          t(`Demo-Anfrage ${platformName()} – ${name}`, `${platformName()} demo request – ${name}`, `طلب عرض ${platformName()} – ${name}`)
        );
        const body = encodeURIComponent(
          `Name: ${name}\n${t("Unternehmen", "Company", "الشركة")}: ${company || "–"}\nE-Mail: ${email}\n${t("Paket", "Plan", "الباقة")}: ${paket ? paketText : "–"}\n\n${t("Nachricht", "Message", "الرسالة")}:\n${message || "–"}`
        );
        window.location.href = `mailto:${cfg.email || "baupass-control@outlook.de"}?subject=${subject}&body=${body}`;
        if (statusEl) {
          statusEl.className = "form-status";
          statusEl.textContent = t(
            "E-Mail-Programm geöffnet – bitte Nachricht absenden.",
            "Email client opened – please send the message.",
            "تم فتح برنامج البريد – يرجى إرسال الرسالة."
          );
        }
      }

      btn.disabled = false;
      btn.textContent = t("Nachricht senden", "Send message", "إرسال الرسالة");
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
