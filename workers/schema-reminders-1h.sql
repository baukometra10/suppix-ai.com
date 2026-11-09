-- ~1h SMS/email reminder tracking (in addition to ~24h reminder_sent_at)
ALTER TABLE demo_bookings ADD COLUMN reminder_1h_sent_at TEXT;
