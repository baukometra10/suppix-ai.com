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
    ? `vielen Dank für Ihre Nachricht zu <strong>${escapeHtml(platform)}</strong>. Wir haben Ihre Anfrage erhalten und melden uns so schnell wie möglich.`
    : ar
      ? `شكراً لرسالتك حول <strong>${escapeHtml(platform)}</strong>. استلمنا طلبك وسنتواصل معك قريباً.`
      : `thank you for your message about <strong>${escapeHtml(platform)}</strong>. We received your request and will get back to you soon.`;
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
  const wa = String(whatsapp || "").replace(/\D/g, "");

  return `<!DOCTYPE html><html><body style="margin:0;background:#eef2f7;font-family:Arial,Helvetica,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="padding:24px 12px"><tr><td align="center">
<table role="presentation" width="560" style="max-width:560px;background:#fff;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0">
<tr><td style="background:#0b1220;padding:28px;text-align:center">
<img src="${escapeHtml(logo)}" alt="${escapeHtml(company)}" width="168" style="max-width:168px;height:auto;border:0"/>
<p style="margin:14px 0 0;color:#94a3b8;font-size:13px">${escapeHtml(platform)} · ${escapeHtml(company)}</p>
</td></tr>
<tr><td style="padding:28px;color:#0f172a">
<p style="margin:0 0 6px;font-size:13px;font-weight:700;color:#2563eb;text-transform:uppercase">${title}</p>
<p style="margin:0 0 14px;font-size:20px;font-weight:700">${greeting}</p>
<p style="margin:0 0 18px;font-size:15px;line-height:1.6;color:#334155">${thanks}</p>
<table width="100%" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;margin:0 0 18px"><tr><td style="padding:14px 16px">
<p style="margin:0 0 6px;font-weight:700;font-size:14px">${nextTitle}</p>
<p style="margin:0;font-size:14px;color:#475569;line-height:1.55">${nextBody}</p>
</td></tr></table>
<p style="margin:0 0 8px;font-weight:700;font-size:14px">${de ? "Direkt kontaktieren" : ar ? "تواصل معنا" : "Contact us"}</p>
<p style="margin:0 0 18px;font-size:14px;line-height:1.7;color:#334155">
${escapeHtml(company)}<br>
<a href="mailto:${escapeHtml(email)}" style="color:#2563eb;text-decoration:none">${escapeHtml(email)}</a><br>
<a href="tel:+${wa}" style="color:#2563eb;text-decoration:none">${escapeHtml(phone)}</a><br>
<a href="https://wa.me/${wa}" style="color:#2563eb;text-decoration:none">WhatsApp</a>
</p>
<a href="${escapeHtml(website)}" style="display:inline-block;background:#2563eb;color:#fff;padding:12px 22px;border-radius:10px;font-weight:700;text-decoration:none;font-size:14px">${cta}</a>
<p style="margin:18px 0 0;font-size:14px;color:#334155">${closing}</p>
</td></tr>
</table>
</td></tr></table>
</body></html>`;
}

function ownerEmailHtml(fields) {
  const rows = Object.entries(fields)
    .filter(([, v]) => v != null && String(v).trim() !== "")
    .map(
      ([k, v]) =>
        `<tr><td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;font-weight:700;color:#0f172a;vertical-align:top">${escapeHtml(k)}</td><td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;color:#334155">${escapeHtml(v)}</td></tr>`
    )
    .join("");
  return `<!DOCTYPE html><html><body style="font-family:Arial,Helvetica,sans-serif;background:#f8fafc;padding:20px">
<table width="100%" style="max-width:640px;margin:0 auto;background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
<tr><td style="background:#0b1220;color:#fff;padding:16px 20px;font-size:16px;font-weight:700">Neue Anfrage – WorkPass</td></tr>
<tr><td style="padding:8px 0"><table width="100%" cellpadding="0" cellspacing="0">${rows}</table></td></tr>
</table></body></html>`;
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
          html: ownerEmailHtml({ Typ: "Newsletter", EMail: email, Sprache: lang }),
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
            Name: name,
            EMail: email,
            Unternehmen: company,
            Paket: paket,
            Nachricht: message,
            Sprache: lang,
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
