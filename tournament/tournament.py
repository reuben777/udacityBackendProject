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
    submitSQL("DELETE FROM matches")
    submitSQL("DELETE FROM tournament_info")


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
    # print ("Total number of rows deleted :", deleteCount)


def countPlayers():
    """Returns the number of players currently registered."""
    returnInfo = submitSQL("SELECT COUNT(*) FROM players")
    playerCount = 0
    if len(returnInfo) > 0:
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
        submitSQL('''INSERT INTO players (name) VALUES (%s)''', (name,))
    else:
        print("Please specify a name")
        requestPlayerName()


def playerStandings(tournamentId=1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    playerCount = 0
    players = submitSQL('''SELECT id, name FROM players''')
    playersList = []
    for player in players:
        playerId = str(player[0])
        playerName = player[1]
        numOfMatches = 0
        sql = '''SELECT COUNT(id) FROM matches WHERE winner = %s'''
        wins = submitSQL(sql, (playerId,))
        sql = '''SELECT COUNT(id) FROM matches WHERE loser = %s'''
        loses = submitSQL(sql, (playerId,))
        numOfMatches = int(wins[0][0]) + int(loses[0][0])
        tup = int(playerId), playerName, int(wins[0][0]), numOfMatches
        playersList.append(tup)
        
    return sorted(playersList, key=lambda x: int(x[2]), reverse=True)  


def getMatchNumber(playerOneId, playerTwoId, tournamentId=1):
    sql = '''SELECT COUNT(id) FROM 
    matches WHERE winner = %s or loser = %s 
    AND tournament_id = %s'''
    matches = submitSQL(sql, (playerOneId, playerTwoId, tournamentId))
    numOfMatches = matches[0][0] + 1
    return numOfMatches
    
    
def createMatchRecord(playerId, opponentId, tournamentId, isDraw, roundNumber):
    if roundNumber <= 4:
        sql = '''INSERT INTO matches 
        (winner,loser,tournament_id,isDraw) 
        VALUES (%s,%s,%s,%s)
        returning id'''
        matchId = submitSQL(sql, (playerId, opponentId, tournamentId, isDraw))
        if matchId[0][0]:
            return True
        else:
            return False
    else:
        print("Players cannot play more than 3 matches")
        return False


def reportMatch(winner, loser, tournamentId=1, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    roundNumber = getMatchNumber(winner, loser, tournamentId)
    winnerSQL = createMatchRecord(
        winner, 
        loser, 
        tournamentId, 
        draw, 
        roundNumber)


def isPairable(tournamentId, player1Id, player2Id):
    playable = True
    drawOccured = False
    lossOccured = False
    matchCount = 0
    sql = '''SELECT * FROM 
    matches WHERE 
    winner = %s 
    and winner = %s 
    and tournament_id = %s'''
    matchInfo = submitSQL(sql, (player1Id, player2Id, tournamentId))
    if len(matchInfo) > 0:
        for match in matchInfo:
            matchCount += 1
            if match[1] == player1Id:
                drawOccured = True
            elif match[2] == player1Id:
                lossOccured = True
    if matchCount == 2:
        if not lossOccured and not drawOccured:
            playable = False
        if lossOccured and not drawOccured:
            playable = False
    if matchCount == 3:
        playable = False
    return playable


def getPlayersFromTournament(tournamentId):
    sql = '''SELECT pl.id,pl.name,ti.tournament_id 
    FROM players as pl LEFT 
    OUTER JOIN tournament_info as ti 
    ON (%s= ti.tournament_id)'''
    players = submitSQL(sql, str(tournamentId))
    return players 


def isInPlayerTuple(value, tup):
    found = False
    for tupItem in tup:
        if int(value) in tupItem:
            found = True
    return found


def swissPairings(tournamentId=1):
    """Returns a list of pairs of players for
    the next round of a match.

    # First get BY if total num of players odd
    # 

    Assuming that there are an even number of players
    registered, each player
    appears exactly once in the pairings.  
    Each player is paired with another
    player with an equal or nearly-equal win record, 
    that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which 
      contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    playerTuple = []
    players = playerStandings(tournamentId)
    sql = '''SELECT * FROM matches where
    tournament_id = %s'''
    matches = submitSQL(sql, (tournamentId,))
    playersCount = 0
    NumOfMatches = len(matches)
    for player in players:
        if NumOfMatches > 0:
            for opponent in players:
                if not isInPlayerTuple(player[0], playerTuple)
                and not isInPlayerTuple(opponent[0], playerTuple):
                    # Opponent and player havent been assigned yet
                    if player[0] != opponent[0] 
                    and isPairable(tournamentId, player[0], opponent[0]):
                        # Can they pair? have they played together yet?
                        combined = (player[0], player[1], opponent[0], opponent[1])
                        playerTuple.append(combined)
                        break;
        else:
            if playersCount % 2 != 0:
                combined = (players[playersCount - 1][0], 
                players[playersCount - 1][1], 
                player[0], 
                player[1])
                playerTuple.append(combined)
        playersCount += 1
    return playerTuple


# Uses Raw Input to return a players name and surname.
def requestPlayerName():
    name = raw_input('''What's your Name and Surname?(Middle names will be excluded) 
    Example: John Snow : ''')
    registerPlayer(name)


# Generic submit SQL query.
def submitSQL(SQL, data=""):
    conn = connect()
    cursi = conn.cursor()
    if data:
        cursi.execute(SQL, data)
    else:
        cursi.execute(SQL)
    SQLResponse = ""
    try:
        SQLResponse = cursi.fetchall()
    except:
        SQLResponse = ""
    conn.commit()
    conn.close()
    return SQLResponse


def assignPlayerToTournament():
    sql = '''SELECT * FROM  players'''
    players = submitSQL(sql)
    if len(players) > 0:
        print("Players:")
        for player in players:
            print("Player Id - ", player[0])
            print("Player Name - ", player[1])
    playerId = input('''Please Enter the Player Id 
    you wish to enroll in a tournament :''')
    try:
        playerId = int(playerId)
    except ValueError:
        print("An error occured when get player info")
        sql = '''SELECT * FROM tournaments'''
    tournaments = submitSQL(sql)
    print("Tournaments:")
    if len(tournaments) > 0:
        for tournament in tournaments:
            print("Tournament Id - ", tournament[0])
            print("Tournament Title - ", tournament[1])
    else:
        print("--Empty--")

    tournamentId = input("Please Enter the Tournament Id you wish to assign player to :")
    try:
        tournamentId = int(tournamentId)
        sql = '''INSERT INTO tournament_info (tournament_id,player_id) 
        VALUES (%s,%s) returning Id'''
        tournamentInfo = submitSQL(sql, (tournamentId, playerId))
        if tournamentInfo[0][0]:
            print("Player Assigned to Tournament")
        else:
            print("An error occured when attempting to assign player")
    except ValueError:
        print("An error occured when attempting to assign player")
