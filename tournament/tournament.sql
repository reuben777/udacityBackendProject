-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
\c tournament

CREATE DATABASE tournament;

CREATE TABLE players (
  id SERIAL PRIMARY KEY, 
  name TEXT
);
CREATE TABLE tournaments (
  id SERIAL PRIMARY KEY, 
  title TEXT
);
CREATE TABLE tournament_info(
  Id SERIAL PRIMARY KEY NOT NULL,
  tournament_id INT REFERENCES tournaments(id),
  playerId INT REFERENCES players(id)
);
CREATE TABLE matches (
  id SERIAL PRIMARY KEY, 
  winner INTEGER REFERENCES players(id),
  loser INTEGER REFERENCES players(id),
  tournament_id INTEGER REFERENCES tournaments(id),
  isDraw BOOLEAN DEFAULT FALSE
);

INSERT INTO tournaments (title) VALUES (1,'Unassigned 500');
INSERT INTO tournaments (title) VALUES (2,'Caster Under 25');
INSERT INTO tournaments (title) VALUES (3,'IIPS');
