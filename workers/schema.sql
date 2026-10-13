-- Demo bookings for Suppix marketing site
CREATE TABLE IF NOT EXISTS demo_bookings (
  id TEXT PRIMARY KEY,
  slot_start TEXT NOT NULL,
  slot_end TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  company TEXT,
  paket TEXT,
  location TEXT,
  demo_type TEXT,
  lang TEXT,
  message TEXT,
  status TEXT NOT NULL DEFAULT 'confirmed',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_demo_bookings_slot
  ON demo_bookings(slot_start)
  WHERE status = 'confirmed';

CREATE INDEX IF NOT EXISTS idx_demo_bookings_email
  ON demo_bookings(email);
