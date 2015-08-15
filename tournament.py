#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
matchIdNum = 1

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    con = connect()
    cur = con.cursor()
    cur.execute('DELETE FROM matches where Id <> 0')
    con.commit()
    #con.close()


def deletePlayers():
    """Remove all the player records from the database."""
    con = connect()
    cur = con.cursor()
    cur.execute('DELETE FROM players where Id <> 0')
    con.commit()

def countPlayers():
    """Returns the number of players currently registered."""
    con = connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM players')
    row = cur.fetchone()
    if row is None:
        return 0
    else:
        return row[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    lastrowid = 0
    con = connect()
    cur = con.cursor()
    insStmt = 'INSERT INTO players(name) VALUES(%s);'
    cur.execute(insStmt, (name, ))
    con.commit()
    lastrowid = cur.lastrowid
    return lastrowid


def playerStandings():
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
    con = connect()
    cur = con.cursor()
    query = 'select p.Id, p.Name, COALESCE(sum(m.Score)/4, 0) as wins, \
             COALESCE(count(m.Id),0) as total from players p left outer \
             join matches m on(p.Id = m.PlayerId) GROUP BY p.Id ORDER BY wins desc'
    cur.execute(query)
    rows = cur.fetchall()
    if rows is None:
        return 0
    else:
        return rows


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    global matchIdNum
    con = connect()
    cur = con.cursor()
    matchIdNum += 1
    insStmt = 'INSERT INTO matches(MatchId, PlayerId, Score) VALUES(%s,%s,%s);'
    cur.execute(insStmt, (matchIdNum, winner, 4, ))
    con.commit()
    insStmt = 'INSERT INTO matches(MatchId, PlayerId, Score) VALUES(%s,%s,%s);'
    cur.execute(insStmt, (matchIdNum, loser, 0, ))
    con.commit()
    return cur.lastrowid


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

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
    con = connect()
    cur = con.cursor()
    query = 'select p.Id, p.Name, sum(m.Score)/4 as wins, count(m.PlayerId) as total from \
             matches m join players p on(p.Id = m.PlayerId) GROUP BY p.Id ORDER BY \
             wins desc'
    cur.execute(query)
    rows = cur.fetchall()
    #Keep record of previous games to avoid re-matches.
    dupQuery = 'select  m1.PlayerId, array_agg( distinct m2.PlayerId) as opps from \
                matches m1 join matches m2 on m1.MatchId = m2.MatchId group by m1.PlayerId'
    cur.execute(dupQuery)
    duprows = cur.fetchall()
    dups = {duprow[0]:set(duprow[1]) for duprow in duprows}
    if rows is None:
        return None
    elif len(rows) & 1:
        print 'Odd number of teams not handled as per specs!'
        return None
    else:
        pairs = []
        for i in range(0, len(rows)):
            if [pair for pair in pairs if (pair[0] == rows[i][0]) or (pair[2] == rows[i][0])]:
                continue
            for j in range(i+1, len(rows)):
                #Only add to pairs is these two havent played before.
                if (rows[j][0] not in dups.get(rows[i][0], [])) and \
                    (not [pair for pair in pairs if (pair[0] == rows[j][0]) \
                    or (pair[2] == rows[j][0])]):
                    pairs.append((rows[i][0], rows[i][1], rows[j][0], rows[j][1]))
                    break
        return pairs
