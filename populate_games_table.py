#helper_functions.py imports all required libraries and sets up the connection to the database
#it also defines the connectionObj and cursorObj used for issuing SQL queries and ingesting results
#lastly it includes some utility functions used for handling data
from helper_functions import *

def main():

	populateGamesTable()
	
	
def populateGamesTable():

	#Collect 20192020 gameIds and store them in a list
	jsonData = requests.get(url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate=2019-10-01&endDate=2020-04-05').json()


	data = []

	for date in jsonData['dates']:
		
		for game in date['games']:
			
			
			data.append({'gameId'        : game['gamePk'],
						 'gameDate'      : game['gameDate'],
						 'season'        : game['season'],
						 'homeTeamId'    : game['teams']['home']['team']['id'],
						 'homeTeamName'  : game['teams']['home']['team']['name'],
						 'awayTeamId'    : game['teams']['away']['team']['id'],
						 'awayTeamName'  : game['teams']['away']['team']['name'],
						 'statusCode'    : game['status']['statusCode'],
						 'detailedState' : game['status']['detailedState']
			})
			
	df = pd.DataFrame(data)

	columnOrderList = ['gameId', 'gameDate', 'season', 'homeTeamId', 'homeTeamName', 
					   'awayTeamId', 'awayTeamName', 'statusCode', 'detailedState']
	df = df[columnOrderList]

	#write DataFrame to CSV file
	df.to_csv('gamesData.csv', index=False, sep = '|', header=False)

	#LOAD
	#load data into DB from CSV data file
	with open('gamesData.csv', 'r') as csvData:
		cursorObj.copy_from(csvData, 'games', sep='|', null='')

	#clean up file
	os.remove('gamesData.csv')
	
if __name__ == '__main__':
	#if this script is being invoked explicitly from command line, run main() and execute.
	#if not, ignore and only import function definitions
    main()