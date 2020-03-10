DROP TABLE IF EXISTS shifts;

CREATE TABLE shifts (
  gameId  TEXT,
  shiftId TEXT,
  typeCode TEXT,
  eventDescription TEXT,
  shiftNumber INTEGER,
  teamId TEXT,
  duration INTEGER,
  eventNumber INTEGER,
  homeTeamId TEXT,
  teamName TEXT,
  period TEXT,
  playerName TEXT,
  detailCode TEXT,
  eventDetails TEXT,
  visitingTeamId TEXT,
  teamAbbrev TEXT,
  playerId TEXT,
  startTime INTEGER,
  endTime INTEGER);