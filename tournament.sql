DROP VIEW IF EXISTS playerdetails;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;
CREATE TABLE players(Id SERIAL PRIMARY KEY, Name TEXT);
CREATE TABLE matches(Id SERIAL PRIMARY KEY, Player1 INTEGER REFERENCES players(Id), Score1 INTEGER, Player2 INTEGER REFERENCES players(Id), Score2 INTEGER);
CREATE VIEW playerdetails as
    SELECT p.id, p.name, m.score1 as score from players p join matches m on (p.id = m.player1)
    UNION ALL
    SELECT p.id, p.name, m.score2 as score from players p join matches m on (p.id = m.player2);

--INSERT INTO PLAYERS(NAME) VALUES('playea101');
--INSERT INTO PLAYERS(NAME) VALUES('playea102');
--INSERT INTO PLAYERS(NAME) VALUES('playea103');
--INSERT INTO PLAYERS(NAME) VALUES('playea104');
--INSERT INTO MATCHES(player1, score1, player2, score2) VALUES(1,4,2,0);
--INSERT INTO MATCHES(player1, score1, player2, score2) VALUES(3,4,4,0);
