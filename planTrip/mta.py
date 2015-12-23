#**********************************************************************************************
# * Copyright (C) 2015-2016 Sareena Abdul Razak sta2378@columbia.edu
# * 
# * This file is part of New-York-MTA-Subway-Trip-Planner.
# * 
# * New-York-MTA-Subway-Trip-Planner can not be copied and/or distributed without the express
# * permission of Sareena Abdul Razak
# *********************************************************************************************
# Usage python mta.py

import json,time,csv,sys
from threading import Thread

import boto3
from boto3.dynamodb.conditions import Key,Attr

sys.path.append('../utils')
import aws


DYNAMODB_TABLE_NAME = "mtaData"
# prompt
def prompt():
    print ""
    print ">Available Commands are : "
    print "1. plan trip"
    print "2. send me list of options for the trip"
    print "3. exit"  

def buildStationssDB():
    stations = []
    with open('stops.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            stations.append(row[0])
    return stations

# Method to get all local going in a given direction on a give routeId and havent passed sourceStopId
def getLocalTrains(table,direction,routeId,sourceStopId):
    response = table.scan(FilterExpression=Attr('direction').eq(direction) & \
                              Attr('routeId').eq(routeId) & \
                              Attr('currentStopId').lte(sourceStopId))
    return response['Items']

# Method to get all express going in a given direction on a give routeId and are at given list of stops
def getExpress(table,direction,routeId,stops):
    response = table.scan(FilterExpression=Attr('direction').eq(direction) & \
                          Attr('currentStopId').is_in(stops) & \
                          Attr('routeId').eq(routeId))
    return response['Items']

# Method to get the earliest train's data
def getEarliestTrain(response,destination):
    # Remove the vehicles with currentStopStatus  = NODATA, that means the trip hasnt started
    movingVehicles =[items for items in response if items['currentStopStatus']!='NODATA']
    
    # If there are no moving trains, use the original list
    if not movingVehicles:
        movingVehicles = response
  
    arrivalTimes = {}
    for v in movingVehicles:
        stops = json.loads(v['futureStopData'])
        arrivalTimes[v['tripId']] = stops[destination][0]['arrivalTime']
    
    # now we have the earliest arriving 1 train
    earliestTrain = min(arrivalTimes, key=arrivalTimes.get)
     
    # get the data for earliestTrain
    trainData = next((train for train in movingVehicles if train['tripId'] == earliestTrain),None) 
    return trainData

def getTimeToReachDestination(trainData,destination):

    # get time at which this train reaches destination
    stopData = json.loads(trainData['futureStopData'])
    timeToReachExpressStation = stopData[destination][0]['arrivalTime']
    return timeToReachExpressStation    





def main():
    dynamodb = aws.getResource('dynamodb','us-east-1')
    snsClient = aws.getClient('sns','us-east-1')
    snsResource = aws.getResource('sns','us-east-1')
    
    dynamoTable = dynamodb.Table(DYNAMODB_TABLE_NAME)

    # Get list of all stopIds
    stations = buildStationssDB()


    while True:
        prompt()
        sys.stdout.write(">select a command : ")
        userIn = sys.stdin.readline().strip()
        if len(userIn) < 1 :
            print "Command not recognized"
        else:
            if userIn == '1':
                sys.stdout.write(">Enter source : ")
                sourceStop = sys.stdin.readline().strip()
                if sourceStop not in stations:
                    sys.stdout.write(">Invalid stop id. Enter a valid stop id")
                    sys.stdout.flush()
                    continue

                sys.stdout.write(">Enter destination : ")
                destinationStop = sys.stdin.readline().strip()
                if destinationStop not in stations:
                    sys.stdout.write(">Invalid stop id. Enter a valid stop id")
                    sys.stdout.flush()
                    continue

                sys.stdout.write(">Type N for uptown, S for downtown: ")
                direction = sys.stdin.readline().strip()

                # Validate direction
                if direction not in ['N','S']:
                    sys.stdout.write(">Invalid direction. Enter a valid direction")
                    sys.stdout.flush()
                    continue

                response = getLocalTrains(dynamoTable,direction,'1',int(sourceStop[:-1]))

                earliestTrainData = getEarliestTrain(response,sourceStop)

                print "local train is ",earliestTrainData['tripId']
                timeToReachExpressStation = getTimeToReachDestination(earliestTrainData,'120S')


                # get list of 2 and 3 trains 

                # List of trains with route id 2 and are either at 96th or before it
                # Note that 2 train's stop starts from 201S and goes till 227S and merges with 96th street(120S)
                # range2 is a list of all stations on 2 train route before and including 96th
                range2 = range(201,228)
                range2.append(120)

                expressTrains2 = getExpress(dynamoTable,direction,'2',range2)

                # List of trains with route id 3 and are either at 96th or before it
                # Note that 3 train's stop starts from 301S and goes till 302S and merges with 2 train lane at 135th street lenox 224S 
                # range3 is a list of all stations on 3 train route before and including 96th
                range3 = range(224,228)
                range3.extend([301,302,120])
                expressTrains3 = getExpress(dynamoTable,direction,'3',range3)

                expressTrains = expressTrains2 + expressTrains3

                # filter the trains that reach 96th before the earliest one reaches.
                for e in expressTrains:
                    stops = json.loads(e['futureStopData'])
                    if stops['120S'][0]['arrivalTime'] - timeToReachExpressStation < 10:
                        expressTrains.remove(e)

                timeTakenByLocal    = getTimeToReachDestination(earliestTrainData,destinationStop)

                print "time taken by local to 96",timeToReachExpressStation
                # If there is an express train find the time at which it reaches time square
                if expressTrains:
                    expressTrainData = getEarliestTrain(expressTrains,'120S')
                    print expressTrainData['tripId']

                    print "time taken by express to 96",getTimeToReachDestination(expressTrainData,'120S')


                    timeTakenByExpress  = getTimeToReachDestination(expressTrainData,destinationStop)
                    timeTakenByLocal    = getTimeToReachDestination(earliestTrainData,destinationStop)
                    print "time taken by local to 42nd",timeTakenByLocal
                    print "Time taken by expres to 42nd",timeTakenByExpress

                    if timeTakenByLocal > timeTakenByExpress:
                        print ">Switch to express"
                    else:
                        print ">Do not switch to express"
                else:
                    print "No express at this time"
                    print ">Do not switch to express"

            elif userIn == '2':
                sys.stdout.write(">Enter phonenumber")
                phoneNumber = sys.stdin.readline().strip()
                phoneNumber = '1'+phoneNumber                

                topic = snsResource.Topic('arn:aws:sns:us-east-1:013162866752:mtaSub')
                topic.subscribe(Protocol='sms', 
                                 Endpoint=phoneNumber)

                snsClient.publish(TopicArn='arn:aws:sns:us-east-1:013162866752:mtaSub', 
                                          Message='You have subscribed to mta data',
                                          Subject='MTAFEED')


            else:
                sys.exit()

	

        # check how if there are any 2 or
if __name__ == "__main__":
    main()
    

   

        