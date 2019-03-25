from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import sys
import time
import json
import os
import RPi.GPIO as GPIO

# These are my AWS IoT login and certificates
host = "a3oosh7oql9nlc.iot.us-east-1.amazonaws.com"
cert_path = os.path.realpath(__file__).rstrip(os.path.basename(__file__)) + "cert/"
rootCAPath = cert_path + "root-CA.crt"
certificatePath = cert_path + "certificate.pem.crt"
privateKeyPath = cert_path + "private.pem.key"
shadowClient = "raspberry"
# These are my config GPIO
livingRoomLightPin = 17
bedRoomLightPin = 27
kitchenLightPin = 22
#status of Light
livingRoomLightStatus = ""
bedRoomLightStatus = ""
kitchenLightStatus = ""
# livingRoomLightStatus = ["", "ON", "OFF"]
# bedRoomLightStatus = ["", "ON", "OFF"]
# kitchenLightStatus = ["", "ON", "OFF"]
# livingRoomLight_Selected = livingRoomLightStatus.index("")
# bedRoomLight_Selected = bedRoomLightStatus.index("")
# kitchenRoomLight_Selected = kitchenRoomLightStatus.index("")

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
GPIO.setmode(GPIO.BCM)
GPIO.setup(livingRoomLightPin, GPIO.OUT)
GPIO.setup(bedRoomLightPin, GPIO.OUT)
GPIO.setup(kitchenLightPin, GPIO.OUT)
# Create a deviceShadow with persistent subscription
myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("raspberry", True)
#myDeviceShadow.shadowGet(IoTShadowCallback_Get, 5)

# Shadow callback for when a DELTA is received (this happens when Lamda does set a DESIRED value in IoT)
def IoTShadowCallback_Delta(payload, responseStatus, token):
#    global Power_StatusSelected, CoffeeChoice_Selected, RegularStrength_Selected, NumberOfCups_Selected
    print(responseStatus)
    payloadDict = json.loads(payload)
    print("++DELTA++ version: " + str(payloadDict["version"]))
    # Desired = LivingRoomLight change
    if ("LivingRoomLight" in payloadDict["state"]):
			print("LivingRoomLight: " + str(payloadDict["state"]["LivingRoomLight"]))
			changeLivingRoomLight(str(payloadDict["state"]["LivingRoomLight"]))
    # Desired = LivingRoomLight change
    if ("BedRoomLight" in payloadDict["state"]):
			print("BedRoomLight: " + str(payloadDict["state"]["BedRoomLight"]))
			changeBedRoomLight(str(payloadDict["state"]["BedRoomLight"]))
    # Desired = ActionTv change
    # if ("ActionTv" in payloadDict["state"]):
        # print("ActionTv: " + str(payloadDict["state"]["ActionTv"]))
        # changeLivingRoomLight(str(payloadDict["state"]["ActionTv"]))
    # Desired = KitchenLight selecction
    if ("KitchenLight" in payloadDict["state"]):
			print("KitchenLight: " + str(payloadDict["state"]["KitchenLight"]))
			changeKitchenLight(str(payloadDict["state"]["KitchenLight"]))
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
	
#call function when received delta LivingRoomLight		
def changeLivingRoomLight(ShadowPayload):
	if (ShadowPayload == "ON" ):
		print("OK")
		GPIO.output(livingRoomLightPin, True)
		reportToIoT()
	elif (ShadowPayload == "OFF" ):
		print("OK")
		GPIO.output(livingRoomLightPin, False)
		reportToIoT()
	else:
		print("NOT OK")


#call function when received delta LivingRoomLight		
def changeBedRoomLight(ShadowPayload):
	if (ShadowPayload == "ON" ):
		GPIO.output(bedRoomLightPin, True)
		reportToIoT()
	elif (ShadowPayload == "OFF" ):
		GPIO.output(bedRoomLightPin, False)
		reportToIoT()
	#Send the new status as REPORTED values
	# myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) 
 
#call function when received delta LivingRoomLight		
def changeKitchenLight(ShadowPayload):
	if (ShadowPayload == "ON" ):
		GPIO.output(kitchenLightPin, True)
		reportToIoT()
		# JSONPayload = '{ "state" : {'+\
						# '"reported": {'+\
							# '"KitchenLight": "' + ShadowPayload + '" '+\
						# '} '+\
					# '} '+\
				# '}'	
		# myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5)
	elif (ShadowPayload == "OFF" ):
		GPIO.output(kitchenLightPin, False)
		reportToIoT()
		# JSONPayload = '{ "state" : {'+\
						# '"reported": {'+\
							# '"KitchenLight": "' + ShadowPayload + '" '+\
						# '} '+\
					# '} '+\
				# '}'	
		# myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5)
		
	# myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) 
def reportToIoT():
	livingRoomLightState = GPIO.input(livingRoomLightPin)
	bedRoomLightState = GPIO.input(bedRoomLightPin)
	kitchenLightState = GPIO.input(kitchenLightPin)
	if(livingRoomLightState == GPIO.LOW):
		livingRoomLightStatus= "OFF"
	elif(livingRoomLightState == GPIO.HIGH):
		livingRoomLightStatus= "ON"
	else:
		livingRoomLightStatus=""
	if(bedRoomLightState == GPIO.LOW):
		bedRoomLightStatus = "OFF"
	elif(bedRoomLightState == GPIO.HIGH):
		bedRoomLightStatus = "ON"
	else:
		bedRoomLightStatus=""		
	if(kitchenLightState == GPIO.LOW):
		kitchenLightStatus = "OFF"
	elif(kitchenLightState == GPIO.HIGH):
		kitchenLightStatus = "ON"
	else:
		kitchenLightStatus=""
	JSONPayload = '{ "state" : {'+\
							'"reported": {'+\
								'"LivingRoomLight":"' +livingRoomLightStatus + '", '+\
								'"BedRoomLight": "' + bedRoomLightStatus + '", '+\
								'"KitchenLight": "' + kitchenLightStatus + '" '+\
							'} '+\
						'} '+\
					'}'	
	myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) 
reportToIoT()
myDeviceShadow.shadowRegisterDeltaCallback(IoTShadowCallback_Delta)
if __name__ == '__main__':
    try:
        print 'SmartHome started, Press Ctrl-C to quit.'
        while True:
			pass
    finally:
        GPIO.cleanup()
        myAWSIoTMQTTShadowClient.shadowUnregisterDeltaCallback()
        myAWSIoTMQTTShadowClient.disconnect()
        print 'SmartHome stopped.'
