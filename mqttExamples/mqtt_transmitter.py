import paho.mqtt.client as mqtt
import time
client = mqtt.Client()
 
#in the .tls_set, put the path of your rootCA key, certification key, and private key files, remain other parameters
client.tls_set("/home/nongshibiao/Downloads/Shibiao/certs/rootCA.pem", "/home/nongshibiao/Downloads/Shibiao/certs/cert.pem", "/home/nongshibiao/Downloads/Shibiao/certs/privateKey.pem", tls_version=2, ciphers=None)
 
#Connect to the domain of your thing, using port 8883
client.connect("AA2MXZ7H1UWUJ.iot.us-east-1.amazonaws.com", 8883, 60)
#Need some time to connect
time.sleep(2)
#Publish "Hello, World!" to the topic "sdkTest/sub"
client.publish("sdkTest/sub", "Hello, World!")
