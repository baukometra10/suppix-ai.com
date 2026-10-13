-- Demo reminder + offer tracking columns
ALTER TABLE demo_bookings ADD COLUMN reminder_sent_at TEXT;
ALTER TABLE demo_bookings ADD COLUMN offer_sent_at TEXT;
