DROP DATABASE IF EXISTS tournament;
-- create database
CREATE DATABASE tournament;
-- connect to the database
\c tournament

CREATE TABLE players(Id SERIAL PRIMARY KEY, Name TEXT);
CREATE TABLE matches(Id SERIAL PRIMARY KEY, Winner INTEGER REFERENCES players(Id), Loser INTEGER REFERENCES players(Id));
CREATE VIEW playerdetails as
SELECT p.id, p.name, coalesce(count(m1.*),0) as wins, coalesce(count(m2.*),0) as losses from players p left outer join matches m1 on (p.Id = m1.Winner)
left outer join matches m2 on (p.Id = m2.Loser) GROUP BY p.id ORDER BY wins desc;
