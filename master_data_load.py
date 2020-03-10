#helper_functions.py imports all required libraries and sets up the connection to the database
#it also defines the connectionObj and cursorObj used for issuing SQL queries and ingesting results
#lastly it includes some utility functions used for handling data
import datetime
from helper_functions import *
from populate_shifts_table import *
from populate_games_table import *
from populate_players_table import *
from populate_playerstats_table import *

def main():

	print('data load starting: %s' % datetime.datetime.now())

	script_dir = os.path.dirname(__file__)
	
	#set up and create shifts table
	runSQLFromFile(os.path.join(script_dir, 'config_queries/shifts_table_init.sql'))
	importShiftChartsFromList(collectGameIds('20192020'))
	
	runSQLFromFile(os.path.join(script_dir, 'config_queries/games_table_init.sql'))
	populateGamesTable()
	
	runSQLFromFile(os.path.join(script_dir, 'config_queries/players_table_init.sql'))
	populatePlayersTable()
	
	runSQLFromFile(os.path.join(script_dir, 'config_queries/playerstats_table_init.sql'))
	populatePlayerStatsTable()
	
	print('data load complete: %s' % datetime.datetime.now())

if __name__ == '__main__':
	#if this script is being invoked explicitly from command line, run main() and execute.
	#if not, ignore and only import function definitions
    main()