-- Add manage token for cancel / reschedule links
ALTER TABLE demo_bookings ADD COLUMN manage_token TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_demo_bookings_manage_token
  ON demo_bookings(manage_token)
  WHERE manage_token IS NOT NULL;
