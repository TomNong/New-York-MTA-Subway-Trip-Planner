#**********************************************************************************************
# * Copyright (C) 2015-2016 Sareena Abdul Razak sta2378@columbia.edu
# * 
# * This file is part of New-York-MTA-Subway-Trip-Planner.
# * 
# * New-York-MTA-Subway-Trip-Planner can not be copied and/or distributed without the express
# * permission of Sareena Abdul Razak
# *********************************************************************************************
# Program to update dynamodb with latest data from mta feed. It also cleans up stale entried from db
# Usage python dynamodata.py

import json,time,sys
from collections import OrderedDict
from threading import Thread

import boto3
from boto3.dynamodb.conditions import Key,Attr

sys.path.append('../utils')
import tripupdate,vehicle,alert,mtaUpdates,aws

DYNAMODB_TABLE_NAME = "mtaData"
COGNITO_ID = "EdisonApp"

def updateDb(APIKEY,dynamoTable):
    while True:
        # Create an object of type mtaUpdates
        mta = mtaUpdates.mtaUpdates(APIKEY)
        tripUpdates = mta.getTripUpdates()

        writeData(tripUpdates,dynamoTable)
        time.sleep(33)


# Method to write to Dynamo DB
def writeData(tripUpdates,dynamoTable):
    for trip in tripUpdates:
        data = createData(trip)
        dynamoTable.put_item(Item=data)


# Method to create the data to be written into dynamo db
def createData(trip):
    data = OrderedDict()
    timestamp = time.time()
    if trip.vehicleData:
        data = {"tripId":trip.tripId, "routeId":trip.routeId, \
                "startDate":trip.startDate, "direction":trip.direction, \
                "currentStopId":int(trip.vehicleData.currentStopId[:-1]), \
                "currentStopStatus":trip.vehicleData.currentStopStatus, "vehicleTimeStamp":trip.vehicleData.timestamp, \
                "futureStopData" : json.dumps(trip.futureStops),
                "timestamp": str(timestamp)}
    else:
        # If there is no vehicle assigned, it is at the start station
        currentStopId = trip.futureStops.keys()[0]
        data = {"tripId":trip.tripId, "routeId":trip.routeId, \
                    "startDate":trip.startDate, "direction":trip.direction, \
                    "currentStopId": int(currentStopId[:-1]), \
                    "currentStopStatus":"NODATA", "vehicleTimeStamp":"NODATA", \
                    "futureStopData" : json.dumps(trip.futureStops), \
                    "timestamp":str(timestamp)}
    return data

def deleteOldEntries(dynamoTable):
    # delete entries that hasnt been updated in 2 minutes
    timeNow = str(time.time() - 120)
    response = dynamoTable.scan(FilterExpression=Attr('timestamp').lte(timeNow))
    for items in response['Items']:
        dynamoTable.delete_item(Key={'tripId':items['tripId']})

def cleanUpDb(dynamoTable):
    while True:
        print ">cleaning up"
        deleteOldEntries(dynamoTable)
        time.sleep(60)


# Two threads running : update DB thread updates dynamo db every 30 seconds
#                     : clean up DB thread cleans up stale entries every 60 seconds
def main():
    with open('../../key.txt', 'rb') as keyfile:
        APIKEY = keyfile.read().rstrip('\n')
        keyfile.close()



    dynamodb = aws.getResource('dynamodb','us-east-1')
    dynamoTable = dynamodb.Table(DYNAMODB_TABLE_NAME)

     # Thread 1 check update dynamo db
    updateDbThread = Thread(target = updateDb, name = 'updateDb',args=(APIKEY,dynamoTable))

    # Thread 2 send clean up old dynamodb entries
    cleanUpDbThread = Thread(target = cleanUpDb, name = 'cleanUpDb',args=(dynamoTable,))

    updateDbThread.daemon = True
    cleanUpDbThread.daemon = True

    # Start all the threads
    updateDbThread.start()

    # Start clean up after 2 minutes
    # if you start clean up db thread right away, you get an error since 
    # udpate db thread hasnt finished writing to dynamodb
    # use only when you start with empty table
    #time.sleep(120)
    cleanUpDbThread.start()


    # Join threads
    updateDbThread.join()    
    cleanUpDbThread.join()
    

        # check how if there are any 2 or
if __name__ == "__main__":
    main()

    """def writeAlertData(self):	
	    for a in self.alerts:
            for trip in a.tripId:
                if trip and a.routeId[trip] and a.alertMessage:
    	             self.dynamoTable.put_item(Item={"tripId":trip, "routeId":a.routeId[trip],\
    				     "currentStop": "NOTAPPLICABLE","type":"ALERT", \
    				     "metaData":"{\"message\" : \"" + str(a.alertMessage) +"}"})"""							
