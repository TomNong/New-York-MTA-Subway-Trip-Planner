#**********************************************************************************************
# * Copyright (C) 2015-2016 Sareena Abdul Razak sta2378@columbia.edu
# * 
# * This file is part of New-York-MTA-Subway-Trip-Planner.
# * 
# * New-York-MTA-Subway-Trip-Planner can not be copied and/or distributed without the express
# * permission of Sareena Abdul Razak
# *********************************************************************************************

import time,csv,sys
from pytz import timezone
from datetime import datetime

sys.path.append('../utils')
import mtaUpdates

# usage python gatherData.py <file_name> <optional iterations>
# 
# This script should be run seperately before we start using the application
# Purpose of this script is to gather enough data to build a training model for Amazon machine learning
# Each time you run the script it gathers data from the feed and writes to a file
# You can specify how many iterations you want the code to run. Default is 50
# This program only collects data. Sometimes you get multiple entries for the same tripId. we can timestamp the 
# entry so that when we clean up data we use the latest entry

# Change DAY to the day given in the feed
DAY = datetime.today().strftime("%A")
TIMEZONE = timezone('America/New_York')

global ITERATIONS

#Default number of iterations
ITERATIONS = 50

# column headers for the csv file
columns =['timestamp','tripId','route','day','timeToReachExpressStation','timeToReachDestination']

DEBUG = False

def getTimeToReachDestination(localTrain,destination):
    # get time at which this train reaches destinatiob  station
    stopData = localTrain.futureStops
    timeToReachExpressStation = stopData[destination][0]
    return timeToReachExpressStation    

def main(fileName):
    # API key
    with open('../../key.txt', 'rb') as keyfile:
        APIKEY = keyfile.read().rstrip('\n')
        keyfile.close()


    data = []

    iteration = 0
    while iteration < ITERATIONS:
	    iteration = iteration +  1


	    # Create an object of type mtaUpdates
	    mta = mtaUpdates.mtaUpdates(APIKEY)
	    tripUpdates = mta.getTripUpdates()

	    # Filter out the trains with no vehicle data and trains going North
	    # These are tentative trips and sometimes it gets cancelled
	    trips = [trip for trip in tripUpdates if trip.vehicleData is not None and trip.direction=='S']

	    # List of trains with route id = 1 and are either at 116th station or before it
	    localTrains = [lcl for lcl in trips if lcl.routeId == '1' and int(lcl.vehicleData.currentStopId[:-1]) <= 120] 

	    # List of trains with route id 2 and are either at 96th or before it
	    # Note that 2 train's stop starts from 201S and goes till 227S and merges with 96th street(120S)
	    # range2 is a list of all stations on 2 train route before and including 96th
	    range2 = range(201,228)
	    range2.append(120)

	    expressTrains2 = [exp2 for exp2 in trips if exp2.routeId == '2' and int(exp2.vehicleData.currentStopId[:-1]) in range2]

		# List of trains with route id 3 and are either at 96th or before it
	    # Note that 3 train's stop starts from 301S and goes till 302S and merges with 2 train lane at 135th street lenox 224S 
	    # range3 is a list of all stations on 3 train route before and including 96th
	    range3 = range(224,228)
	    range3.extend([301,302,120])
	    expressTrains3 = [exp3 for exp3 in trips if exp3.routeId == '3' and int(exp3.vehicleData.currentStopId[:-1]) in range3]

	    expressTrains = expressTrains2 + expressTrains3

	    if DEBUG:
			print "$$$@$@$$$$$$ iteration : %d $$#$@^$#$" %iteration
			print "current time : ",time.time()
			print "local"
			for e in localTrains:
				print e.tripId + " : " + e.vehicleData.currentStopId + " : " + e.vehicleData.currentStopStatus + " reaching 42 at : " + str(getTimeToReachDestination(e,'127S'))
			print "expressTrains"
			for l in expressTrains:
				print l.tripId + " : " + l.vehicleData.currentStopId + " : " + l.vehicleData.currentStopStatus +  " reaching 42 at : " + str(getTimeToReachDestination(l,'127S'))


		# Here we are just collecting data. So we blindly copy all the items from the filtered list
	    # Note that there might be multiple entries for the same tripId, but we will have another method 
	    # to clean up data

	    for l in localTrains:
			item = {}
			item['tripId'] = l.tripId
			item['timeToReachExpressStation'] = getTimeToReachDestination(l,'120S')
			# L for local trains
			item['route'] = 'L'
			item['timeToReachDestination'] = getTimeToReachDestination(l,'127S')
			item['timestamp'] = time.time()
			item['day'] = DAY
			data.append(item)

	    for e in expressTrains:
			item = {}
			item['tripId'] = e.tripId
			item['timeToReachExpressStation'] = getTimeToReachDestination(e,'120S')
			# E for express trains
			item['route'] = 'E'
			item['timeToReachDestination'] = getTimeToReachDestination(e,'127S')
			item['timestamp'] = time.time()
			item['day'] = DAY
			data.append(item)

		# A new feed is generated every 30 seconds
	    time.sleep(40)


	# if the file name given by user doesn't have .csv extension , add it
    if '.csv' not in fileName:
    	fileName = fileName + '.csv'

    # write data to file
    with open(fileName ,'wb') as f:

    	w = csv.DictWriter(f,columns)
    	w.writeheader()
    	w.writerows(data)
    	f.close()


if __name__ == "__main__":

	lengthArg = len(sys.argv)


	if lengthArg < 2:
		print "Missing arguments"
		sys.exit(-1)

	if lengthArg > 3:
		print "Extra arguments"
		sys.exit(-1)
	
	fileHandle = sys.argv[1]

	if lengthArg == 3:
		ITERATIONS = int(sys.argv[2])



	main(fileHandle)


