#helper_functions.py imports all required libraries and sets up the connection to the database
#it also defines the connectionObj and cursorObj used for issuing SQL queries and ingesting results
#lastly it includes some utility functions used for handling data
from helper_functions import *

def main():

	fillGameSkaterStatesTable()
	
def getTotalPeriods(gameId):
	#returns the number of periods in a game. Overtime begins at period 4

    
    cursorObj.execute('''SELECT DISTINCT period FROM shifts WHERE gameId = '%s';''' % gameId)

    periodList = []

    for period in cursorObj.fetchall():
        periodList.append(period[0])

    return periodList
	
def getUnprocessedGameIds():
	#check the db for gameIds that have not yet had their skaterState table data generated
    
    cursorObj.execute('''
		SELECT DISTINCT gameId
		FROM shifts
		WHERE gameId NOT IN (SELECT DISTINCT gameId
							 FROM skaterStates);
    ''')
    
    gameIdList = []
    
    for game in cursorObj.fetchall():
        gameIdList.append(game[0])
        
    return gameIdList
	
def parseSkaterQueryResults(skaterResult):
    #takes the tuple from a psycopg2 query result and formats it into a dict
    #Query *MUST*, in this order, SELECT playerId, playerName, position, teamId, teamName, startTime, endTime, shiftId
    
    return {'playerId'    :    skaterResult[0],
            'playerName'  :    skaterResult[1],
            'position'    :    skaterResult[2],
            'teamId'      :    skaterResult[3],
            'teamName'    :    skaterResult[4],
            'startTime'   :    int(skaterResult[5]),
            'endTime'     :    int(skaterResult[6]),
            'shiftId'     :    skaterResult[7]}
    
def showSkaterState(skaterList):
    #show all skaters on the ice for a given skater state. Useful for debugging
    for skater in skaterList:
        print(skater['teamName'] + ' - ' + skater['playerName'])
        
    print('\n---\n')       
    
def getStrengthState(teamId, skaterList):
	#strength state from the perspective of our skater of interest.
	#i.e. 5v4 would be a power play and 4v5 would be a penalty kill
    
    friendlySkaterCount = 0 
    opposingSkaterCount = 0
    
    for skater in skaterList:
        
        if skater['teamId'] == teamId:
        
            friendlySkaterCount += 1
            
        else:
            
            opposingSkaterCount += 1
            
    return str(friendlySkaterCount) + 'v' + str(opposingSkaterCount)
	
def createSkaterChangeTimelineQuery(gameId, period):

	#this query will produce an ordered timeline of unique timestamps (in seconds)
	# of any personnel change on the ice, whether from shift changes, injuries, scoring plays or penalties

	return '''
	  WITH change_times AS (
		SELECT startTime AS skaterChangeTime
		FROM shifts
		INNER JOIN players
		ON shifts.playerId = players.playerId
		WHERE gameId = '%s'
		AND period = '%s'
		AND position != 'G'
		
		UNION
		
		SELECT endTime AS skaterChangeTime
		FROM shifts
		INNER JOIN players
		ON shifts.playerId = players.playerId
		WHERE gameId = '%s'
		AND period = '%s'
		AND position != 'G')
	  SELECT DISTINCT skaterChangeTime
	  FROM change_times
	  ORDER BY skaterChangeTime ASC;
	''' % (gameId, period, gameId, period)
	
def createSkatersEnteringGameQuery(gameId, period, startTime):
	#query to return player data for players coming onto the ice
	
	return '''
	SELECT shifts.playerId, shifts.playerName, players.position, shifts.teamId,
			shifts.teamName, shifts.startTime, shifts.endTime, shifts.shiftId
	FROM shifts
	INNER JOIN players
	ON shifts.playerId = players.playerId
	WHERE gameId = '%s'
	AND period = '%s'
	AND position != 'G'
	AND startTime = %s;
	''' % (gameId, period, startTime)
	
def createSkatersExitingGameQuery(gameId, period, startTime):
	#query to return player data for players coming off the ice
	
	return '''
	SELECT shifts.playerId, shifts.playerName, players.position, shifts.teamId,
			shifts.teamName, shifts.startTime, shifts.endTime, shifts.shiftId
	FROM shifts
	INNER JOIN players
	ON shifts.playerId = players.playerId
	WHERE gameId = '%s'
	AND period = '%s'
	AND position != 'G'
	AND endTime = %s;
	''' % (gameId, period, startTime)
	
def processSkaterStatesForGame(gameId):

	print(gameId)

	data = []

	for period in getTotalPeriods(gameId):

		print('period %s' % period)
	
		cursorObj.execute(createSkaterChangeTimelineQuery(gameId, period))

		subTimelineList = []

		for timestamp_seconds in cursorObj.fetchall():
			
			subTimelineList.append(timestamp_seconds[0])
			
		skatersOnIceList = []
		prevShiftStartTime = 0

		#need to rewrite this section to make one large query for line changes to improve performance
		for timestamp_seconds in subTimelineList:
			
			cursorObj.execute(createSkatersEnteringGameQuery(gameId, period, timestamp_seconds))
			
			for skater in cursorObj.fetchall():
				
				#add skaters who entered the game
				skatersOnIceList.append(parseSkaterQueryResults(skater))
			
			cursorObj.execute(createSkatersExitingGameQuery(gameId, period, timestamp_seconds))
			
			for skater in cursorObj.fetchall():
				
				#remove skaters that came off the ice
				skatersOnIceList = [skate for skate in skatersOnIceList if not (skate['playerId'] == parseSkaterQueryResults(skater)['playerId'])]

			if prevShiftStartTime != timestamp_seconds:
				#only record data if time has elapsed i.e. not the initial shift of a period

				for skater in skatersOnIceList:
					
					strengthState = getStrengthState(skater['teamId'], skatersOnIceList)
				
					otherSkaters = [skate for skate in skatersOnIceList if not (skate['playerId'] == skater['playerId'])]

					for otherSkater in otherSkaters:
						
						if skater['teamId'] != otherSkater['teamId']:
							
							data.append({'gameId'              :   gameId,
										 'shiftId'             :   skater['shiftId'],
										 'period'              :   period,
										 'playerId'            :   skater['playerId'],
										 'playerName'          :   skater['playerName'],
										 'position'            :   skater['position'],
										 'teamId'              :   skater['teamId'],
										 'teamName'            :   skater['teamName'],
										 'opposingPlayerId'    :   otherSkater['playerId'],
										 'opposingPlayerName'  :   otherSkater['playerName'],
										 'opposingPosition'    :   otherSkater['position'],
										 'opposingTeamId'      :   otherSkater['teamId'],
										 'opposingTeamName'    :   otherSkater['teamName'],
										 'iceTimeSeconds'      :   str(timestamp_seconds - prevShiftStartTime),
										 'strengthState'       :   strengthState})
				
			prevShiftStartTime = timestamp_seconds
			
			
	#load aggregated data into DataFrame
	df = pd.DataFrame(data)

	#enforce column ordering
	columnOrderList = ['gameId', 'shiftId', 'period', 'playerId', 'playerName', 'position', 'teamId', 'teamName', 'opposingPlayerId',
					   'opposingPlayerName', 'opposingPosition', 'opposingTeamId', 'opposingTeamName', 'iceTimeSeconds', 'strengthState']
	df = df[columnOrderList]

	#integer bug correction
	df['iceTimeSeconds'] = dotZeroBugFix(df['iceTimeSeconds'])

	#write DataFrame to CSV file
	df.to_csv('%s.csv' % gameId , index=False, sep = '|', header=False)

	#LOAD
	#load data into DB from CSV data file
	with open('%s.csv' % gameId, 'r') as csvData:
		cursorObj.copy_from(csvData, 'skaterStates', sep='|', null='')

	#clean up file
	os.remove('%s.csv' % gameId)

def fillGameSkaterStatesTable():
	
	for gameId in getUnprocessedGameIds():
	
		processSkaterStatesForGame(gameId)

if __name__ == '__main__':
	#if this script is being invoked explicitly from command line, run main() and execute.
	#if not, ignore and only import function definitions
    main()