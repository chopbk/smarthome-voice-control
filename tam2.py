import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from time import sleep

#define some pin numbers
pinLivingRoomLight = 17
pinKitchenLight = 27
pinBedRoomLight = 22

#we have to clean up to reset pin definitions
GPIO.cleanup()

#set the software to use the Broadcom numbers
GPIO.setmode(GPIO.BCM)
#set up the  pins definitions
GPIO.setup(pinLivingRoomLight,GPIO.OUT)
GPIO.setup(pinKitchenLight,GPIO.OUT)
GPIO.setup(pinBedRoomLight,GPIO.OUT)

def pinSet(pin, setLed):
	"""set pin number to given state"""
	GPIO.output(pin, setLed)
		
def pinRead(pin):
	"""Read pin number state"""
	return GPIO.input(pin)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/Living/Light")
    client.subscribe("/Kitchen/Light")
    client.subscribe("/Bedroom/Light")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))
	topic = str(msg.topic)
        if "/Living/Light" in topic:
                pin = pinLivingRoomLight
                if 'ON' in msg.payload:
                        pinSet(pin,True)
                if 'OFF' in msg.payload:
                        pinSet(pin,False)		
        elif "/Kitchen/Light" in topic:
                pin = pinKitchenLight
                if 'ON' in msg.payload:
                        pinSet(pin,True)
                if 'OFF' in msg.payload:
                        pinSet(pin,False)
        elif "/Bedroom/Light" in topic:
                pin = pinBedRoomLight
                if 'ON' in msg.payload:
                        pinSet(pin,True)
                if 'OFF' in msg.payload:
                        pinSet(pin,False)
	sleep(0.1)
	state = pinRead(pin)
	if state:
		sstate = 1
	else:
		sstate = 0
	client.publish(topic+"/state", sstate)

#def on_disconnect(client, userdata, rc):
#	if rc != 0:
#		pass
#	client.connect("10.0.0.16", 1883, 60)
	
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
#client.on_disconnect = on_disconnect

client.connect(host="192.168.100.20", port=1883, keepalive=60)

client.loop_forever()
