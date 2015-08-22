#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
'''
swiss parings module.
'''
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

def runquery(query, res=False, params=None):
    '''
    Helper function to run a specified query.
    '''
    (executed, results) = (False, None)
    con, cur = connect()
    if con is None or cur is None:
        return (executed, results)
    try:
        if not params:
            cur.execute(query)
        else:
            cur.execute(query, params)
        if res:
            #print 'getting results for query: '+query
            results = cur.fetchall()
        else:
            con.commit()
        executed = True
    except Exception as err:
        print 'Exception here: '+str(err)
        return (False, None)
    finally:
        cur.close()
        con.close()
    return (executed, results)

def deleteMatches():
    """Remove all the match records from the database."""
    return runquery('TRUNCATE TABLE matches CASCADE;')[0]


def deletePlayers():
    """Remove all the player records from the database."""
    return runquery('TRUNCATE TABLE players CASCADE;')[0]


def countPlayers():
    """Returns the number of players currently registered."""
    (executed, results) = runquery('SELECT count(*) from players;', True)
    if executed and results:
        return results[0][0]
    else:
        return 0

def registerPlayer(name):
    """Adds a player to the tournament database.
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
    Args:
      name: the player's full name (need not be unique).
    """
    return runquery('INSERT INTO players(name) VALUES(%s);', False,
    params=(name, ))[0]


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
    (executed, results) = runquery('''select id, max(name), max(wins), \
    sum(wins+losses) from playerdetails group by id;''', True)
    if executed and results:
        return results
    else:
        return None


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.
    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    return runquery('INSERT INTO matches(winner, loser) VALUES(%s,%s);',
    False, params=(winner, loser))[0]


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
    results = runquery('''select p1.id, p1.name, p2.id, p2.name \
    from playerdetails p1 cross join playerdetails p2 where \
    (p1.id <> p2.id) AND (p1.id, p2.id) not in (select winner, loser \
    from matches)  AND (p2.id, p1.id) not in (select winner, loser from \
    matches) order by abs(p1.wins - p2.wins), p1.wins desc, p2.wins desc;'''
    , True)[1]
    pairs = []
    inpairs = set()
    for result in results:
        if result[0] in inpairs:
            continue
        pairs.append((result[0], result[1], result[2], result[3]))
        inpairs.add(result[0])
        inpairs.add(result[2])
    return pairs
