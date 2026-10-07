/**
 * Cloudflare Worker: Kontaktformular → Resend (von @suppixai.com)
 *
 * Deploy:
 *   1. npm i -g wrangler  (oder npx wrangler)
 *   2. cd workers && npx wrangler login
 *   3. npx wrangler secret put RESEND_API_KEY
 *   4. npx wrangler deploy
 *
 * Secrets / vars (wrangler.toml + Dashboard):
 *   RESEND_API_KEY   – aus Resend Dashboard
 *   TO_EMAIL         – info@suppixai.com
 *   FROM_EMAIL       – WorkPass <info@suppixai.com>  (Domain in Resend verifiziert)
 *   ALLOWED_ORIGINS  – https://suppixai.com,https://www.suppixai.com
 */

const DEFAULT_ALLOWED = [
  "https://suppixai.com",
  "https://www.suppixai.com",
  "http://localhost:5500",
  "http://127.0.0.1:5500",
];

function corsHeaders(origin, allowed) {
  const ok = !origin || allowed.includes(origin);
  return {
    "Access-Control-Allow-Origin": ok ? origin || allowed[0] : allowed[0],
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

function parseAllowed(env) {
  const raw = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  return raw.length ? raw : DEFAULT_ALLOWED;
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Helles, Dark-Mode-sicheres Shell (keine Gradients – die brechen in Mail-Apps). */
/**
 * logoSrc: externe URL oder "cid:logo" (mit Resend-Attachment).
 * useImage: false = nur Text-Branding (besser für Owner-Mails / Spam / Dark Mode).
 */
function emailShell({ logoSrc, company, platform, website, titleBadge, bodyHtml, footerNote, dir, useImage }) {
  const rtl = dir === "rtl";
  const host = escapeHtml((website || "").replace(/^https?:\/\//, ""));
  const brandBlock = useImage
    ? `<img src="${escapeHtml(logoSrc)}" alt="SUPPIX AI" width="148" style="display:block;margin:0 auto 10px;border:0;max-width:148px;height:auto"/>
<p style="margin:0;font-size:20px;font-weight:700;color:#0b1220;letter-spacing:0.02em">SUPPIX AI</p>
<p style="margin:6px 0 0;font-size:13px;color:#64748b">${escapeHtml(platform)} · ${escapeHtml(company)}</p>`
    : `<p style="margin:0;font-size:22px;font-weight:700;color:#0b1220;letter-spacing:0.04em">SUPPIX AI</p>
<p style="margin:6px 0 0;font-size:13px;color:#64748b">${escapeHtml(platform)} · ${escapeHtml(company)}</p>`;

  return `<!DOCTYPE html>
<html lang="${rtl ? "ar" : "de"}" dir="${rtl ? "rtl" : "ltr"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
</head>
<body bgcolor="#f4f7fb" style="margin:0;padding:0;background-color:#f4f7fb;font-family:Arial,Helvetica,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f4f7fb">
<tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="560" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width:560px;width:100%;background-color:#ffffff;border:1px solid #dbe3ee">
<tr>
  <td bgcolor="#ffffff" style="background-color:#ffffff;padding:22px 24px;text-align:center;border-bottom:3px solid #5eb8e8">
    ${brandBlock}
  </td>
</tr>
<tr>
  <td bgcolor="#ffffff" style="background-color:#ffffff;padding:22px 24px">
    <p style="margin:0 0 14px;font-size:12px;font-weight:700;color:#1a6f93;text-transform:uppercase;letter-spacing:0.04em">${titleBadge}</p>
    ${bodyHtml}
  </td>
</tr>
<tr>
  <td bgcolor="#f8fafc" style="background-color:#f8fafc;padding:14px 24px;border-top:1px solid #e2e8f0;font-size:12px;line-height:1.5;color:#64748b;text-align:center">
    ${footerNote || ""}<a href="${escapeHtml(website)}" style="color:#2b8fc0;text-decoration:none;font-weight:700">${host}</a>
  </td>
</tr>
</table>
</td></tr>
</table>
</body></html>`;
}

function ctaButton(href, label) {
  return `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 10px">
<tr>
  <td bgcolor="#3a9fd4" style="background-color:#3a9fd4;border-radius:10px">
    <a href="${escapeHtml(href)}" style="display:inline-block;padding:13px 22px;font-size:14px;font-weight:700;color:#ffffff;text-decoration:none">${label}</a>
  </td>
</tr>
</table>`;
}

function customerEmailHtml({ name, lang, company, platform, email, phone, whatsapp, website, logo }) {
  const de = !lang || lang.startsWith("de");
  const ar = lang && lang.startsWith("ar");
  const greeting = name
    ? de
      ? `Hallo ${escapeHtml(name)},`
      : ar
        ? `مرحباً ${escapeHtml(name)}،`
        : `Hello ${escapeHtml(name)},`
    : de
      ? "Hallo,"
      : ar
        ? "مرحباً،"
        : "Hello,";
  const title = de ? "Anfrage erhalten" : ar ? "تم استلام الطلب" : "Request received";
  const thanks = de
    ? `vielen Dank für Ihre Nachricht zu <strong style="color:#0f172a">${escapeHtml(platform)}</strong>. Wir haben Ihre Anfrage erhalten und melden uns so schnell wie möglich.`
    : ar
      ? `شكراً لرسالتك حول <strong style="color:#0f172a">${escapeHtml(platform)}</strong>. استلمنا طلبك وسنتواصل معك قريباً.`
      : `thank you for your message about <strong style="color:#0f172a">${escapeHtml(platform)}</strong>. We received your request and will get back to you soon.`;
  const nextTitle = de ? "Was als Nächstes passiert" : ar ? "ما التالي" : "What happens next";
  const nextBody = de
    ? "Unser Team prüft Ihre Anfrage und meldet sich mit einer Demo oder den nächsten Schritten."
    : ar
      ? "سيراجع فريقنا طلبك ويتواصل معك."
      : "Our team will review your request and follow up with a demo or next steps.";
  const cta = de ? "Website öffnen" : ar ? "فتح الموقع" : "Open website";
  const closing = de
    ? `Mit freundlichen Grüßen<br><strong style="color:#0f172a">Ihr Team von ${escapeHtml(company)}</strong>`
    : ar
      ? `مع أطيب التحيات<br><strong style="color:#0f172a">فريق ${escapeHtml(company)}</strong>`
      : `Kind regards<br><strong style="color:#0f172a">Your team at ${escapeHtml(company)}</strong>`;
  const replyHint = de
    ? "Sie können auf diese E-Mail antworten – die Nachricht geht an unser Team."
    : ar
      ? "يمكنك الرد على هذا البريد – ستصل الرسالة إلى فريقنا."
      : "You can reply to this email – it goes straight to our team.";
  const wa = String(whatsapp || "").replace(/\D/g, "");

  const bodyHtml = `
<p class="em-value" style="margin:0 0 10px;font-size:22px;font-weight:700;color:#0f172a;line-height:1.3">${greeting}</p>
<p class="em-muted" style="margin:0 0 18px;font-size:15px;line-height:1.65;color:#475569">${thanks}</p>
<table role="presentation" class="em-field" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8fafc" style="background-color:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;margin:0 0 20px">
  <tr><td style="padding:14px 16px">
    <p class="em-value" style="margin:0 0 6px;font-weight:700;font-size:14px;color:#0f172a">${nextTitle}</p>
    <p class="em-muted" style="margin:0;font-size:14px;color:#64748b;line-height:1.6">${nextBody}</p>
  </td></tr>
</table>
<p class="em-value" style="margin:0 0 6px;font-weight:700;font-size:12px;color:#0f172a;text-transform:uppercase;letter-spacing:0.04em">${de ? "Kontakt" : ar ? "تواصل" : "Contact"}</p>
<p class="em-muted" style="margin:0 0 18px;font-size:14px;line-height:1.75;color:#475569">
${escapeHtml(company)}<br>
<a href="mailto:${escapeHtml(email)}" style="color:#2b8fc0;text-decoration:none">${escapeHtml(email)}</a><br>
<a href="tel:+${wa}" style="color:#2b8fc0;text-decoration:none">${escapeHtml(phone)}</a>
 · <a href="https://wa.me/${wa}" style="color:#2b8fc0;text-decoration:none">WhatsApp</a>
</p>
${ctaButton(website, cta)}
<p class="em-muted" style="margin:12px 0 6px;font-size:14px;line-height:1.6;color:#334155">${closing}</p>
<p class="em-muted" style="margin:0;font-size:12px;color:#94a3b8">${replyHint}</p>`;

  return {
    html: emailShell({
      logoSrc: "cid:suppix-logo",
      company,
      platform,
      website,
      titleBadge: title,
      bodyHtml,
      footerNote: `${escapeHtml(company)} · `,
      dir: ar ? "rtl" : "ltr",
      useImage: true,
    }),
    text: [
      title,
      "",
      greeting.replace(/<[^>]+>/g, ""),
      thanks.replace(/<[^>]+>/g, ""),
      "",
      nextTitle,
      nextBody,
      "",
      `${company} · ${email} · ${phone}`,
      website,
    ].join("\n"),
  };
}

/** Owner-Mail ohne Bilder – externe Logos + Forwarding landen sonst oft in Spam. */
function ownerEmailHtml({ fields, company, platform, website, replyEmail }) {
  const host = (website || "").replace(/^https?:\/\//, "");
  const rows = Object.entries(fields)
    .filter(([, v]) => v != null && String(v).trim() !== "")
    .map(([k, v]) => {
      return `<tr>
  <td style="padding:10px 0;border-bottom:1px solid #e8eef5;font-size:12px;color:#64748b;width:120px;vertical-align:top">${escapeHtml(k)}</td>
  <td style="padding:10px 0;border-bottom:1px solid #e8eef5;font-size:15px;color:#0f172a;font-weight:600;vertical-align:top;word-break:break-word">${escapeHtml(v)}</td>
</tr>`;
    })
    .join("");

  const mail = replyEmail || "";
  const bodyHtml = `
<p style="margin:0 0 6px;font-size:20px;font-weight:700;color:#0f172a">Neue Demo-Anfrage</p>
<p style="margin:0 0 16px;font-size:14px;color:#64748b">Kontaktformular auf ${escapeHtml(host)}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 18px">${rows}</table>
${
  mail
    ? `${ctaButton(`mailto:${mail}?subject=${encodeURIComponent("Re: WorkPass Anfrage")}`, "Kunde antworten")}
<p style="margin:0;font-size:12px;color:#94a3b8">Antwort an ${escapeHtml(mail)}</p>`
    : ""
}`;

  const textLines = Object.entries(fields)
    .filter(([, v]) => v != null && String(v).trim() !== "")
    .map(([k, v]) => `${k}: ${v}`);

  return {
    html: emailShell({
      logoSrc: "",
      company,
      platform,
      website,
      titleBadge: "Neue Anfrage · WorkPass",
      bodyHtml,
      footerNote: "Interne Benachrichtigung · ",
      dir: "ltr",
      useImage: false,
    }),
    text: [
      "SUPPIX AI / WorkPass – Neue Demo-Anfrage",
      `Website: ${host}`,
      "",
      ...textLines,
      mail ? `\nKunde antworten: ${mail}` : "",
    ].join("\n"),
  };
}

function logoAttachment(logoUrl) {
  return {
    path: logoUrl,
    filename: "logo.png",
    content_id: "suppix-logo",
  };
}

async function sendResend(env, payload) {
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data?.message || data?.error || res.statusText || "Resend error";
    throw new Error(msg);
  }
  return data;
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
}

export default {
  async fetch(request, env) {
    const allowed = parseAllowed(env);
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, allowed);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    if (request.method !== "POST") {
      return json({ ok: false, error: "Method not allowed" }, 405, cors);
    }

    if (origin && !allowed.includes(origin)) {
      return json({ ok: false, error: "Origin not allowed" }, 403, cors);
    }

    if (!env.RESEND_API_KEY) {
      return json({ ok: false, error: "Server not configured" }, 500, cors);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ ok: false, error: "Invalid JSON" }, 400, cors);
    }

    // Honeypot
    if (body._gotcha || body._honey) {
      return json({ ok: true }, 200, cors);
    }

    const name = String(body.name || "").trim().slice(0, 120);
    const email = String(body.email || "").trim().slice(0, 200);
    const company = String(body.company || "").trim().slice(0, 160);
    const paket = String(body.paket || "").trim().slice(0, 80);
    const message = String(body.message || "").trim().slice(0, 4000);
    const privacy = String(body.privacy || "").trim();
    const lang = String(body.lang || "de").trim().slice(0, 8);
    const formType = String(body.formType || "contact").trim();

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ ok: false, error: "Valid email required" }, 400, cors);
    }
    if (formType !== "newsletter" && !name) {
      return json({ ok: false, error: "Name required" }, 400, cors);
    }
    if (formType !== "newsletter" && privacy !== "accepted") {
      return json({ ok: false, error: "Privacy consent required" }, 400, cors);
    }

    const toEmail = env.TO_EMAIL || "info@suppixai.com";
    const fromEmail = env.FROM_EMAIL || "WorkPass <info@suppixai.com>";
    // Owner-Mail bewusst NICHT von info@ → info@ (Porkbun-Forward/Gmail droppt das oft still).
    const notifyFrom =
      env.NOTIFY_FROM_EMAIL || "WorkPass Anfragen <anfragen@suppixai.com>";
    // OWNER_EMAIL = private Inbox (Gmail/iCloud) – umgeht Porkbun-Forward → weniger Spam.
    // Sonst TO_EMAIL (info@), oft weitergeleitet und dann Junk.
    const ownerRecipients = String(env.OWNER_EMAIL || env.TO_EMAIL || "info@suppixai.com")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const brandCompany = env.BRAND_COMPANY || "Suppix AI UG";
    const platform = env.PLATFORM || "WorkPass";
    const phone = env.PHONE || "017631676589";
    const whatsapp = env.WHATSAPP || "4917631676589";
    const website = env.WEBSITE || "https://suppixai.com";
    const logo = env.LOGO_URL || "https://suppixai.com/assets/logo.png";
    const logoAtt = [logoAttachment(logo)];

    try {
      if (formType === "newsletter") {
        const ownerMail = ownerEmailHtml({
          fields: { Typ: "Newsletter", EMail: email, Sprache: lang },
          company: brandCompany,
          platform,
          website,
          replyEmail: email,
        });
        await sendResend(env, {
          from: notifyFrom,
          to: ownerRecipients,
          reply_to: email,
          subject: `Newsletter-Anmeldung – ${email}`,
          html: ownerMail.html,
          text: ownerMail.text,
        });
        const customerMail = customerEmailHtml({
          name: "",
          lang,
          company: brandCompany,
          platform,
          email: toEmail,
          phone,
          whatsapp,
          website,
          logo,
        });
        await sendResend(env, {
          from: fromEmail,
          to: [email],
          reply_to: toEmail,
          subject: lang.startsWith("en")
            ? "Newsletter confirmed – WorkPass"
            : lang.startsWith("ar")
              ? "تم تأكيد الاشتراك – WorkPass"
              : "Newsletter bestätigt – WorkPass",
          html: customerMail.html,
          text: customerMail.text,
          attachments: logoAtt,
        });
      } else {
        const ownerMail = ownerEmailHtml({
          fields: {
            Name: name,
            EMail: email,
            Unternehmen: company,
            Paket: paket,
            Nachricht: message,
            Sprache: lang,
          },
          company: brandCompany,
          platform,
          website,
          replyEmail: email,
        });
        await sendResend(env, {
          from: notifyFrom,
          to: ownerRecipients,
          reply_to: email,
          subject: `Demo-Anfrage – ${name || "Kunde"}`,
          html: ownerMail.html,
          text: ownerMail.text,
        });
        const customerMail = customerEmailHtml({
          name,
          lang,
          company: brandCompany,
          platform,
          email: toEmail,
          phone,
          whatsapp,
          website,
          logo,
        });
        await sendResend(env, {
          from: fromEmail,
          to: [email],
          reply_to: toEmail,
          subject: lang.startsWith("en")
            ? "We received your WorkPass request"
            : lang.startsWith("ar")
              ? "استلمنا طلبك بخصوص WorkPass"
              : "Wir haben Ihre WorkPass-Anfrage erhalten",
          html: customerMail.html,
          text: customerMail.text,
          attachments: logoAtt,
        });
      }

      return json({ ok: true }, 200, cors);
    } catch (err) {
      return json({ ok: false, error: String(err.message || err) }, 502, cors);
    }
  },
};
