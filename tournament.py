#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        con = psycopg2.connect("dbname=tournament")
        cur = con.cursor()
        return (con, cur)
    except:
        print 'Unable to connect to database tournament'
        return (None, None)


def deleteMatches():
    """Remove all the match records from the database."""
    con, cur = connect()
    if con is None or cur is None:
        return None
    try:
        cur.execute('TRUNCATE TABLE matches CASCADE;')
        con.commit()
    except:
        return None
    finally:
        cur.close()
        con.close()


def deletePlayers():
    """Remove all the player records from the database."""
    con, cur = connect()
    if con is None or cur is None:
        return None
    #if deleteMatches() is None:
        #return None
    try:
        cur.execute('TRUNCATE TABLE players CASCADE;')
        con.commit()
    except:
        return None
    finally:
        cur.close()
        con.close()

def countPlayers():
    """Returns the number of players currently registered."""
    con, cur = connect()
    if con is None or cur is None:
        return None
    try:
        cur.execute('SELECT count(*) FROM players;')
        row = cur.fetchone()
        if row is None:
            return 0
        else:
            return row[0]
    except:
        return None
    finally:
        cur.close()
        con.close()


def registerPlayer(name):
    """Adds a player to the tournament database.
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
    Args:
      name: the player's full name (need not be unique).
    """
    lastrowid = 0
    con, cur= connect()
    if con is None or cur is None:
        return None
    try:
        insStmt = 'INSERT INTO players(name) VALUES(%s);'
        cur.execute(insStmt, (name, ))
        con.commit()
        lastrowid = cur.lastrowid
        return lastrowid
    except:
        return None
    finally:
        cur.close()
        con.close()


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
    con, cur = connect()
    if con is None or cur is None:
        return None
    query = 'select p.id, p.name, COALESCE(sum(pd.score)/4,0) as wins, count(pd.*) as total from \
             players p left outer join playerdetails pd on (p.id = pd.id) group by p.id order by wins desc;'
    try:
        cur.execute(query)
        rows = cur.fetchall()
        if rows is None:
            return 0
        else:
            return rows
    except:
        return None
    finally:
        cur.close()
        con.close()


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.
    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    con, cur = connect()
    if con is None or cur is None:
        return None
    try:
        insStmt = 'INSERT INTO matches(Player1, Score1, Player2, Score2) VALUES(%s,%s,%s,%s);'
        cur.execute(insStmt, (winner, 4, loser, 0))
        con.commit()
        return cur.lastrowid
    except:
        return None
    finally:
        cur.close()
        con.close()


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
    #build a lookup to check re-matches
    _records = {}
    con, cur = connect()
    if con is None or cur is None:
        return None
    query = 'select player1, player2 from matches'
    try:
        cur.execute(query)
        for row in cur.fetchall():
            if row[0] not in _records:
                _records[row[0]] = set()
            if row[1] not in _records:
                _records[row[1]] = set()
            _records[row[0]].add(row[1])
            _records[row[1]].add(row[0])
    except:
        return None
    finally:
        cur.close()
        con.close()

    pairs = []
    pmem = set()
    pstandings = playerStandings()
    for ith, playerinfo1 in enumerate(pstandings):
            if playerinfo1[0] in pmem:
                continue
            for jth, playerinfo2 in enumerate(pstandings[ith+1:]):
                if playerinfo2[0] in pmem or int(playerinfo2[0]) in _records[playerinfo1[0]]:
                    continue
                pairs.append((playerinfo1[0], playerinfo1[1], playerinfo2[0], playerinfo2[1]))
                pmem.add(playerinfo1[0])
                pmem.add(playerinfo2[0])
                break

    return pairs
