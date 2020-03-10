DROP TABLE IF EXISTS playerstats;

CREATE TABLE playerstats (
playerId TEXT,
season TEXT,
shots INTEGER,
goals INTEGER,
assists INTEGER,
points INTEGER,
plusMinus INTEGER,
shotsAgainst INTEGER,
saves INTEGER);

ALTER TABLE playerstats
  ADD CONSTRAINT uq_playerstats UNIQUE(playerId, season);