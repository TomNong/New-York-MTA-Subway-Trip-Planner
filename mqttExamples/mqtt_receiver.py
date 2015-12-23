import paho.mqtt.client as mqtt
import os
#This function makes the subscription to the Mqtt topic "sdkTest/sub"
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("sdkTest/sub")
 
#This function prints out the message received
def on_message(client, userdata, msg):
    print "Topic: ", msg.topic+'\nMessage: '+str(msg.payload)

def receive(): 
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
 
	#In the .tls_set, put the path of your rootCA key, certification key, and private key files, remain other parameters
	client.tls_set("/home/nongshibiao/Downloads/Shibiao/certs/rootCA.pem", "/home/nongshibiao/Downloads/Shibiao/certs/cert.pem", "/home/nongshibiao/Downloads/Shibiao/certs/privateKey.pem", tls_version=2, ciphers=None)
 
	#Connect to the domain of your thing, using port 8883
	client.connect("AA2MXZ7H1UWUJ.iot.us-east-1.amazonaws.com", 8883, 60)
 
	#Wait for the message
	client.loop_forever()

def main():
	newpid = os.fork()
	if newpid == 0:
		receive()

if __name__ == "__main__":
	main()
