DROP TABLE IF EXISTS players;

CREATE TABLE players (
playerId TEXT UNIQUE,
playerName TEXT,
dateOfBirth DATE,
position TEXT,
teamId TEXT,
teamName TEXT);