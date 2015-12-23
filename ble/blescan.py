import subprocess,raspberryPiData,senseDevice,time,sys
from threading import Thread
import json
import httplib

RSSITHRESHOLD = 15
TIMEOUT  = 5
# Create an object called raspberrypiData
rpiData = raspberryPiData.raspberryPiData(RSSITHRESHOLD,TIMEOUT)
baseUrl = "api.parse.com"

# Thread to scan the ble devices 
def lescan():
	# Subprocess is a python library to start a process
	# Call hci0 down followed by hci0 up to bring down and bring up the hci0 (bluetooth) interface
	subprocess.call(["sudo","hciconfig","hci0","down"])
	subprocess.call(["sudo","hciconfig","hci0","up"])

	# Start a process to scan for bluetooth low energy devices , command is sudo hcitool lescan 
	# stdout option is set to subprocess.PIPE so that we can read the values printed on the command line 
	bleScanProcess = subprocess.Popen(['sudo','hcitool', 'lescan'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	for line in bleScanProcess.stdout:
		lineData = line.strip("\n")
		name = lineData.split(' ',1)[1]
		bdAddr = lineData.split(' ')[0]
		if(name == "WICED Sense Kit"):
			senseObj = rpiData.getSenseObject(bdAddr)
			if not senseObj:
				newSenseObj = senseDevice.senseDevice()
				newSenseObj.bluetoothAddress = bdAddr
				newSenseObj.timeStamp = time.time()
				rpiData.devices.append(newSenseObj)
				rpiData.count += 1
	print "exitted"


def getRSSI():

	print "RSSI thread started"
	bleDumpProcess = subprocess.Popen(['sudo','hcidump'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while True:
		check = False
		address = None
		senseObj = None
		rssi = None

		for line in bleDumpProcess.stdout:
			data =  line.strip()
			if 'bdaddr' in line:
				address = data.split(' ')[1]
				continue

			if check and senseObj:
				if 'RSSI' in line:
					rssi = line.split(':')[1].strip()
					print rssi
					connection = httplib.HTTPSConnection(baseUrl, 443)
					connection.connect()
					connection.request('PUT', '/1/classes/Sense/vKNRTX3CT3', json.dumps({
       "RSSI": int(rssi),
     }), {
       "X-Parse-Application-Id": "kayWALfBm6h1SQdANXoZtTZqA0N9sZsB7cwUUVod",
       "X-Parse-REST-API-Key": "pCtDSSXbhSuufcTpLz4a9Xfr2C5ImRfSyWQESBYH",
       "Content-Type": "application/json"
     })
					senseObj.rssi = rssi
	     			check = False
	     			address = None
	     			senseObj = None
	     			continue

			if 'WICED Sense Kit' in line:
				senseObj =rpiData.getSenseObject(address)
				if(senseObj):
					senseObj.timeStamp = time.time()
					check = True
					continue
				

def userInput():
	while True:
		userIn = sys.stdin.readline().strip()
		if len(userIn) < 1 :
			print "Enter a correct command"
		else:
			if userIn == "CLOSE":
			    break
			else:
			    command = userIn.split(' ')[0]
			    print command    
		sys.exit()

def handleTimeOut():
	while True:
		# Check if 3 * timeout has passed for each neighbors
	    for sense in rpiData.devices:
	    	if((time.time()-sense.timeStamp) > rpiData.timeOutValue):
	        	print "timedout\n"
	        	rpiData.devices.remove(sense)
	        	rpiData.count -=1

if __name__ == "__main__":


	# Thread 1 listen for events on localPort
    scanThread = Thread(target = lescan, name = 'lescan')

    # Thread 2 send data on localPort
    timeOutThread = Thread(target = handleTimeOut, name = 'timeout')

    # Thread 3  user input thread 
    userInputThread = Thread(target = userInput, name = 'userInput')

    # Thread to get RSSI value
    getRSSIThread    = Thread(target = getRSSI , name = 'rssi')



    scanThread.daemon = True
    timeOutThread.daemon = True
    userInputThread.daemon = True
    getRSSIThread.daemon = True
    
    # Start all the threads
    scanThread.start()
    timeOutThread.start()
    userInputThread.start()
    getRSSIThread.start()

    # Join Threads
    userInputThread.join()
    quit()
    scanThread.join()
    timeOutThread.join()
    getRSSIThread.join()


	


