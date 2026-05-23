document.addEventListener("DOMContentLoaded", () => {
  const cfg = window.SITE_CONFIG || {};

  applySiteConfig();
  initHeader();
  initSmoothScroll();
  initContactForm();
  initNewsletterForm();
  initFaq();
  initPriceCalculator();
  initCookieBanner();
  initWhatsApp();
  initContactWhatsApp();
  initStickyMobileCta();
  initScrollReveal();
  initFooterYear();

  function isEnglish() {
    return document.documentElement.lang === "en";
  }

  function t(de, en) {
    return isEnglish() ? en : de;
  }

  function initContactWhatsApp() {
    const link = document.getElementById("contactWhatsApp");
    if (!link || !cfg.whatsapp) return;
    const text = encodeURIComponent(t("Hallo, ich interessiere mich für Baupass Controll.", "Hello, I am interested in Baupass Controll."));
    link.href = `https://wa.me/${cfg.whatsapp}?text=${text}`;
    link.target = "_blank";
    link.rel = "noopener";
  }

  function applySiteConfig() {
    if (!cfg.email && !cfg.phone) return;

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
      el.href = cfg.appLoginUrl || "index.html#vorschau";
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
      hamburgerBtn.addEventListener("click", () => {
        mobileNav.classList.toggle("open");
      });
      mobileNav.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => mobileNav.classList.remove("open"));
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
          _subject: data._subject || "Baupass Controll Anfrage",
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
      btn.textContent = t("Wird gesendet…", "Sending…");

      const ok = await submitToFormSubmit(
        {
          _subject: t(`Demo-Anfrage – ${name}`, `Demo request – ${name}`),
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
            "Thank you! Your request was sent. We will get back to you shortly."
          );
        } else {
          alert(t("Vielen Dank! Ihre Anfrage wurde gesendet.", "Thank you! Your request was sent."));
        }
        form.reset();
      } else {
        const subject = encodeURIComponent(
          t(`Demo-Anfrage Baupass Controll – ${name}`, `Baupass Controll demo request – ${name}`)
        );
        const body = encodeURIComponent(
          `Name: ${name}\n${t("Unternehmen", "Company")}: ${company || "–"}\nE-Mail: ${email}\n${t("Paket", "Plan")}: ${paket ? paketText : "–"}\n\n${t("Nachricht", "Message")}:\n${message || "–"}`
        );
        window.location.href = `mailto:${cfg.email || "baupass-control@outlook.de"}?subject=${subject}&body=${body}`;
        if (statusEl) {
          statusEl.className = "form-status";
          statusEl.textContent = t(
            "E-Mail-Programm geöffnet – bitte Nachricht absenden.",
            "Email client opened – please send the message."
          );
        }
      }

      btn.disabled = false;
      btn.textContent = t("Nachricht senden", "Send message");
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
          "Erfolgreich angemeldet! Willkommen bei Baupass Controll.",
          "Successfully subscribed! Welcome to Baupass Controll."
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
      besucherkarte: { base: 19, perEmployee: 0, threshold: Infinity, label: t("Besucherkarte", "Visitor Card") },
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
        : `${total.toLocaleString("de-DE", { minimumFractionDigits: 0, maximumFractionDigits: 2 })} €`;
      resultNote.textContent =
        plan.perEmployee > 0 && count > plan.threshold
          ? t(
              `${plan.label}: ${plan.base} € + ${count - plan.threshold} × ${plan.perEmployee} €`,
              `${plan.label}: €${plan.base} + ${count - plan.threshold} × €${plan.perEmployee}`
            )
          : t(`${plan.label}: Alle Mitarbeiter inklusive`, `${plan.label}: All employees included`);
    }

    paketSelect.addEventListener("change", calculate);
    range.addEventListener("input", calculate);
    calculate();
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
    if (!btn || !cfg.whatsapp) return;
    const text = encodeURIComponent(
      t(
        "Hallo, ich interessiere mich für Baupass Controll. Können wir eine Demo vereinbaren?",
        "Hello, I am interested in Baupass Controll. Can we schedule a demo?"
      )
    );
    btn.href = `https://wa.me/${cfg.whatsapp}?text=${text}`;
    btn.setAttribute("aria-label", t("Demo per WhatsApp anfragen", "Request demo via WhatsApp"));
    btn.setAttribute("data-tooltip", t("Demo per WhatsApp", "Demo via WhatsApp"));
  }

  function initStickyMobileCta() {
    const bar = document.getElementById("mobileCtaBar");
    const waBtn = document.getElementById("mobileCtaWhatsapp");
    if (!bar) return;

    document.body.classList.add("has-mobile-cta");

    if (waBtn && cfg.whatsapp) {
      const text = encodeURIComponent(
        t(
          "Hallo, ich möchte eine Demo für Baupass Controll buchen.",
          "Hello, I would like to book a Baupass Controll demo."
        )
      );
      waBtn.href = `https://wa.me/${cfg.whatsapp}?text=${text}`;
      waBtn.target = "_blank";
      waBtn.rel = "noopener";
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
