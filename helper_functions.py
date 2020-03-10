import warnings
warnings.filterwarnings('ignore')
import os
import requests
import pandas as pd
import psycopg2

DEBUG=0 #set to 1 for verbose output

connectionObj = psycopg2.connect(dbname = 'XXX',
                                 host = 'XXX',
                                 port = 'XXX',
                                 user = 'XXX',
                                 password = 'XXX')

connectionObj.autocommit=True

cursorObj = connectionObj.cursor()

def durationToSeconds(durationString):
    #return the total number of seconds from a duration text literal (i.e. 1:19 becomes 79)
    
    if durationString is not None and durationString != '':

        if durationString.split(':')[0] != '0':

            return (int(durationString.split(':')[0]) * 60) + int(durationString.split(':')[1])

        else:

            return int(durationString.split(':')[1])

    else:
        return 0
    
def dotZeroBugFix(dataFrame):
    #bugfix for pandas.write_csv issue with integer-ish values
    #see more here: https://github.com/tidyverse/readr/issues/526
    dataFrame=dataFrame.apply(str)
    dataFrame=dataFrame.str.split('.').str[0]
    return dataFrame.str.replace('nan','')

def runSQLFromFile(fileName):
	queryFileData=''
	
	with open(fileName, 'r') as queryFile:
		queryFileData+=queryFile.read()
	
	allQueries=queryFileData.split(';')
	
	for query in allQueries:
		
		query=query.strip()

		if any(char.isalpha() for char in query): #ignore empty queries
			executeSQL(query)
			
def executeSQL(query):

	if DEBUG:
		print(query)
		
	cursorObj.execute(query)
	connectionObj.commit()