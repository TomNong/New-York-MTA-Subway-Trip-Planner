#**********************************************************************************************
# * Copyright (C) 2015-2016 Sareena Abdul Razak sta2378@columbia.edu
# * 
# * This file is part of New-York-MTA-Subway-Trip-Planner.
# * 
# * New-York-MTA-Subway-Trip-Planner can not be copied and/or distributed without the express
# * permission of Sareena Abdul Razak
# *********************************************************************************************
# This program reads raw data from the csv file and builds the model
# Usage python buildTrainingDataSet.py <csv file name with extension>
import sys

# Pandas is a python library used for data analysis
import pandas
from pandas import read_csv
from pytz import timezone
from datetime import datetime


TIMEZONE = timezone('America/New_York')


def main(fileHandle):
	# This creates a dataframe
	rawData = read_csv(fileHandle)

	# Remove duplicate entries based on tripId, retain the one with maximum timestamp
	data  =rawData.groupby('tripId').apply(lambda x: x.ix[x.timestamp.idxmax()])

	# Seperate all the local trains and form a new data frame
	localTrains = data[data.route == 'L']

	# Express trains
	expressTrains = data[data.route == 'E']

	# 1. Find the time difference (to reach 96th) between all combinations of local trains and express
	# 2. Consider only positive delta
	# 3. Make the final table

	# Create a new data frame for final table
	finalData = pandas.DataFrame()


	# Find the delta for all the values of expresstrains and local train time
	for index,row in localTrains.iterrows():

		# Create temporary storage for adding to finalData
		tempData = pandas.DataFrame()
		tempData['delta'] = expressTrains['timeToReachExpressStation'] - row['timeToReachExpressStation']

		# Drop all the rows with negative values
		# Resetting index to get rid of tripId - or else when we add it to tempData it is not going to duplicate
		tempData = tempData[tempData['delta'] >= 0]

		# Duplicate local express train time as many time as the positive delta values
		tempData['timeToReachExpressStation'] = [row['timeToReachExpressStation']]* tempData.shape[0]


		# Time at whcih local train reaches destination
		timeToReachDestination = row['timeToReachDestination']

		# Convert the time to seconds , value is between 0 - 24*60*60
		timeStampToDate = datetime.fromtimestamp(row['timeToReachExpressStation'],TIMEZONE)

		inSeconds = ( timeStampToDate.hour* 60 * 60 ) + ( timeStampToDate.minute * 60 ) + (timeStampToDate.second)
		
		# We shouldnt use timestamp value for timeToReachExpressStation to train model. Since it is a unique value
		# it doesnt add anything to the model. it is better to give time of day as a parameter
		tempData['time'] = inSeconds

		# Get the express train time to reach destination values
		# Here we are considering the time for express trains with positive delta values
		tempData['timeToReachDestination'] = expressTrains.ix[tempData.index]['timeToReachDestination']


		# If True = express reaches first, False = Local reaches first
		tempData['first'] = tempData['timeToReachDestination'] < row['timeToReachDestination'] 

		# We dont need time to reach destination anymore. so delete that column
		tempData.drop('timeToReachDestination',axis=1,inplace=True)

		#Drop timeToReachExpressStation 
		tempData.drop('timeToReachExpressStation',axis=1,inplace=True)

		# Replace True = Express= 0, False = Local =1
		# AML will take only 0 or 1 as labels
		tempData.replace(to_replace=[True,False],value=['0','1'],inplace=True)

		# reset index . right now index are tripIds of express trains. we want index as 0-N
		tempData.reset_index(drop=True,inplace=True)

		# day
		tempData['day'] = row['day']
		# Append it to final table
		finalData   =  finalData.append(tempData,ignore_index=True)

	
	finalData.to_csv("finalData.csv",index=False)



if __name__ == "__main__":

	lengthArg = len(sys.argv)


	if lengthArg < 2:
		print "Missing arguments"
		sys.exit(-1)

	if lengthArg > 2:
		print "Extra arguments"
		sys.exit(-1)
	
	fileHandle = sys.argv[1]
	main(fileHandle)