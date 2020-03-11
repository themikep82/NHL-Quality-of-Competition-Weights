# NHL Quality of Competition Weights
 Simulates NHL shift changes and record player vs player TOI for QoC weighted averages

Quality of Competition is used in player modeling to account for the quality of opponents that a given player faces in game action. This is calculated as a weighted average of some opposing player quality variable weighted by the amount of time on the ice each opposing player is faced. A weighted average calculation is fairly simple, however, collecting the weights using line change data is an interesting and challenging technical problem. This repo is a solution to that problem.

This project solves it by first retreiving substitution and line change data from the NHL Stats API, cleaning it, loading it into a postgresql database on AWS, then stepping through every single player substitution and line change for a given game in chronological order and recording the combination of skaters on the ice for each event, plus the duration that these skaters were on the ice together. For the purposes of this project, I am calling that combination of skaters + duration a "skater state".

##Tableau Demo
Interactive Tableau Demo is available here: https://public.tableau.com/profile/mike.peterson3278#!/vizhome/QoCFrameworkDemo/KingsQoC-AveragePlusMinusofAllOpposingSkatersWeightedbyTimeonIcevsEachOpposingSkater

Demo uses plus/minus as the player quality metric. Obviously plus/minus is deeply flawed, but it was an easy accessible overall player statistic available on the NHL Stats API. If you have a database with better player metrics, like xGF% or some WAR-like metric keyed by NHLs 7-digit playerIds, it's a very simple join to replace plus/minus.

# File glossary

## populate_skater_states_table.py
The meat of this project is in this file. Contains all the logic to generate the weights needed for the weighted average calculation. Assumes raw data is already loaded into database. It works by essentially 'simulating' all player substitutions and line changes in chronological order and recording all the player combinations and durations on ice together in a table called 'skaterstates'. This is the table that can be queried for your Quality of Competition weights or calcs.

Example query:

    SELECT playerName, SUM((plusMinus * iceTimeSeconds)::DECIMAL) / SUM(iceTimeSeconds) AS qoc_plusMinus
    FROM skaterStates
    INNER JOIN playerStats
    ON skaterStates.opposingPlayerId = playerStats.playerId
    WHERE skaterStates.teamId = '26'
    GROUP BY playerId;

## master_data_load.py
First script to run if using a database with no data yet. This will run the table initializations SQL files which WILL drop existing tables if they already exists. Use caution.

## helper_functions.py
File used by all other python files to handle imports, database connection and other frequently used utilities.

## populate_shifts_table.py
Loads data into an already existing table called 'shifts'. If this table does not exist in your database, either run master_data_load.py or the shifts_table_init.sql file in your preferred DBMS.

## populate_games_table.py
Loads 2019-2020 NHL season schedule games in the an already existing table called 'games'. I'll make some updates where you can pass a season string (i.e. '20192020') into the script to specifiy the season whose games you want to load. Games data is not technically necessary for this project, but it is useful if you want to dimension Quality of Competetion by a range of dates, a specific opponent or home/away. If this table does not exist in your database, either run master_data_load.py or the games_table_init.sql file in your preferred DBMS.

## populate_players_table.py
Loads player data from the NHL Stats API into an already existing table called 'players'. If this table does not exist in your database, either run master_data_load.py or the players_table_init.sql file in your preferred DBMS. This script is dependent on the 'shifts' table already being loaded, as it starts by collecting all unique playerIds in 'shifts' to determine which player data to collect.

## populate_player_statstable.py
Not necessary to run this if you are just interested in the framework, but in order to test/demo, I needed some basic NHL player statistics. Loads some basic player stats in to an already existing table called 'playerstats'. If this table does not exist in your database, either run master_data_load.py or the playerstats_table_init.sql file in your preferred DBMS. Also requires an already existing 'players' data since it sources the playerIds for which to gather statistics from that table.

## \config_queries directory
Contains several queries to set up the required tables as well as setting primary keys, enforcing uniqueness constraints etc. Also contains shifts_table_remove_duplicate_shift_changes.sql file which is a necessary deduplication script because the NHL Stats API has some imperfect data -- identical shift change data rows keyed with unique shiftIds.
