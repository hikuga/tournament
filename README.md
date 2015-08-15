# tournament
swiss tournament pairing.
This module generates a list of pairings for various players entered in a tournament. To pair players
it uses swiss pairing algorithm. To simulate a real tournament rounds each of the parings must be 
entered as a reported match to advance to the next round.

Dependencies:
postgre psql version > 9.0
psycopg2

To run, load tournament.sql into database(\i tournament.sql on psql command prompt) to create tables and import module tournament in your python file or shell.
Follow the documentation in the module to invoke various functions on the database.
