DROP TABLE IF EXISTS games;

CREATE TABLE games (
  gameId  TEXT UNIQUE,
  gameDate TIMESTAMP WITH TIME ZONE,
  season TEXT,
  homeTeamId TEXT,
  homeTeamName TEXT,
  awayTeamId TEXT,
  awayTeamName TEXT,
  statusCode TEXT,
  detailedState TEXT);