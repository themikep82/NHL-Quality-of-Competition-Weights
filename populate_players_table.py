#helper_functions.py imports all required libraries and sets up the connection to the database
#it also defines the connectionObj and cursorObj used for issuing SQL queries and ingesting results
#lastly it includes some utility functions used for handling data
from helper_functions import *


def main():
	populatePlayersTable()

def getPlayerIds():

	cursorObj.execute('SELECT DISTINCT playerid FROM shifts;')

	playerIdList = []

	for player in cursorObj.fetchall():
		playerIdList.append(player[0])
		
	return playerIdList
	
def populatePlayersTable():

	data = []

	for playerId in getPlayerIds():

		URL = 'https://statsapi.web.nhl.com/api/v1/people/%s' % playerId

		jsonData = requests.get(url = URL).json()
		
		if 'currentTeam' in jsonData['people'][0]:
		#check if current team data exists
		#emergency goalies have no associated team and break the script if it is not accounted for
		
			data.append({'playerId'    :  playerId,
						 'playerName'  :  jsonData['people'][0]['fullName'],
						 'dateOfBirth' :  jsonData['people'][0]['birthDate'],
						 'position'    :  jsonData['people'][0]['primaryPosition']['abbreviation'],
						 'teamId'      :  jsonData['people'][0]['currentTeam']['id'],
						 'teamName'    :  jsonData['people'][0]['currentTeam']['name']
			})
			
		else:
			
			data.append({'playerId'    :  playerId,
						 'playerName'  :  jsonData['people'][0]['fullName'],
						 'dateOfBirth' :  jsonData['people'][0]['birthDate'],
						 'position'    :  jsonData['people'][0]['primaryPosition']['abbreviation'],
						 'teamId'      :  None,
						 'teamName'    :  None
			})

	df = pd.DataFrame(data)

	columnOrderList = ['playerId', 'playerName', 'dateOfBirth', 'position', 'teamId', 'teamName']
	df = df[columnOrderList]

	df['teamId'] = dotZeroBugFix(df['teamId'])

	#write DataFrame to CSV file
	df.to_csv('playerData.csv', index=False, sep = '|', header=False)

	#LOAD
	#load data into DB from CSV data file
	with open('playerData.csv', 'r') as csvData:
		cursorObj.copy_from(csvData, 'players', sep='|', null='')

	#clean up file
	os.remove('playerData.csv')
	
if __name__ == '__main__':
	#if this script is being invoked explicitly from command line, run main() and execute.
	#if not, ignore and only import function definitions
    main()