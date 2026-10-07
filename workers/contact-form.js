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

function emailShell({ logo, company, platform, website, titleBadge, bodyHtml, footerNote, dir }) {
  const rtl = dir === "rtl";
  return `<!DOCTYPE html>
<html lang="${rtl ? "ar" : "de"}" dir="${rtl ? "rtl" : "ltr"}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#e8eef6;font-family:Arial,Helvetica,sans-serif;-webkit-font-smoothing:antialiased">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#e8eef6;padding:32px 14px">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:18px;overflow:hidden;border:1px solid #d7e0ec;box-shadow:0 8px 28px rgba(15,23,42,0.08)">
<tr>
  <td style="background:linear-gradient(135deg,#0b1220 0%,#152238 55%,#1a2f4a 100%);padding:28px 28px 24px;text-align:center">
    <img src="${escapeHtml(logo)}" alt="SUPPIX AI" width="172" style="max-width:172px;height:auto;border:0;display:block;margin:0 auto 12px"/>
    <p style="margin:0;color:#94a3b8;font-size:13px;letter-spacing:0.04em">${escapeHtml(platform)} · ${escapeHtml(company)}</p>
  </td>
</tr>
<tr><td style="height:4px;background:linear-gradient(90deg,#5eb8e8,#7b8cff,#5eb8e8);font-size:0;line-height:0">&nbsp;</td></tr>
<tr>
  <td style="padding:28px 28px 8px">
    <p style="margin:0 0 18px;display:inline-block;background:#e8f6fc;color:#1d6f95;font-size:12px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:6px 12px;border-radius:999px">${titleBadge}</p>
    ${bodyHtml}
  </td>
</tr>
<tr>
  <td style="padding:8px 28px 28px">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fb;border:1px solid #e2e8f0;border-radius:12px">
      <tr><td style="padding:14px 16px;font-size:12px;line-height:1.55;color:#64748b;text-align:center">
        ${footerNote || ""}
        <a href="${escapeHtml(website)}" style="color:#3a9fd4;text-decoration:none;font-weight:700">${escapeHtml(website.replace(/^https?:\/\//, ""))}</a>
      </td></tr>
    </table>
  </td>
</tr>
</table>
</td></tr>
</table>
</body></html>`;
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
    ? `Mit freundlichen Grüßen<br><strong>Ihr Team von ${escapeHtml(company)}</strong>`
    : ar
      ? `مع أطيب التحيات<br><strong>فريق ${escapeHtml(company)}</strong>`
      : `Kind regards<br><strong>Your team at ${escapeHtml(company)}</strong>`;
  const replyHint = de
    ? "Sie können auf diese E-Mail antworten – die Nachricht geht an unser Team."
    : ar
      ? "يمكنك الرد على هذا البريد – ستصل الرسالة إلى فريقنا."
      : "You can reply to this email – it goes straight to our team.";
  const wa = String(whatsapp || "").replace(/\D/g, "");

  const bodyHtml = `
<p style="margin:0 0 10px;font-size:22px;font-weight:700;color:#0f172a;line-height:1.3">${greeting}</p>
<p style="margin:0 0 20px;font-size:15px;line-height:1.65;color:#475569">${thanks}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;margin:0 0 22px">
  <tr><td style="padding:16px 18px">
    <p style="margin:0 0 6px;font-weight:700;font-size:14px;color:#0f172a">${nextTitle}</p>
    <p style="margin:0;font-size:14px;color:#64748b;line-height:1.6">${nextBody}</p>
  </td></tr>
</table>
<p style="margin:0 0 8px;font-weight:700;font-size:13px;color:#0f172a;text-transform:uppercase;letter-spacing:0.04em">${de ? "Kontakt" : ar ? "تواصل" : "Contact"}</p>
<p style="margin:0 0 20px;font-size:14px;line-height:1.75;color:#475569">
${escapeHtml(company)}<br>
<a href="mailto:${escapeHtml(email)}" style="color:#3a9fd4;text-decoration:none">${escapeHtml(email)}</a><br>
<a href="tel:+${wa}" style="color:#3a9fd4;text-decoration:none">${escapeHtml(phone)}</a>
 · <a href="https://wa.me/${wa}" style="color:#3a9fd4;text-decoration:none">WhatsApp</a>
</p>
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 18px"><tr>
  <td style="border-radius:12px;background:linear-gradient(135deg,#5eb8e8,#3a9fd4)">
    <a href="${escapeHtml(website)}" style="display:inline-block;padding:13px 24px;color:#ffffff;font-weight:700;font-size:14px;text-decoration:none">${cta}</a>
  </td>
</tr></table>
<p style="margin:0 0 8px;font-size:14px;line-height:1.6;color:#334155">${closing}</p>
<p style="margin:0;font-size:12px;color:#94a3b8">${replyHint}</p>`;

  return emailShell({
    logo,
    company,
    platform,
    website,
    titleBadge: title,
    bodyHtml,
    footerNote: `${escapeHtml(company)} · `,
    dir: ar ? "rtl" : "ltr",
  });
}

function ownerEmailHtml({ fields, logo, company, platform, website, replyEmail }) {
  const rows = Object.entries(fields)
    .filter(([, v]) => v != null && String(v).trim() !== "")
    .map(([k, v]) => {
      const isMsg = String(k).toLowerCase().includes("nachricht") || String(k).toLowerCase() === "message";
      const valueStyle = isMsg
        ? "padding:12px 14px;color:#334155;font-size:14px;line-height:1.6;white-space:pre-wrap;word-break:break-word"
        : "padding:12px 14px;color:#0f172a;font-size:14px;font-weight:600;word-break:break-word";
      return `<tr>
        <td style="padding:12px 14px;width:34%;vertical-align:top;background:#f8fafc;border-bottom:1px solid #e8eef6;font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.03em">${escapeHtml(k)}</td>
        <td style="${valueStyle};border-bottom:1px solid #e8eef6">${escapeHtml(v)}</td>
      </tr>`;
    })
    .join("");

  const mail = escapeHtml(replyEmail || "");
  const bodyHtml = `
<p style="margin:0 0 6px;font-size:22px;font-weight:700;color:#0f172a">Neue Demo-Anfrage</p>
<p style="margin:0 0 20px;font-size:14px;line-height:1.55;color:#64748b">Über das Kontaktformular auf ${escapeHtml((website || "").replace(/^https?:\/\//, ""))}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:14px;overflow:hidden;margin:0 0 22px">
  ${rows}
</table>
${
  mail
    ? `<table role="presentation" cellpadding="0" cellspacing="0"><tr>
  <td style="border-radius:12px;background:linear-gradient(135deg,#5eb8e8,#3a9fd4)">
    <a href="mailto:${mail}" style="display:inline-block;padding:13px 24px;color:#ffffff;font-weight:700;font-size:14px;text-decoration:none">Kunde antworten</a>
  </td>
</tr></table>
<p style="margin:12px 0 0;font-size:12px;color:#94a3b8">Antwort geht direkt an ${mail}</p>`
    : ""
}`;

  return emailShell({
    logo,
    company,
    platform,
    website,
    titleBadge: "Lead · WorkPass",
    bodyHtml,
    footerNote: "Interne Benachrichtigung · ",
    dir: "ltr",
  });
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
    const brandCompany = env.BRAND_COMPANY || "Suppix AI UG";
    const platform = env.PLATFORM || "WorkPass";
    const phone = env.PHONE || "017631676589";
    const whatsapp = env.WHATSAPP || "4917631676589";
    const website = env.WEBSITE || "https://suppixai.com";
    const logo = env.LOGO_URL || "https://suppixai.com/assets/logo.png";

    try {
      if (formType === "newsletter") {
        await sendResend(env, {
          from: fromEmail,
          to: [toEmail],
          reply_to: email,
          subject: `Newsletter-Anmeldung – ${email}`,
          html: ownerEmailHtml({
            fields: { Typ: "Newsletter", EMail: email, Sprache: lang },
            logo,
            company: brandCompany,
            platform,
            website,
            replyEmail: email,
          }),
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
          html: customerEmailHtml({
            name: "",
            lang,
            company: brandCompany,
            platform,
            email: toEmail,
            phone,
            whatsapp,
            website,
            logo,
          }),
        });
      } else {
        await sendResend(env, {
          from: fromEmail,
          to: [toEmail],
          reply_to: email,
          subject: `Demo-Anfrage – ${name || "Kunde"}`,
          html: ownerEmailHtml({
            fields: {
              Name: name,
              EMail: email,
              Unternehmen: company,
              Paket: paket,
              Nachricht: message,
              Sprache: lang,
            },
            logo,
            company: brandCompany,
            platform,
            website,
            replyEmail: email,
          }),
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
          html: customerEmailHtml({
            name,
            lang,
            company: brandCompany,
            platform,
            email: toEmail,
            phone,
            whatsapp,
            website,
            logo,
          }),
        });
      }

      return json({ ok: true }, 200, cors);
    } catch (err) {
      return json({ ok: false, error: String(err.message || err) }, 502, cors);
    }
  },
};
