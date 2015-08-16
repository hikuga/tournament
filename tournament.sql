-- This is the new sql file. Looks liek previous upload had the incorrect file.
DROP TABLE IF EXISTS players;
CREATE TABLE players(Id SERIAL PRIMARY KEY, Name TEXT);
DROP TABLE IF EXISTS matches;
CREATE TABLE matches(Id SERIAL PRIMARY KEY, MatchId INTEGER, PlayerId INTEGER, Score INTEGER);
