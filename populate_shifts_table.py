#helper_functions.py imports all required libraries and sets up the connection to the database
#it also defines the connectionObj and cursorObj used for issuing SQL queries and ingesting results
#lastly it includes some utility functions used for handling data
from helper_functions import *


def main():
	
	importShiftChartsFromList(collectGameIds('20192020'))

def collectGameIds(seasonString):
	
	#Collect 20192020 gameIds and store them in a list
	jsonData = requests.get(url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate=2019-10-01&endDate=2020-04-05').json()

	gameIdList = []

	for date in jsonData['dates']:
		
		for game in date['games']:
			
			gameIdList.append(game['gamePk'])
			
	return gameIdList
	
	
def importShiftChartsFromList(gameIdList):

	#get all 20192020 NHL shift data
	for gameId in gameIdList:
		
		#EXTRACT
		URL = "https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId=%s" % gameId

		#submit request to NHL REST API and collect JSON game data
		jsonData = requests.get(url = URL).json()

		#TRANSFORM
		#separate and flatten JSON data into a flat CSV for DB consumption

		if jsonData['total'] > 0:

			data = []

			for shift in jsonData['data']:            

				if shift['playerId'] is not None and shift['typeCode'] == 517:
				
					data.append({'gameId'             : shift['gameId'],
								 'shiftId'            : shift['id'],
								 'typeCode'           : shift['typeCode'],
								 'eventDescription'   : shift['eventDescription'],
								 'shiftNumber'        : shift['shiftNumber'],
								 'teamId'             : shift['teamId'],
								 'duration'           : durationToSeconds(shift['duration']),
								 'eventNumber'        : shift['eventNumber'],
								 'homeTeamId'         : shift['homeTeamId'],
								 'teamName'           : shift['teamName'],
								 'period'             : shift['period'],
								 'playerName'         : shift['firstName'] + ' ' + shift['lastName'],
								 'detailCode'         : shift['detailCode'],
								 'eventDetails'       : shift['eventDetails'],
								 'visitingTeamId'     : shift['visitingTeamId'],
								 'teamAbbrev'         : shift['teamAbbrev'],
								 'playerId'           : shift['playerId'],
								 'endTime'            : durationToSeconds(shift['endTime']),
								 'startTime'          : durationToSeconds(shift['startTime'])                

							 })

			#load aggregated data into DataFrame
			df = pd.DataFrame(data)

			#enforce column ordering
			columnOrderList = ['gameId', 'shiftId', 'typeCode', 'eventDescription', 'shiftNumber', 'teamId', 'duration',
							   'eventNumber', 'homeTeamId', 'teamName', 'period', 'playerName', 'detailCode', 'eventDetails',
							   'visitingTeamId', 'teamAbbrev', 'playerId', 'startTime', 'endTime']
			df = df[columnOrderList]

			#integer bug correction
			df['eventNumber'] = dotZeroBugFix(df['eventNumber'])

			#write DataFrame to CSV file
			df.to_csv('%s.csv' % gameId , index=False, sep = '|', header=False)



			#back up CSV to S3
			#S3upload('%s.csv' % gameId, S3_KEY_NAME, S3_BUCKET)

			#LOAD
			#load data into DB from CSV data file
			with open('%s.csv' % gameId, 'r') as csvData:
				cursorObj.copy_from(csvData, 'shifts', sep='|', null='')

			#clean up file
			os.remove('%s.csv' % gameId)
			
	#clean up data in database
	#shifts API sometimes sends duplicate shift change data keyed with unique shift_ids.
	#they must be removed with some deduplication SQL
	script_dir = os.path.dirname(__file__)
	runSQLFromFile(os.path.join(script_dir, 'config_queries/shifts_table_remove_duplicate_shift_changes.sql'))
	
	#also remove spurious 0 duration events (penalty shots I think?)
	cursorObj.execute('DELETE FROM shifts WHERE duration = 0;')
			
if __name__ == '__main__':
	#if this script is being invoked explicitly from command line, run main() and execute.
	#if not, ignore and only import function definitions
    main()