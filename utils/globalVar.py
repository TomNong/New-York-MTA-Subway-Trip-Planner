import csv
import paho.mqtt.client as mqtt
import json
count = 0
formerStatus = 0
endFormerStatus = 0
startSingleTimeDataFeed = 0
endSingleTimeDataFeed = 0
date = []
localList = []
localEstimateEndTime = []
localArrivalTime = []
expList = []
expEstimateTime = []
expEstimateEndTime = []
deltaT = []


client = mqtt.Client()
client.tls_set("/home/nongshibiao/Downloads/Shibiao/certs/rootCA.pem", "/home/nongshibiao/Downloads/Shibiao/certs/cert.pem", "/home/nongshibiao/Downloads/Shibiao/certs/privateKey.pem", tls_version=2, ciphers=None)
client.connect("AA2MXZ7H1UWUJ.iot.us-east-1.amazonaws.com", 8883, 60)

class exEntity:
    def __init__(self, expTripID, prdArrivalTime):
        self.expTripID = expTripID
        self.prdArrivalTime = prdArrivalTime

def recordOnCsv(result):
    localList.pop(0)
    expList.pop(0)
    localArrivalTimeCp = localArrivalTime.pop(0)
    expEstimateTimeCp = expEstimateTime.pop(0)
    localEstimateEndTimeCp = localEstimateEndTime.pop(0)
    expEstimateEndTimeCp = expEstimateEndTime.pop(0)
    dateCp = date.pop(0)
    deltaTCp = deltaT.pop(0)
    data = [(localArrivalTimeCp, dateCp, deltaTCp, localEstimateEndTimeCp, expEstimateEndTimeCp, result)]
    csvfile = file('MtaLocalExpress.csv', 'a')
    writer = csv.writer(csvfile)
    writer.writerows(data)
    csvfile.close() 
    data = {}
    data = {"LocalTrainArrivalTime": localArrivalTimeCp, "Date": dateCp, "deltaT": deltaTCp, "LocalEstimateEndTime": localEstimateEndTimeCp, "ExpressTrainEstimateEndTime": expEstimateEndTimeCp, "Result": result}
    return data

