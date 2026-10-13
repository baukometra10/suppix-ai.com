/**
 * Demo booking helpers (slots + reserve) for contact-form Worker.
 * Timezone: Europe/Berlin. Hours / duration from env or defaults.
 */

const DEFAULT_TZ = "Europe/Berlin";
const DEFAULT_START_HOUR = 10;
const DEFAULT_END_HOUR = 17;
const DEFAULT_DURATION_MIN = 30;
const DEFAULT_LEAD_HOURS = 2;
const DEFAULT_HORIZON_DAYS = 28;

function bookingConfig(env) {
  return {
    tz: env.BOOKING_TZ || DEFAULT_TZ,
    startHour: Number(env.BOOKING_START_HOUR || DEFAULT_START_HOUR),
    endHour: Number(env.BOOKING_END_HOUR || DEFAULT_END_HOUR),
    durationMin: Number(env.BOOKING_DURATION_MIN || DEFAULT_DURATION_MIN),
    leadHours: Number(env.BOOKING_LEAD_HOURS || DEFAULT_LEAD_HOURS),
    horizonDays: Number(env.BOOKING_HORIZON_DAYS || DEFAULT_HORIZON_DAYS),
    weekdays: String(env.BOOKING_WEEKDAYS || "1,2,3,4,5")
      .split(",")
      .map((s) => Number(s.trim()))
      .filter((n) => n >= 0 && n <= 6),
  };
}

/** Parts of an instant in a given IANA timezone. */
function zonedParts(date, timeZone) {
  const fmt = new Intl.DateTimeFormat("en-GB", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
    weekday: "short",
  });
  const map = {};
  for (const p of fmt.formatToParts(date)) {
    if (p.type !== "literal") map[p.type] = p.value;
  }
  const weekdayMap = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
  return {
    year: Number(map.year),
    month: Number(map.month),
    day: Number(map.day),
    hour: Number(map.hour),
    minute: Number(map.minute),
    second: Number(map.second),
    weekday: weekdayMap[map.weekday] ?? 0,
  };
}

function pad(n) {
  return String(n).padStart(2, "0");
}

/** Approximate UTC Date for local wall time in tz (handles DST via offset probe). */
function zonedLocalToUtc(year, month, day, hour, minute, timeZone) {
  const guess = new Date(Date.UTC(year, month - 1, day, hour, minute, 0));
  const parts = zonedParts(guess, timeZone);
  const asUtc = Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, parts.second);
  const desired = Date.UTC(year, month - 1, day, hour, minute, 0);
  return new Date(guess.getTime() + (desired - asUtc));
}

function ymdInTz(date, timeZone) {
  const p = zonedParts(date, timeZone);
  return `${p.year}-${pad(p.month)}-${pad(p.day)}`;
}

function addDaysYmd(ymd, days) {
  const [y, m, d] = ymd.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d + days));
  return `${dt.getUTCFullYear()}-${pad(dt.getUTCMonth() + 1)}-${pad(dt.getUTCDate())}`;
}

function parseYmd(ymd) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(ymd)) return null;
  const [y, m, d] = ymd.split("-").map(Number);
  if (m < 1 || m > 12 || d < 1 || d > 31) return null;
  return { y, m, d };
}

function formatSlotLabel(iso, timeZone, lang) {
  const d = new Date(iso);
  const locale = lang?.startsWith("ar") ? "ar" : lang?.startsWith("en") ? "en-GB" : "de-DE";
  return new Intl.DateTimeFormat(locale, {
    timeZone,
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(d);
}

function generateDaySlots(ymd, cfg, now) {
  const parsed = parseYmd(ymd);
  if (!parsed) return [];
  const { y, m, d } = parsed;
  const probe = zonedLocalToUtc(y, m, d, 12, 0, cfg.tz);
  const weekday = zonedParts(probe, cfg.tz).weekday;
  if (!cfg.weekdays.includes(weekday)) return [];

  const earliest = now.getTime() + cfg.leadHours * 60 * 60 * 1000;
  const slots = [];
  for (let minutes = cfg.startHour * 60; minutes + cfg.durationMin <= cfg.endHour * 60; minutes += cfg.durationMin) {
    const h = Math.floor(minutes / 60);
    const min = minutes % 60;
    const start = zonedLocalToUtc(y, m, d, h, min, cfg.tz);
    if (start.getTime() < earliest) continue;
    const end = new Date(start.getTime() + cfg.durationMin * 60 * 1000);
    slots.push({
      start: start.toISOString(),
      end: end.toISOString(),
      label: `${pad(h)}:${pad(min)}`,
    });
  }
  return slots;
}

async function bookedStartsForDay(db, ymd, tz) {
  if (!db) return new Set();
  const [y, m, d] = ymd.split("-").map(Number);
  const rangeStart = zonedLocalToUtc(y, m, d, 0, 0, tz).toISOString();
  const rangeEnd = zonedLocalToUtc(y, m, d, 23, 59, tz).toISOString();
  const rows = await db
    .prepare(
      `SELECT slot_start FROM demo_bookings
       WHERE status = 'confirmed' AND slot_start >= ? AND slot_start <= ?`
    )
    .bind(rangeStart, rangeEnd)
    .all();
  return new Set((rows?.results || []).map((r) => r.slot_start));
}

export async function handleSlotsGet(request, env, cors) {
  const cfg = bookingConfig(env);
  const url = new URL(request.url);
  const dateParam = String(url.searchParams.get("date") || "").trim();
  const lang = String(url.searchParams.get("lang") || "de").trim().slice(0, 8);
  const now = new Date();
  const todayYmd = ymdInTz(now, cfg.tz);
  const maxYmd = addDaysYmd(todayYmd, cfg.horizonDays);

  if (!dateParam) {
    return json(
      {
        ok: true,
        timezone: cfg.tz,
        durationMin: cfg.durationMin,
        today: todayYmd,
        maxDate: maxYmd,
        weekdays: cfg.weekdays,
        startHour: cfg.startHour,
        endHour: cfg.endHour,
      },
      200,
      cors
    );
  }

  if (!parseYmd(dateParam) || dateParam < todayYmd || dateParam > maxYmd) {
    return json({ ok: false, error: "Invalid date" }, 400, cors);
  }

  const booked = await bookedStartsForDay(env.DB, dateParam, cfg.tz);
  const slots = generateDaySlots(dateParam, cfg, now)
    .filter((s) => !booked.has(s.start))
    .map((s) => ({
      ...s,
      display: formatSlotLabel(s.start, cfg.tz, lang),
    }));

  return json(
    {
      ok: true,
      date: dateParam,
      timezone: cfg.tz,
      durationMin: cfg.durationMin,
      slots,
    },
    200,
    cors
  );
}

function newId() {
  return crypto.randomUUID();
}

function buildIcs({ uid, startIso, endIso, summary, description, organizerEmail }) {
  const stamp = (iso) =>
    iso.replace(/[-:]/g, "").replace(/\.\d{3}/, "").replace(/Z$/, "Z");
  const escapeIcs = (s) =>
    String(s || "")
      .replace(/\\/g, "\\\\")
      .replace(/;/g, "\\;")
      .replace(/,/g, "\\,")
      .replace(/\n/g, "\\n");
  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Suppix AI//WorkPass Demo//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:REQUEST",
    "BEGIN:VEVENT",
    `UID:${uid}`,
    `DTSTAMP:${stamp(new Date().toISOString())}`,
    `DTSTART:${stamp(startIso)}`,
    `DTEND:${stamp(endIso)}`,
    `SUMMARY:${escapeIcs(summary)}`,
    `DESCRIPTION:${escapeIcs(description)}`,
    `ORGANIZER:mailto:${organizerEmail}`,
    "STATUS:CONFIRMED",
    "END:VEVENT",
    "END:VCALENDAR",
  ];
  return lines.join("\r\n");
}

function toBase64(str) {
  return btoa(unescape(encodeURIComponent(str)));
}

export async function handleBookingPost(body, env, cors, helpers) {
  const { escapeHtml, emailShell, ownerEmailHtml, sendResend, logoAttachment, ctaButton } = helpers;
  const cfg = bookingConfig(env);

  if (body._gotcha || body._honey) {
    return json({ ok: true }, 200, cors);
  }

  const name = String(body.name || "").trim().slice(0, 120);
  const email = String(body.email || "").trim().slice(0, 200);
  const company = String(body.company || "").trim().slice(0, 160);
  const paket = String(body.paket || "").trim().slice(0, 80);
  const location = String(body.location || body.standort || "").trim().slice(0, 120);
  const demoType = String(body.demoType || body.demo_type || "").trim().slice(0, 80);
  const message = String(body.message || "").trim().slice(0, 2000);
  const privacy = String(body.privacy || "").trim();
  const lang = String(body.lang || "de").trim().slice(0, 8);
  const slotStart = String(body.slotStart || body.slot_start || "").trim();
  const slotEnd = String(body.slotEnd || body.slot_end || "").trim();

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ ok: false, error: "Valid email required" }, 400, cors);
  }
  if (!name) return json({ ok: false, error: "Name required" }, 400, cors);
  if (privacy !== "accepted") {
    return json({ ok: false, error: "Privacy consent required" }, 400, cors);
  }
  if (!slotStart || Number.isNaN(Date.parse(slotStart))) {
    return json({ ok: false, error: "Valid slot required" }, 400, cors);
  }

  const startDate = new Date(slotStart);
  const endDate = slotEnd && !Number.isNaN(Date.parse(slotEnd))
    ? new Date(slotEnd)
    : new Date(startDate.getTime() + cfg.durationMin * 60 * 1000);

  const ymd = ymdInTz(startDate, cfg.tz);
  const todayYmd = ymdInTz(new Date(), cfg.tz);
  const maxYmd = addDaysYmd(todayYmd, cfg.horizonDays);
  if (ymd < todayYmd || ymd > maxYmd) {
    return json({ ok: false, error: "Slot outside booking window" }, 400, cors);
  }

  const daySlots = generateDaySlots(ymd, cfg, new Date());
  const match = daySlots.find((s) => s.start === startDate.toISOString());
  if (!match) {
    return json({ ok: false, error: "Slot not available" }, 409, cors);
  }

  if (!env.DB) {
    return json({ ok: false, error: "Booking store not configured" }, 500, cors);
  }

  const id = newId();
  const slotStartIso = match.start;
  const slotEndIso = match.end;

  try {
    await env.DB.prepare(
      `INSERT INTO demo_bookings
        (id, slot_start, slot_end, name, email, company, paket, location, demo_type, lang, message, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmed')`
    )
      .bind(
        id,
        slotStartIso,
        slotEndIso,
        name,
        email,
        company,
        paket,
        location,
        demoType,
        lang,
        message
      )
      .run();
  } catch (err) {
    const msg = String(err?.message || err);
    if (/UNIQUE|constraint/i.test(msg)) {
      return json({ ok: false, error: "Slot already booked" }, 409, cors);
    }
    throw err;
  }

  const toEmail = env.TO_EMAIL || "info@suppixai.com";
  const fromEmail = env.FROM_EMAIL || "WorkPass <info@suppixai.com>";
  const notifyFrom = env.NOTIFY_FROM_EMAIL || "WorkPass Anfragen <anfragen@suppixai.com>";
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

  const whenLabel = formatSlotLabel(slotStartIso, cfg.tz, lang);
  const de = !lang || lang.startsWith("de");
  const ar = lang && lang.startsWith("ar");

  const ownerMail = ownerEmailHtml({
    fields: {
      Typ: "Demo-Termin",
      Name: name,
      EMail: email,
      Unternehmen: company,
      Paket: paket,
      Standort: location,
      "Demo-Typ": demoType,
      Termin: whenLabel,
      SlotStart: slotStartIso,
      Nachricht: message,
      Sprache: lang,
      BookingId: id,
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
    subject: `Demo-Termin – ${name} · ${whenLabel}`,
    html: ownerMail.html,
    text: ownerMail.text,
  });

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

  const title = de ? "Termin bestätigt" : ar ? "تم تأكيد الموعد" : "Booking confirmed";
  const thanks = de
    ? `Ihr Demo-Termin für <strong style="color:#0f172a">${escapeHtml(platform)}</strong> ist gebucht.`
    : ar
      ? `تم حجز موعد العرض لـ <strong style="color:#0f172a">${escapeHtml(platform)}</strong>.`
      : `Your <strong style="color:#0f172a">${escapeHtml(platform)}</strong> demo is booked.`;
  const whenTitle = de ? "Ihr Termin" : ar ? "موعدك" : "Your appointment";
  const cta = de ? "Website öffnen" : ar ? "فتح الموقع" : "Open website";
  const closing = de
    ? `Mit freundlichen Grüßen<br><strong style="color:#0f172a">Ihr Team von ${escapeHtml(brandCompany)}</strong>`
    : ar
      ? `مع أطيب التحيات<br><strong style="color:#0f172a">فريق ${escapeHtml(brandCompany)}</strong>`
      : `Kind regards<br><strong style="color:#0f172a">Your team at ${escapeHtml(brandCompany)}</strong>`;

  const bodyHtml = `
<p style="margin:0 0 10px;font-size:22px;font-weight:700;color:#0f172a;line-height:1.3">${greeting}</p>
<p style="margin:0 0 18px;font-size:15px;line-height:1.65;color:#475569">${thanks}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8fafc" style="background-color:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;margin:0 0 20px">
  <tr><td style="padding:14px 16px">
    <p style="margin:0 0 6px;font-weight:700;font-size:14px;color:#0f172a">${whenTitle}</p>
    <p style="margin:0;font-size:16px;color:#0f172a;font-weight:700">${escapeHtml(whenLabel)}</p>
    <p style="margin:8px 0 0;font-size:13px;color:#64748b">${cfg.durationMin} min · ${escapeHtml(cfg.tz)}${demoType ? ` · ${escapeHtml(demoType)}` : ""}</p>
  </td></tr>
</table>
${ctaButton(website, cta)}
<p style="margin:12px 0 0;font-size:14px;line-height:1.6;color:#334155">${closing}</p>`;

  const customerHtml = emailShell({
    logoSrc: "cid:suppix-logo",
    company: brandCompany,
    platform,
    website,
    titleBadge: title,
    bodyHtml,
    footerNote: `${escapeHtml(brandCompany)} · `,
    dir: ar ? "rtl" : "ltr",
    useImage: true,
  });

  const ics = buildIcs({
    uid: `${id}@suppixai.com`,
    startIso: slotStartIso,
    endIso: slotEndIso,
    summary: `${platform} Demo`,
    description: `Demo with ${brandCompany}. Paket: ${paket || "-"}. Location: ${location || "-"}. Type: ${demoType || "-"}.`,
    organizerEmail: toEmail,
  });

  await sendResend(env, {
    from: fromEmail,
    to: [email],
    reply_to: toEmail,
    subject: de
      ? `Demo bestätigt – ${whenLabel}`
      : ar
        ? `تأكيد الموعد – ${whenLabel}`
        : `Demo confirmed – ${whenLabel}`,
    html: customerHtml,
    text: [
      title,
      "",
      greeting.replace(/<[^>]+>/g, ""),
      thanks.replace(/<[^>]+>/g, ""),
      whenLabel,
      website,
    ].join("\n"),
    attachments: [
      logoAttachment(logo),
      {
        filename: "workpass-demo.ics",
        content: toBase64(ics),
      },
    ],
  });

  return json(
    {
      ok: true,
      id,
      slotStart: slotStartIso,
      slotEnd: slotEndIso,
      label: whenLabel,
    },
    200,
    cors
  );
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
}

export { bookingConfig, formatSlotLabel };
