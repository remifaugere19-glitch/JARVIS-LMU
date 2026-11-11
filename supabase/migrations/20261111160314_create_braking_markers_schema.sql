/*
# Create braking markers schema

1. New Tables
- `tracks`: circuits of Le Mans Ultimate.
  - `id` (uuid, primary key)
  - `name` (text, required, unique) - track name as shown in the game
  - `created_at` (timestamptz)
- `cars`: cars of Le Mans Ultimate and custom team cars.
  - `id` (uuid, primary key)
  - `name` (text, required) - car model, e.g. "Porsche 963"
  - `category` (text, required) - e.g. "Hypercar", "LMGT3"
  - `source` (text, required) - "game" for official cars, "custom" for custom team cars
  - `team_name` (text, optional) - custom team name when source is "custom"
  - `created_at` (timestamptz)
- `braking_markers`: a braking reference point for one car on one track.
  - `id` (uuid, primary key)
  - `track_id` (uuid, references tracks, cascade delete)
  - `car_id` (uuid, references cars, cascade delete)
  - `label` (text, required) - corner name, e.g. "Virage 1"
  - `distance_m` (integer, required, >= 0) - distance from the start/finish line in meters
  - `brake_speed_kmh` (integer, optional) - speed at which braking starts
  - `notes` (text, optional)
  - `created_at` (timestamptz)

2. Security
- Row level security is enabled on all three tables.
- This app has no sign-in, so the data is intentionally shared: anon and authenticated roles can read, create, update and delete.
- Grants are given only for the verbs the app uses.

3. Important notes
- No existing data is modified or removed.
- Markers are removed automatically when their track or car is deleted.
- Migration is idempotent: tables, indexes and policies use IF NOT EXISTS or DROP POLICY IF EXISTS.
*/

CREATE TABLE IF NOT EXISTS tracks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cars (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  category text NOT NULL,
  source text NOT NULL CHECK (source IN ('game', 'custom')),
  team_name text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS braking_markers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  track_id uuid NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
  car_id uuid NOT NULL REFERENCES cars(id) ON DELETE CASCADE,
  label text NOT NULL,
  distance_m integer NOT NULL CHECK (distance_m >= 0),
  brake_speed_kmh integer CHECK (brake_speed_kmh IS NULL OR brake_speed_kmh > 0),
  notes text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_braking_markers_track_car ON braking_markers (track_id, car_id, distance_m);

ALTER TABLE tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE cars ENABLE ROW LEVEL SECURITY;
ALTER TABLE braking_markers ENABLE ROW LEVEL SECURITY;

GRANT SELECT, INSERT, UPDATE, DELETE ON tracks TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON cars TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON braking_markers TO anon, authenticated;

DROP POLICY IF EXISTS "anon_select_tracks" ON tracks;
CREATE POLICY "anon_select_tracks" ON tracks FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_insert_tracks" ON tracks;
CREATE POLICY "anon_insert_tracks" ON tracks FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_update_tracks" ON tracks;
CREATE POLICY "anon_update_tracks" ON tracks FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_delete_tracks" ON tracks;
CREATE POLICY "anon_delete_tracks" ON tracks FOR DELETE TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_select_cars" ON cars;
CREATE POLICY "anon_select_cars" ON cars FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_insert_cars" ON cars;
CREATE POLICY "anon_insert_cars" ON cars FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_update_cars" ON cars;
CREATE POLICY "anon_update_cars" ON cars FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_delete_cars" ON cars;
CREATE POLICY "anon_delete_cars" ON cars FOR DELETE TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_select_braking_markers" ON braking_markers;
CREATE POLICY "anon_select_braking_markers" ON braking_markers FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_insert_braking_markers" ON braking_markers;
CREATE POLICY "anon_insert_braking_markers" ON braking_markers FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_update_braking_markers" ON braking_markers;
CREATE POLICY "anon_update_braking_markers" ON braking_markers FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_delete_braking_markers" ON braking_markers;
CREATE POLICY "anon_delete_braking_markers" ON braking_markers FOR DELETE TO anon, authenticated USING (true);
