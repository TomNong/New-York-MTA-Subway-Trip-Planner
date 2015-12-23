import pexpect
import sys
import time
import json
import os
import thread
import datetime
import configure
import boto3


class wicedsense:
    # Init function to connect to wiced sense using mac address
    # Blue tooth address is obtained from blescan.py
    def __init__( self, bluetooth_adr ):
        self.con = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' --interactive')
        self.con.expect('\[LE\]>', timeout=3)
        print "Preparing to connect. You might need to press the side button..."
        self.con.sendline('connect')
        # test for success of connect
        self.con.expect('Connection successful.*\[LE\]>', timeout = 5)
        print "Connection successful"
        self.cb = {}
        # Data from sensors
        self.accelerometer = []
        self.gyroscope = []
        self.magnetometer=[]
        self.humidity = 0
        self.temperature = 0
        self.pressure = 0
        return
    # Function to write a value to a particular handle
    def char_write_cmd( self, handle, value ):
        cmd = 'char-write-req 0x%02x 0%x' % (handle, value)
        #print cmd
        self.con.sendline(cmd)
        self.con.expect('Notification handle = 0x002a value: 34 .*? \r',
timeout = 5)
        after = self.con.after
        rval = after.split()[5:]
        self.processdata(rval)
        return
    # Funcrion to read from a handle
    def char_read_hnd(self, handle):
        self.con.sendline('char-read-hnd 0x%02x' % handle)
        self.con.expect('descriptor: .*? \r', timeout = 60)
        after = self.con.after
        rval = after.split()[1:]
        #print rval
        # decode data obtained from the sensor tag
        self.processdata(rval)
    def processdata(self,data):
        # This is to decode and get sensor data from the packets we received
        # please refer to the broadcom data packet format document to understan the data
        data_decode = ''.join(data)
        print data_decode
        mask = int(data_decode[0:2],16)
        if(mask==0x0b):
            self.accelerometer.append(int((data_decode[4:6] + data_decode[2:4]), 16))
            self.accelerometer.append(int((data_decode[8:10] + data_decode[6:8]), 16))
            self.accelerometer.append(int((data_decode[12:14] + data_decode[10:12]), 16))
            self.gyroscope.append(int((data_decode[16:18] + data_decode[14:16]), 16))
            self.gyroscope.append(int((data_decode[20:22] + data_decode[18:20]), 16))
            self.gyroscope.append(int((data_decode[24:26] + data_decode[22:24]), 16))
            self.magnetometer.append(int((data_decode[28:30] + data_decode[26:28]), 16))
            self.magnetometer.append(int((data_decode[32:34] + data_decode[30:32]), 16))
        else:
            self.humidity = int((data_decode[4:6] + data_decode[2:4]),16)/10
            self.pressure = int((data_decode[8:10] + data_decode[6:8]),16)/10
            self.temperature = int((data_decode[12:14] + data_decode[10:12]),16)/10
    def disconnect(self):
        self.con.sendline('disconnect')
        self.con.sendline('quit')
DATA = ''
def snsNotificate(threadName, interval):
    try:
        snsClient = boto3.client(service_name="sns",
            aws_access_key_id=configure.AWS_ACCESS_KEY,
            aws_secret_access_key=configure.AWS_SECRET_ACCESS_KEY,
            region_name=configure.AWS_REGION, use_ssl=True)
        while True:
            time.sleep(interval)
            if DATA == '':
                continue
            response = snsClient.publish(
                TopicArn=configure.topicArn,
                Message=DATA
            )
    except:
        print('sns exception')
try:
   thread.start_new_thread( snsNotificate, ("Thread-sns", 1800,) )
except:
   print "Error: unable to start thread"

while True:
    macList = []
    child = pexpect.run('hciconfig hci0 down')
    child = pexpect.run('hciconfig hci0 up')
    detectCount = 0
    connCount = 0
    body = {}
    child = pexpect.spawn('hcitool lescan')
    time.sleep(5)
    child.expect('.+')
    #print(child.after)
    split = child.after.split()
    for tmp in range(0, len(split)):
        if split[tmp] == 'WICED':
            detectCount += 1
            macList.append(split[tmp - 1])
    for tmp in range(0, len(macList)):
        try:
            tag = wicedsense(macList[tmp])
            connCount += 1
            data = {}
            tag.char_write_cmd(0x2b,0x01)
            # Print the data
            ts = time.time()
            tn = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            data = {'Temperature': tag.temperature, 'Humidity':
tag.humidity, 'Pressure': tag.pressure, 'Updated at': tn}
            body[connCount] = data
            DATA = json.dumps(data)
            print tag.temperature
            print tag.humidity
            print tag.pressure
            tag.disconnect()
        except pexpect.TIMEOUT:
            continue
    print(DATA)
