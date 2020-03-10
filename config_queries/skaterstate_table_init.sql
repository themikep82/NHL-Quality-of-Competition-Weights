DROP TABLE IF EXISTS skaterStates;

CREATE TABLE skaterStates(
  gameId TEXT, 
  shiftId TEXT,
  period TEXT, 
  playerId TEXT, 
  playerName TEXT, 
  position TEXT,
  teamId TEXT,
  teamName TEXT,
  opposingPlayerId TEXT,
  opposingplayerName TEXT,
  opposingPosition TEXT,
  opposingTeamId TEXT,
  opposingTeamName TEXT,
  iceTimeSeconds INTEGER,
  strengthState TEXT);