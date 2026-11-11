/*
# Seed Le Mans Ultimate circuits

1. Modified Tables
- `tracks`: adds the 18 circuits of Le Mans Ultimate so they can be selected in the app.
  - Base game: Algarve International Circuit, Bahrain International Circuit, Circuit de la Sarthe (Le Mans), Fuji Speedway, Autodromo Nazionale Monza, Sebring International Raceway, Circuit de Spa-Francorchamps.
  - 2024 DLC: Autodromo Enzo e Dino Ferrari (Imola), Circuit of the Americas, Autodromo Jose Carlos Pace (Interlagos), Lusail International Circuit.
  - ELMS DLC: Silverstone Circuit, Circuit Paul Ricard, Circuit de Barcelona-Catalunya.
  - US Track DLC: Daytona International Speedway, WeatherTech Raceway Laguna Seca, Michelin Raceway Road Atlanta, Streets of Long Beach Circuit.

2. Security
- No table, policy or grant changes. Existing RLS rules still apply.

3. Important notes
- Idempotent: names that already exist are skipped (ON CONFLICT on the unique name), so re-running does not duplicate rows or remove existing ones.
- Track names are written as fixed text, not generated ids, so a fresh database gets the same rows.
*/

INSERT INTO tracks (name) VALUES
  ('Algarve International Circuit (Portimao)'),
  ('Bahrain International Circuit'),
  ('Circuit de la Sarthe (Le Mans)'),
  ('Fuji Speedway'),
  ('Autodromo Nazionale Monza'),
  ('Sebring International Raceway'),
  ('Circuit de Spa-Francorchamps'),
  ('Autodromo Internazionale Enzo e Dino Ferrari (Imola)'),
  ('Circuit of the Americas (COTA)'),
  ('Autodromo Jose Carlos Pace (Interlagos)'),
  ('Lusail International Circuit'),
  ('Silverstone Circuit'),
  ('Circuit Paul Ricard'),
  ('Circuit de Barcelona-Catalunya'),
  ('Daytona International Speedway'),
  ('WeatherTech Raceway Laguna Seca'),
  ('Michelin Raceway Road Atlanta'),
  ('Streets of Long Beach Circuit')
ON CONFLICT (name) DO NOTHING;
