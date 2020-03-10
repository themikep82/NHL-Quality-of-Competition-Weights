#helper_functions.py imports all required libraries and sets up the connection to the database
#it also defines the connectionObj and cursorObj used for issuing SQL queries and ingesting results
#lastly it includes some utility functions used for handling data
from helper_functions import *


def main():

	populatePlayerStatsTable()

def getPlayerStatsList():

	cursorObj.execute('SELECT playerId, position FROM players;')

	playerList = []

	for player in cursorObj.fetchall():
		playerList.append({'playerId' : player[0],
						  'position' : player[1]})
						  
	return playerList
						  
def populatePlayerStatsTable():

	data = []

	for player in getPlayerStatsList():

		URL = 'https://statsapi.web.nhl.com/api/v1/people/%s/stats?stats=statsSingleSeason&season=20192020' % player['playerId']

		jsonData = requests.get(url = URL).json()
		
		if player['position'] == 'G':
			
			data.append({'playerId'     :    player['playerId'],
						 'season'       :    jsonData['stats'][0]['splits'][0]['season'],
						 'shots'        :    None,
						 'goals'        :    None,
						 'assists'      :    None,
						 'points'       :    None,
						 'plusMinus'    :    None,
						 'shotsAgainst' :    jsonData['stats'][0]['splits'][0]['stat']['shotsAgainst'],
						 'saves'        :    jsonData['stats'][0]['splits'][0]['stat']['saves']
			})
			
		else:

			data.append({'playerId'     :    player['playerId'],
						 'season'       :    jsonData['stats'][0]['splits'][0]['season'],
						 'shots'        :    jsonData['stats'][0]['splits'][0]['stat']['shots'],
						 'goals'        :    jsonData['stats'][0]['splits'][0]['stat']['goals'],
						 'assists'      :    jsonData['stats'][0]['splits'][0]['stat']['assists'],
						 'points'       :    jsonData['stats'][0]['splits'][0]['stat']['points'],
						 'plusMinus'    :    jsonData['stats'][0]['splits'][0]['stat']['plusMinus'],
						 'shotsAgainst' :    None,
						 'saves'        :    None
			})

	df = pd.DataFrame(data)

	columnOrderList = ['playerId', 'season', 'shots', 'goals', 
					   'assists', 'points', 'plusMinus', 'shotsAgainst', 'saves']
	df = df[columnOrderList]


	df['shots'] = dotZeroBugFix(df['shots'])
	df['assists'] = dotZeroBugFix(df['assists'])
	df['goals'] = dotZeroBugFix(df['goals'])
	df['points'] = dotZeroBugFix(df['points'])
	df['plusMinus'] = dotZeroBugFix(df['plusMinus'])
	df['shotsAgainst'] = dotZeroBugFix(df['shotsAgainst'])
	df['saves'] = dotZeroBugFix(df['saves'])

	#write DataFrame to CSV file
	df.to_csv('playserStats.csv', index=False, sep = '|', header=False)

	#LOAD
	#load data into DB from CSV data file
	with open('playserStats.csv', 'r') as csvData:
		cursorObj.copy_from(csvData, 'playerstats', sep='|', null='')

	#clean up file
	os.remove('playserStats.csv')
	
if __name__ == '__main__':
	#if this script is being invoked explicitly from command line, run main() and execute.
	#if not, ignore and only import function definitions
    main()