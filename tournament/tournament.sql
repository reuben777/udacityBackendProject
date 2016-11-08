-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP TABLE IF EXISTS PLAYERINFO;
DROP TABLE IF EXISTS TOURNAMENTINFO;
DROP TABLE IF EXISTS TOURNAMENTS;
DROP VIEW IF EXISTS STANDINGS;
DROP TABLE IF EXISTS MATCHRESULTS;
DROP TABLE IF EXISTS MATCHRECORDS;
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

CREATE TABLE PLAYERINFO(
   Id INT PRIMARY KEY NOT NULL,
   playerName VARCHAR(50) NOT NULL,
   playerSurname VARCHAR(50) NOT NULL,
   dateCreated timestamp DEFAULT current_timestamp,
   dateUpdated timestamp DEFAULT current_timestamp
);
CREATE TABLE TOURNAMENTS(
	Id INT PRIMARY KEY NOT NULL,
	tournamentName TEXT NOT NULL
);
CREATE TABLE TOURNAMENTINFO(
  Id INT PRIMARY KEY NOT NULL,
  tournamentId INT NOT NULL,
  playerId INT NOT NULL
);
CREATE TABLE MATCHRESULTS(
	Id INT PRIMARY KEY NOT NULL,
	resultName VARCHAR(5)
);
CREATE TABLE MATCHRECORDS(
	Id INT PRIMARY KEY NOT NULL,
	player_Id INT NOT NULL,
  	opponent_Id INT NOT NULL,
	matchResult_Id INT NOT NULL,
	tournamentId INT NOT NULL,
	roundNumber INT NOT NULL,
  points INT NOT NULL
);

-- CREATE VIEW STANDINGS AS
--     SELECT mr.player_Id, mr.tournamentId,
--     (SELECT COUNT(*) FROM MATCHRECORDS as mr2 WHERE mr2.tournamentId = mr.tournamentId and mr2.player_Id = mr.player_Id and mr2.matchResult_Id = 1) as WINS,
--     (SELECT COUNT(*) FROM MATCHRECORDS as mr2 WHERE mr2.tournamentId = mr.tournamentId and mr2.player_Id = mr.player_Id and mr2.matchResult_Id = 2) as LOSES,
--     (SELECT COUNT(*) FROM MATCHRECORDS as mr2 WHERE mr2.tournamentId = mr.tournamentId and mr2.player_Id = mr.player_Id and mr2.matchResult_Id = 3) as DRAWS,
--     (SELECT SUM(points) FROM MATCHRECORDS as mr2 WHERE mr2.tournamentId = mr.tournamentId and mr2.player_Id = mr.player_Id) as POINTS
--     FROM MATCHRECORDS as mr
--     GROUP BY mr.player_Id, mr.tournamentId
--     ORDER BY POINTS DESC;

CREATE VIEW STANDINGS AS
    SELECT pi.Id, mr.player_Id, mr.tournamentId,
    (SELECT COUNT(*) FROM MATCHRECORDS as mr2 WHERE mr2.tournamentId = mr.tournamentId and mr2.player_Id = mr.player_Id and mr2.matchResult_Id = 1) as WINS,
    (SELECT COUNT(*) FROM MATCHRECORDS as mr2 WHERE mr2.tournamentId = mr.tournamentId and mr2.player_Id = mr.player_Id and mr2.matchResult_Id = 2) as LOSES,
    (SELECT COUNT(*) FROM MATCHRECORDS as mr2 WHERE mr2.tournamentId = mr.tournamentId and mr2.player_Id = mr.player_Id and mr2.matchResult_Id = 3) as DRAWS,
    (SELECT SUM(points) FROM MATCHRECORDS as mr2 WHERE mr2.tournamentId = mr.tournamentId and mr2.player_Id = mr.player_Id) as POINTS
    FROM PLAYERINFO as pi
    LEFT OUTER JOIN MATCHRECORDS as mr ON (mr.player_Id = pi.Id)
    GROUP BY pi.Id, mr.player_Id, mr.tournamentId
    ORDER BY POINTS DESC;

INSERT INTO MATCHRESULTS (Id,resultName) VALUES (1,'Win');
INSERT INTO MATCHRESULTS (Id,resultName) VALUES (2,'Loss');
INSERT INTO MATCHRESULTS (Id,resultName) VALUES (3,'Draw');

INSERT INTO TOURNAMENTS (Id,tournamentName) VALUES (1,'Unassigned 500');
INSERT INTO TOURNAMENTS (Id,tournamentName) VALUES (2,'Caster Under 25');
INSERT INTO TOURNAMENTS (Id,tournamentName) VALUES (3,'IIPS');
