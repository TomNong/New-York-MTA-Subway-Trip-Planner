import gtfs_realtime_pb2, nyct_subway_pb2
import urllib2, contextlib, datetime, copy
from operator import itemgetter
from pytz import timezone
import threading, time
import csv, math, json
import logging
import google.protobuf.message
import json
import paho.mqtt.client as mqtt
import globalVar
import operator
import csv
import time
#This class use the Mta real-time data feeds to build a .csv file for machine learning, 
#heads for the .csv file are the arrival time of 1 train at 96th Street, the date, the
#delta T(how long would be the next 2 or 3 train arrive), 1 train's estimated time 
#arrive at 34th street, next 2 or 3 train 's estimated time arrive at 34th street, which
#of them arrive first

class buildCSV(object):
    def __init__(self, mtaDataEntity):
        self.mtaDataEntity = mtaDataEntity
    def recordData(self):
            #time
            globalVar.startSingleTimeDataFeed = time.clock()    
            for entity in self.mtaDataEntity:             
                if entity.vehicle and entity.vehicle.trip.trip_id:
                    #to find the time and the local train that arrival 120S(96th st) 
                    if str(entity.vehicle.trip.route_id) == '1' and str(entity.vehicle.stop_id) == '120S':
                        #if now the current status is "stop"
                        if entity.vehicle.current_status == 1:
                            if globalVar.formerStatus != 1:
                                print('Arrival at ' + str(entity.vehicle.timestamp))
                                #get the trip ID of th local train that just arrived
                                globalVar.localList.append(entity.vehicle.trip.trip_id)
                                globalVar.localArrivalTime.append(entity.vehicle.timestamp)
                                globalVar.date.append(entity.vehicle.trip.start_date)
                                #to find the next express train
                                expEntityList = []
                                expTrains = filter(lambda expEntity: expEntity.trip_update.trip.route_id == '2' or expEntity.trip_update.trip.route_id == '3', self.mtaDataEntity)
                                #expStopTimeUpdate = [x.trip_update.stop_time_update for x in expTrains]
                                for expEntity in expTrains:
                                    expUpdate = next((x for x in expEntity.trip_update.stop_time_update if x.stop_id == '120S'), None)
                                    if expUpdate != None:
                                        expEntityList.append(globalVar.exEntity(expEntity.trip_update.trip.trip_id, expUpdate.arrival.time))
                                        print('found a express')
                                    
                                
                                if expEntityList != []:
                                    expEntityList = sorted(expEntityList, key = operator.attrgetter('prdArrivalTime'))
                                    #get the next express train information 
                                    globalVar.expList.append(expEntityList[0].expTripID)
                                    globalVar.expEstimateTime.append(expEntityList[0].prdArrivalTime)
                                    globalVar.deltaT.append(expEntityList[0].prdArrivalTime - entity.vehicle.timestamp)
                                    #find the estimate time of the local and express train reaching 34st
                                    localTrainInMeasured = filter(lambda tmpEntity: tmpEntity.trip_update.trip.trip_id == entity.vehicle.trip.trip_id, self.mtaDataEntity)[0]
                                    localStopUpdate = filter(lambda tmpUpdate: tmpUpdate.stop_id == '128S', localTrainInMeasured.trip_update.stop_time_update)[0]
                                    globalVar.localEstimateEndTime.append(localStopUpdate.arrival.time)
                                    expressTrainInMeasured = filter(lambda tmpEntity: tmpEntity.trip_update.trip.trip_id == expEntityList[0].expTripID, self.mtaDataEntity)[0]
                                    expressStopUpdate = filter(lambda tmpUpdate: tmpUpdate.stop_id == '128S', expressTrainInMeasured.trip_update.stop_time_update)[0]
                                    globalVar.expEstimateEndTime.append(expressStopUpdate.arrival.time)
                                else:
                                    globalVar.localList.pop(0)
                                    globalVar.localArrivalTime.pop(0)
                                    globalVar.date.pop(0)                                   
                        globalVar.formerStatus = entity.vehicle.current_status
                        
                if entity.vehicle and entity.vehicle.trip.trip_id:
                    if entity.vehicle.stop_id == '128S' and entity.vehicle.current_status == 1 and globalVar.localList != [] and globalVar.expList != []:
                        print("arrival " + str(entity.vehicle.trip.trip_id) + ' ' + entity.vehicle.stop_id)
                        print(globalVar.localList[0])
                        print(globalVar.expList[0])
                        if str(entity.vehicle.trip.trip_id) == str(globalVar.localList[0]):
                            print('local arrival first')
                            result = 1
                            data = globalVar.recordOnCsv(result)
                            globalVar.client.publish("sdkTest/sub", json.dumps(data))
                            print(data)
                        elif str(entity.vehicle.trip.trip_id) == str(globalVar.expList[0]):
                            print('express arrival first')
                            result = 0
                            data = globalVar.recordOnCsv(result)
                            globalVar.client.publish("sdkTest/sub", json.dumps(data))
                            print(data)
                    #globalVar.endFormerStatus = entity.vehicle.current_status        
                        
            #if the update is not received, in case that the arrival can never be measured, clean it up when the number of tripIDs exceeds 4
            print(len(globalVar.localList))
            globalVar.endSingleTimeDataFeed = time.clock()
            print("runing time for all updates " + str(globalVar.endSingleTimeDataFeed - globalVar.startSingleTimeDataFeed))
            if len(globalVar.localList) >= 4:
                globalVar.date = []
                globalVar.localList = []
                globalVar.localEstimateEndTime = []
                globalVar.localArrivalTime = []
                globalVar.expList = []
                globalVar.expEstimateTime = []
                globalVar.expEstimateEndTime = []
                globalVar.deltaT = []
    
