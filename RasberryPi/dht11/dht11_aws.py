import RPi.GPIO as GPIO
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import dht11_lib
import sys
import paho.mqtt.client as mqtt
import time
import datetime
import json
import os
import vlc
import subprocess
import alsaaudio, wave, numpy
pinButton = 20
p = ""
audioplaying = False
button_pressed = False
# These are my AWS IoT login and certificates
host = "a3oosh7oql9nlc.iot.us-east-1.amazonaws.com"
cert_path = os.path.realpath(__file__).rstrip(os.path.basename(__file__)) + "cert/"
rootCAPath = cert_path + "root-CA.crt"
certificatePath = cert_path + "certificate.pem.crt"
privateKeyPath = cert_path + "private.pem.key"
shadowClient = "raspberry"
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(pinButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#define some pin numbers
pinLivingRoomDht11 = 5
pinKitchenDht11 = 19
pinBedRoomDht11 = 6
#set up the  pins definitions
GPIO.setup(pinLivingRoomDht11,GPIO.IN)
GPIO.setup(pinKitchenDht11,GPIO.IN)
GPIO.setup(pinBedRoomDht11,GPIO.IN)
#define topic
topicLivingTemp = "/Living/Temperature"
topicLivingHumi = "/Living/Humidity"
topicBedRoomTemp = "/Bedroom/Temperature"
topicBedRoomHumi = "/Bedroom/Humidity"
topicKitchenTemp = "/Kitchen/Temperature"
topicKitchenHumi = "/Kitchen/Humidity"
def detect_button(channel):
    global button_pressed
    button_pressed = True
    time.sleep(.5) # time for the button input to settle down
    while (GPIO.input(pinButton)==0): #button seems to still be pressed
        button_pressed = True
        time.sleep(.1)
    button_pressed = False
    time.sleep(.5) # more time for the button to settle down
# Shadow callback for updating the AWS IoT
def IoTShadowCallback_Update(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("++UPDATE++ request " + token + " timed out!")
    if responseStatus == "accepted":
         payloadDict = json.loads(payload)
         print("++UPDATE++ request with token: " + token + " accepted!")
         if ("desired" in payloadDict["state"]):
             print("Desired: " + str(payloadDict["state"]["desired"]))
         if ("reported" in payloadDict["state"]):
             print("Reported: " + str(payloadDict["state"]["reported"]))
    if responseStatus == "rejected":
        print("++UPDATE++ request " + token + " rejected!")
def play_audio(file, offset=0, overRideVolume=0):
    # global currVolume
    global p, audioplaying
    k = file.rfind("/") #find the start of the filename from the full path
    new_file = file[k+1:] #filname only
    i = vlc.Instance('--aout=alsa') # , '--alsa-audio-device=mono', '--file-logging', '--logfile=vlc-log.txt')
    m = i.media_new(file)
    p = i.media_player_new()
    p.set_media(m)
    mm = m.event_manager()
    mm.event_attach(vlc.EventType.MediaStateChanged, state_callback, p)
    audioplaying = True
    if (overRideVolume == 0):
        p.audio_set_volume(100)
    else:
        p.audio_set_volume(overRideVolume)
    p.play()
    while audioplaying:
        if button_pressed:
            p.stop()
	else: 
            continue		
def state_callback(event, player):
    global nav_token, audioplaying, streamurl, streamid
    state = player.get_state()
    #0: 'NothingSpecial'    #1: 'Opening'     #2: 'Buffering'
    #3: 'Playing'                   #4: 'Paused'       #5: 'Stopped'
    #6: 'Ended'             #7: 'Error'

    if state == 5:    #Stopped
        audioplaying = False
    elif state == 6:    #Ended
        audioplaying = False
    elif state == 7:
        audioplaying = False
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
# read data using pin 14
LivingRoomDht11 = dht11_lib.DHT11(pin=pinLivingRoomDht11)
BedRoomDht11 = dht11_lib.DHT11(pin=pinBedRoomDht11)
KitchenDht11 = dht11_lib.DHT11(pin=pinKitchenDht11)
client = mqtt.Client()
client.on_connect = on_connect
client.connect(host="192.168.100.20", port=1883, keepalive=60)

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(shadowClient)
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec
# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()
# Create a deviceShadow with persistent subscription
myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("raspberry", True)
GPIO.add_event_detect(pinButton, GPIO.FALLING, callback=detect_button, bouncetime=100) # threaded detection of button press
while True:
    resultLivingRoomDht11 = LivingRoomDht11.read()
    if resultLivingRoomDht11.is_valid():
        print ("Phong khac"+str(resultLivingRoomDht11.temperature))
        resultBedRoomDht11 = BedRoomDht11.read()
        client.publish(topicLivingTemp,resultLivingRoomDht11.temperature)
        client.publish(topicLivingHumi,resultLivingRoomDht11.humidity)
        print ("Phong ngu"+str(resultBedRoomDht11.temperature))
        if resultBedRoomDht11.is_valid():
			resultKitchenDht11 = KitchenDht11.read()
			client.publish(topicBedRoomTemp,resultBedRoomDht11.temperature)
			client.publish(topicBedRoomHumi,resultBedRoomDht11.humidity)
			
			if resultKitchenDht11.is_valid():
                                print ("Phong bep"+str(resultKitchenDht11.temperature))
				client.publish(topicKitchenTemp,resultKitchenDht11.temperature)
				client.publish(topicKitchenHumi,resultKitchenDht11.humidity)
				JSONPayload = '{ "state" : {'+\
                                                            '"reported": {'+\
                                                                            '"LivingRoomTemp":"' +str(resultLivingRoomDht11.temperature)+ '", '+\
                                                                            '"LivingRoomHumi": "' + str(resultLivingRoomDht11.humidity) + '", '+\
                                                                            '"KitchenRoomTemp":"' +str(resultKitchenDht11.temperature)+ '", '+\
                                                                            '"KitchenRoomHumi": "' + str(resultKitchenDht11.humidity) + '", '+\
                                                                            '"BedRoomTemp":"' +str(resultBedRoomDht11.temperature)+ '", '+\
                                                                            '"BedRoomHumi": "' + str(resultBedRoomDht11.humidity) + '" '+\
                                                            '} '+\
                                            '} '+\
								'}'	
				myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update,  5)
				if resultBedRoomDht11.temperature > 50 or resultKitchenDht11.temperature > 50  or resultLivingRoomDht11.temperature > 50 : 
					play_audio(path+"warning.mp3")
          
    time.sleep(10)


	

    
