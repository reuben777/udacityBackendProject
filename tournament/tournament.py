#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from psycopg2.extensions import AsIs
from array import array

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect(database="tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    submitSQL("DELETE FROM match")
    submitSQL("DELETE FROM TOURNAMENTINFO")

def deletePlayers():
    """Remove all the player records from the database."""
    # matchCount = submitSQL("SELECT COUNT(Id) FROM MATCHRESULTS")
    deleteCount = 0
    # if matchCount > 0 :
        conn = connect()
        cursi = conn.cursor()
        cursi.execute('''DELETE FROM players''')
        deleteCount = cursi.rowcount
        conn.commit()
        conn.close()
    print ("Total number of rows deleted :", deleteCount)

def countPlayers():
    """Returns the number of players currently registered."""
    returnInfo = submitSQL("SELECT COUNT(*) FROM players")
    playerCount = 0
    if len(returnInfo) > 0:
        print returnInfo
        # TODO here
        playerCount = int(returnInfo[0][0]) 
    return playerCount

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    if name:
        submitSQL('''INSERT INTO players (name) VALUES (%s)''',(name,))
    else:
        print("Please specify a name")
        requestPlayerName()

def playerStandings(tournamentId=1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    playerCount = 0
    players = submitSQL('''SELECT id, name FROM player_info''')
    playersList = []
    for player in players:
        playerId = str(player[0])
        playerName = player[1]
        numOfMatches = 0
        winnings = submitSQL('''SELECT COUNT(id) FROM matches WHERE winner = %s''',(playerId,playerId))
        loses = submitSQL('''SELECT COUNT(id) FROM matches WHERE loser = %s''',(playerId,playerId))
        numOfMatches = winnings + loses
        tup = playerId,playerName,wins,numOfMatches
        playersList.append(tup)
    return playersList

def getMatchNumber(playerOneId,playerTwoId,tournamentid=1):
    matches = submitSQL('''SELECT * FROM matches WHERE winner = %s or winner = %s AND tournament_id = %s''',(playerOneId,playerTwoId,tournamentid))
    numOfMatches = len(matches) + 1
    return numOfMatches

def reportMatch(winner, loser,tournamentId=1,draw=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    roundNumber = getMatchNumber(winner,loser,tournamentid)
    winnerSQL = createMatchRecord(winner,loser,tournamentId,winnerResultId,roundNumber,winnerPoints)
    loserSQL = createMatchRecord(loser,winner,tournamentId,loserResultId,roundNumber,loserPoints)

    if winnerSQL and loserSQL:
        print("Match Reported")
    else:
        print("An Error Occured while attempting to report match")

def isPairable(tournamentId,player1Id,player2Id):
    playable = True;
    drawOccured = False;
    lossOccured = False;
    matchCount = 0;
    sql = "SELECT * FROM matches WHERE winner = %s and winner = %s and tournamentid = %s";
    matchInfo = submitSQL(sql,(player1Id,player2Id,tournamentId))
    if len(matchInfo) > 0 :
        for match in matchInfo:
            matchCount += 1;
            if match[1] == player1Id:
                drawOccured = True
            elif match[2] == player1Id:
                lossOccured = True;

    if matchCount == 2:
        if not lossOccured and not drawOccured:
            playable = False
        if lossOccured and not drawOccured:
            playable = False
    if matchCount == 3:
        playable = False

    return playable

def getPlayersFromTournament(tournamentId):
    players = submitSQL("SELECT pl.id,pl.name,ti.tournament_id FROM players as pl LEFT OUTER JOIN tournament_info as ti ON (%s= ti.tournament_id)",str(tournamentId))
    return players 

def swissPairings(tournamentId=1):
    """Returns a list of pairs of players for the next round of a match.

    # First get BY if total num of players odd
    # 

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    playerTuple = []
    players = getPlayersFromTournament(tournamentId)
    playersStandingsInfo = submitSQL("SELECT * FROM STANDINGS where tournamentId = %s",str(tournamentId))
    matchInfo = playerStandings(tournamentId)
    if len(playersStandingsInfo) > 0:
        if len(playersStandingsInfo) % 2 == 0:  
            for i in xrange(0,len(playersStandingsInfo),2):
                playerPairInfo = submitSQL("SELECT pi.Id,pi.playerName,ti.tournamentId FROM PLAYERINFO as pi LEFT OUTER JOIN TOURNAMENTINFO as ti ON (%s= ti.tournamentId) where pi.Id = %s or pi.Id = %s",(str(tournamentId),playersStandingsInfo[i][0],playersStandingsInfo[i+1][0]))
                numOfPlayableMatches = len(playersStandingsInfo) / 2
                if matchInfo[i][3] <= numOfPlayableMatches and matchInfo[i+1][3] <= numOfPlayableMatches:
                    if isPairable(playerPairInfo[0][0],playerPairInfo[1][0],tournamentId):
                        if playerPairInfo[0][2] is None and tournamentId ==  1:
                            tup = str(playerPairInfo[0][0]),playerPairInfo[0][1],str(playerPairInfo[1][0]),playerPairInfo[1][1]
                            playerTuple.append(tup)
                        elif not playerPairInfo[0][2] is None and not tournamentId == 1:
                            if isPairable(playerPairInfo[0][0],playerPairInfo[1][0],tournamentId):
                                tup = str(playerPairInfo[0][0]),playerPairInfo[0][1],str(playerPairInfo[1][0]),playerPairInfo[1][1]
                                playerTuple.append(tup)
        else:
            print "give BY here"
    else:
        if len(players) % 2 == 0:  
            for i in xrange(0,len(players),2):
                if isPairable(players[i][0],players[i+1][0],tournamentId):
                    if players[i][2] is None and tournamentId ==  1:
                        tup = str(players[i][0]),players[i][1],str(players[i+1][0]),players[i+1][1]
                        playerTuple.append(tup)
                    elif not players[i][2] is None and not tournamentId == 1:
                        if isPairable(players[i][0],players[i+1][0],tournamentId):
                            tup = str(players[i][0]),players[i][1],str(players[i+1][0]),players[i+1][1]
                            playerTuple.append(tup)
        else:
            print "give BY here"
    return playerTuple


# Uses Raw Input to return a players name and surname.
def requestPlayerName():
    name = raw_input("What's your Name and Surname?(Middle names will be excluded) Example: John Snow : ")
    registerPlayer(name)

# Generic submit SQL query.
def submitSQL(SQL,data=""):
    conn = connect()
    cursi = conn.cursor()
    if data:
        cursi.execute(SQL,data)
    else:
        cursi.execute(SQL)
    SQLResponse = ""
    try:
        SQLResponse = cursi.fetchall()
    except:
        SQLResponse = "";
    conn.commit()
    conn.close()
    return SQLResponse


def assignPlayerToTournament():
    players = submitSQL('''SELECT * FROM  players''')
    if len(players) > 0:
        print("Players:")
        for player in players:
            print("Player Id - ",player[0])
            print("Player Name - ",player[1])
    playerId = input("Please Enter the Player Id you wish to enroll in a tournament :")
    try:
        playerId = int(playerId)
    except ValueError:
        print("An error occured when get player info")
    tournaments = submitSQL('''SELECT * FROM tournaments''')
    print("Tournaments:")
    if len(tournaments) > 0:
        for tournament in tournaments:
            print("Tournament Id - ",tournament[0])
            print("Tournament Title - ",tournament[1])
    else:
        print("--Empty--")

    tournamentId = input("Please Enter the Tournament Id you wish to assign player to :")
    try:
        tournamentId = int(tournamentId)
        tournamentInfo = submitSQL('''INSERT INTO tournament_info (tournament_id,player_id) VALUES (%s,%s) returning Id''',(tournamentId,playerId))
        if tournamentInfo[0][0]:
            print("Player Assigned to Tournament")
        else:
            print("An error occured when attempting to assign player")
    except ValueError:
        print("An error occured when attempting to assign player")

def createMatchRecord(playerId,opponentId,tournamentId,isDraw,roundNumber):
    if roundNumber <= 4:
        matchId = submitSQL('''INSERT INTO matches (winner,loser,tournamentId,isDraw) VALUES (%s,%s,%s,%s) returning Id''',(playerId,opponentId,tournamentId,isDraw))
        if matchId[0][0]:
            return True
        else:
            return False;
    else:
        print("Players cannot play more than 3 matches")
        return False;


registerPlayer('Test User')