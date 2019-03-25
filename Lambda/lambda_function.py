from __future__ import print_function
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import datetime
import json
import time

# These are my AWS IoT login and certificates
host = "a3oosh7oql9nlc.iot.us-east-1.amazonaws.com"
cert_path = "cert/"
rootCAPath = cert_path + "root-CA.crt"
certificatePath = cert_path + "certificate.pem.crt"
privateKeyPath = cert_path + "private.pem.key"
shadowName = "raspberry"
LivingRoomLightStatus = ""
BedRoomLightStatus = ""
KitchenLightStatus = ""
LivingRoomHumi = ""
BedRoomHumi = ""
KitchenHumi = ""
LivingRoomTemp = ""
BedRoomTemp = ""
KitchenTemp = ""
GetStatus = ""
def lambda_handler(event, context):
    global myAWSIoTMQTTShadowClient, myDeviceShadow
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    #print ('RECEIVED EVENT: ' + json.dumps(event, separators=(',', ':')))
    if 'session' in event:
        print("event.session.application.applicationId=" + event['session']['application']['applicationId'])
        """
        Uncomment this if statement and populate with your skill's application ID to
        prevent someone else from configuring a skill that sends requests to this
        function.
        """
        # if (event['session']['application']['applicationId'] !=
        #     "amzn1.ask.skill.b2d37e60-ecae-4beb-aed0-adf69fe456a4"):
        #     raise ValueError("Invalid Application ID")
        if event['session']['new'] and 'requestId' in event['request']:
            on_session_started({'requestId': event['request']['requestId']},event['session'])
        if 'request' in event:
            # Init AWSIoTMQTTClient
            myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(shadowName+"_Lambda_"+event['request']['requestId'][-12:])
            myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
            myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

            # AWSIoTMQTTClient connection configuration
            myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
            myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
            myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec
            # Connect to AWS IoT Shadow
            myAWSIoTMQTTShadowClient.connect()
            myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(shadowName, True)
            myDeviceShadow.shadowGet(IoTShadowCallback_Get,5)
            # JSONPayload = '{ "state" : {'+\
						# '"desired": {'+\
							# '"LivingRoomLight":"", '+\
							# '"BedRoomLight": "", '+\
							# '"KitchenLight": "" '+\
						# '} '+\
					# '} '+\
				# '}'	
            # myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) 
            while GetStatus == "":
                ready = ""
            if event['request']['type'] == "LaunchRequest":
                return on_launch(event['request'], event['session'])
            elif event['request']['type'] == "IntentRequest":
                return on_intent(event['request'], event['session'])
            elif event['request']['type'] == "SessionEndedRequest":
                return on_session_ended(event['request'], event['session'])
def on_session_started(session_started_request, session):
    """ Called when the session starts """
    #print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])
def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want """
    #print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    intent = launch_request
    return Welcome_response(intent, session)
def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    # Dispatch to your skill's intent handlers
    if intent_name == "WelcomeIntent":
        return Welcome_response(intent, session)
    elif intent_name == "LivingRoomLightIntent":
        return LivingRoomLight_response(intent, session)
    elif intent_name == "BedRoomLightIntent":
        return BedRoomLight_response(intent, session)
    elif intent_name == "KitchenLightIntent":
        return KitchenLight_response(intent, session)
    elif intent_name == "TvIntent":
        return ActionTv_response(intent, session)
    elif intent_name == "EnvironmentIntent":
        return EnvironmentIntent_response(intent, session)
    elif intent_name == "YesIntent":
        return YesIntent_response(intent, session)
    elif intent_name == "NoIntent":
        return NoIntent_response(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return Stop_response()
    elif intent_name == "HelpIntent":
        return Help_response()
    elif intent_name == "AMAZON.HelpIntent":
        return Help_response()
    else:
        raise ValueError("Invalid intent")
def on_session_ended(session_ended_request, session):
    return Stop_response()
# Shadow callback for updating the AWS IoT
def IoTShadowCallback_Update(payload, responseStatus, token):
    print("IoT update response: " + responseStatus.upper())
def IoTShadowCallback_Get(payload, responseStatus, token):
    global LivingRoomLightStatus
    global BedRoomLightStatus
    global KitchenLightStatus, LivingRoomHumi, LivingRoomTemp, KitchenTemp, KitchenHumi
    global GetStatus
    GetStatus =  responseStatus
    payloadDict = json.loads(payload)
    LivingRoomHumi = str(payloadDict["state"]["reported"]["LivingRoomHumi"])
    print(LivingRoomHumi)
    LivingRoomTemp = str(payloadDict["state"]["reported"]["LivingRoomTemp"])
    print(LivingRoomTemp)
    KitchenTemp = str(payloadDict["state"]["reported"]["KitchenRoomTemp"])
    KitchenHumi = str(payloadDict["state"]["reported"]["KitchenRoomHumi"])
    print("LivingRoomLight: " + str(payloadDict["state"]["reported"]["LivingRoomLight"]))
    LivingRoomLightStatus = str(payloadDict["state"]["reported"]["LivingRoomLight"])
    print("BedRoomLightStatus: " + str(payloadDict["state"]["desired"]["BedRoomLight"]))
    BedRoomLightStatus = str(payloadDict["state"]["reported"]["BedRoomLight"])
    print("KitchenLightStatus: " + str(payloadDict["state"]["desired"]["KitchenLight"]))
    KitchenLightStatus = str(payloadDict["state"]["reported"]["KitchenLight"])
##    BedRoomHumi = str(payloadDict["state"]["reported"]["LivingRoomHumi"])
##    BedRoomTemp = str(payloadDict["state"]["reported"]["KitchenLight"])

# --------------- Functions that control the skill's behavior ------------------
def Welcome_response(intent, session):
    # Set Session Attributes
    LivingRoomLight = ''
    BedRoomLight = ''
    ActionTv = ''
    # Set other defaults
    card_title = "Welcome"
    should_end_session = False
    # Start the real task
    currentTime = datetime.datetime.now()
    if currentTime.hour < 6:
        printTime = "morning"
    elif 6 <= currentTime.hour < 11:
        printTime = "afternoon"
    else:
        printTime = "evening"
    
    speech_output = "Good " + printTime + ", welcome to Smart Home Control " \
                    "What action do you want?"
    reprompt_text = "What kind action do you want? " \
                    "I ready for command"
   # Send response back to the Alexa Voice Skill
    session_attributes = create_attributes(LivingRoomLight,BedRoomLight,ActionTv)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def LivingRoomLight_response(intent, session):
    global LivingRoomLightStatus
    # Set Session Attributes
    LivingRoomLight = ''
    BedRoomLight = ''
    ActionTv = ''
    if 'attributes' in session:
        if 'LivingRoomLight' in session['attributes']:
            LivingRoomLight = session['attributes']['LivingRoomLight']
        else:
            LivingRoomLight = ''
    else:
		LivingRoomLight = ''
		BedRoomLight = ''
		ActionTv = ''
    # Set other defaults
    card_title = "LivingRoomLight"
    should_end_session = False
    
    speech_output = "I didn't understand your commands" \
                    "Please repeat again"
    reprompt_text = "Please repeat again"
    
    # Start the real task
    if 'slots' in intent:
        if 'LivingRoomLight' in intent['slots']:
            if 'value' in intent['slots']['LivingRoomLight']:
                LivingRoomLight = intent['slots']['LivingRoomLight']['value'].upper()
                if(LivingRoomLightStatus == LivingRoomLight):
                    speech_output = "Your Living Room Light already turn " + LivingRoomLight + " . " \
                                        "Did you want another commands"
                    reprompt_text = "I am ready for new command?"
                else:
                    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"LivingRoomLight\": \"" + LivingRoomLight + "\""\
                                                "} "\
                                    "} "\
                    "}"
                    myDeviceShadow.shadowUpdate(myJSONPayload, IoTShadowCallback_Update, 5)
                    if (LivingRoomLight == "ON" ):
                        LivingRoomLight = 'ON'
                        speech_output = "Your Living Room Light will be turn " + LivingRoomLight + " . " \
                                        "Did you want another commands"
                        reprompt_text = "I am ready for new command?"
                        LivingRoomLightStatus = "ON"
                    # Publish to AWS IoT Shadow
                    elif (LivingRoomLight == "OFF"):
                        LivingRoomLight = 'OFF'
                        speech_output = "Your Living Room Light will be turn " + LivingRoomLight + " . " \
                                        "Did you want another commands"
                        reprompt_text = "I am ready for new command?"
                        LivingRoomLightStatus = "OFF"

	
        

    #print ('UPLOADED TO IoT: ' + json.dumps(json.loads(myJSONPayload), separators=(',', ':')))
    session_attributes = create_attributes(LivingRoomLight,BedRoomLight,ActionTv)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def BedRoomLight_response(intent, session):
    global BedRoomLightStatus
    # Set Session Attributes
    LivingRoomLight = ''
    BedRoomLight = ''
    ActionTv = ''
    if 'attributes' in session:
        if 'BedRoomLight' in session['attributes']:
            BedRoomLight = session['attributes']['BedRoomLight']
        else:
            BedRoomLight = ''
    else:
		LivingRoomLight = ''
		BedRoomLight = ''
		ActionTv = ''

    # Set other defaults
    card_title = "BedRoomLight"
    should_end_session = False
    
    speech_output = "I didn't understand your commands" \
                    "Please repeat again"
    reprompt_text = "Please repeat again"

    # Start the real task
    if 'slots' in intent:
        if 'BedRoomLight' in intent['slots']:
            if 'value' in intent['slots']['BedRoomLight']:
                BedRoomLight = intent['slots']['BedRoomLight']['value'].upper()
                print("BedRoomLightStatus"+BedRoomLightStatus)
                if(BedRoomLightStatus == BedRoomLight):
                    speech_output = "Your bedroom light already turn " + BedRoomLight + " . " \
                                        "Did you want another commands"
                    reprompt_text = "I am ready for new command?"
                else:
                    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"BedRoomLight\": \"" + BedRoomLight + "\""\
                                                "} "\
                                    "} "\
                    "}"
                    myDeviceShadow.shadowUpdate(myJSONPayload, IoTShadowCallback_Update, 5)
                    if (BedRoomLight == "ON" ):
                        BedRoomLight = 'ON'
                        speech_output = "Your BedRoom Light will be turn " + BedRoomLight + " . " \
                                        "Did you want another commands"
                        reprompt_text = "I am ready for new command?"
                        BedRoomLightStatus = "ON"
                    # Publish to AWS IoT Shadow
                    elif (BedRoomLight == "OFF"):
                        BedRoomLight = 'OFF'
                        speech_output = "Your BedRoomLight will be turn " + BedRoomLight + " . " \
                                        "Did you want another commands"
                        reprompt_text = "I am ready for new command?"	 
                        BedRoomLightStatus = "OFF"
    #print ('UPLOADED TO IoT: ' + json.dumps(json.loads(myJSONPayload), separators=(',', ':')))
    session_attributes = create_attributes(LivingRoomLight,BedRoomLight,ActionTv)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def KitchenLight_response(intent, session):
    global KitchenLightStatus
    # Set Session Attributes
    LivingRoomLight = ''
    BedRoomLight = ''
    ActionTv = ''
    if 'attributes' in session:
        if 'KitchenLight' in session['attributes']:
            KitchenLight = session['attributes']['KitchenLight']
        else:
            KitchenLight = ''
    else:
		LivingRoomLight = ''
		BedRoomLight = ''
		ActionTv = ''

    # Set other defaults
    card_title = "KitchenLight"
    should_end_session = False
    
    speech_output = "I didn't understand your commands" \
                    "Please repeat again"
    reprompt_text = "Please repeat again"

    # Start the real task
    if 'slots' in intent:
        if 'KitchenLight' in intent['slots']:
            if 'value' in intent['slots']['KitchenLight']:
                KitchenLight = intent['slots']['KitchenLight']['value'].upper()
                if(KitchenLightStatus == KitchenLight):
                    speech_output = "Your Kitchen Light  already turn " + KitchenLight + " . " \
                                        "Did you want another commands"
                    reprompt_text = "I am ready for new command?"
                else:
                    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"KitchenLight\": \"" + KitchenLight + "\""\
                                                "} "\
                                    "} "\
                    "}"
                    myDeviceShadow.shadowUpdate(myJSONPayload, IoTShadowCallback_Update, 5)
                    if (KitchenLight == "ON" ):
                        KitchenLight = 'ON'
                        speech_output = "Your Kitchen Light will be turn " + KitchenLight + " . " \
                                        "Did you want another commands"
                        reprompt_text = "I am ready for new command?"
                        KitchenLightStatus = "ON"
                    # Publish to AWS IoT Shadow
                    elif (KitchenLight == "OFF"):
                        KitchenLight = 'OFF'
                        speech_output = "Your Kitchen Light will be turn " + KitchenLight + " . " \
                                        "Did you want another commands"
                        reprompt_text = "I am ready for new command?"	  
                        KitchenLightStatus = "OFF"
	
    #print ('UPLOADED TO IoT: ' + json.dumps(json.loads(myJSONPayload), separators=(',', ':')))
    session_attributes = create_attributes(LivingRoomLight,BedRoomLight,ActionTv)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def ActionTv_response(intent, session):
    # Set Session Attributes
    LivingRoomLight = ''
    BedRoomLight = ''
    ActionTv = ''
    if 'attributes' in session:
        if 'ActionTv' in session['attributes']:
            ActionTv = session['attributes']['ActionTv']
        else:
            ActionTv = ''
    else:
		LivingRoomLight = ''
		BedRoomLight = ''
		ActionTv = ''

    # Set other defaults
    card_title = "ActionTv"
    should_end_session = False
    
    speech_output = "I didn't understand your commands" \
                    "Please repeat again"
    reprompt_text = "Please repeat again"

    # Start the real task
    if 'slots' in intent:
        if 'ActionTv' in intent['slots']:
            if 'value' in intent['slots']['ActionTv']:
                ActionTv = intent['slots']['ActionTv']['value'].upper()

                if (ActionTv == "ON" ):
                    speech_output = "Okey, Turn " + ActionTv + " your Tv "                     
                elif (ActionTv == "OFF"):
                    speech_output = "Okey, Turn " + ActionTv + " your Tv "
                elif (ActionTv == "CHANNEL UP"):
                    speech_output = "Okey, " + ActionTv + " your Tv "
                elif (ActionTv == "CHANNEL DOWN"):
                    speech_output = "Okey," + ActionTv + " your Tv "
                elif (ActionTv == "VOLUME UP"):
                    speech_output = "Okey, " + ActionTv + " your Tv 5 unit "
                elif (ActionTv == "VOLUME DOWN"):
                    speech_output = "Okey," + ActionTv + " your Tv 5 unit "
					
  	myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"ActionTv\": \"" + ActionTv + "\""\
                                                "} "\
                                    "} "\
                    "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, IoTShadowCallback_Update, 5)
    #print ('UPLOADED TO IoT: ' + json.dumps(json.loads(myJSONPayload), separators=(',', ':')))
# 	if statusLivingRoomLight == LivingRoomLight
# 		print("OK")
# 	else 
# 	    print("Not OK")
    # Send response back to the Alexa Voice Skill
    session_attributes = create_attributes(LivingRoomLight,BedRoomLight,ActionTv)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def EnvironmentIntent_response(intent, session):
    # Set other defaults
    card_title = "Room"
    should_end_session = False
    
    speech_output = "I didn't understand your commands" \
                    "Please repeat again"
    reprompt_text = "Please repeat again"
    
    # Start the real task
    if 'slots' in intent:
        if 'Room' in intent['slots']:
            if 'value' in intent['slots']['Room']:
                Room = intent['slots']['Room']['value'].upper()
    if 'slots' in intent:
        if 'Room' in intent['slots']:
            if 'value' in intent['slots']['Room']:
                Room = intent['slots']['Room']['value'].upper()
                if("LIVING ROOM" == Room):
                    speech_output = "Temperature is " + str(LivingRoomTemp) + ".   Humidity is "+ str(LivingRoomHumi)+ " ." \
                                        "Did you want another commands"
                    reprompt_text = "I am ready for new command?"	
                elif("BEDROOM" == Room):
                    speech_output = "Temperature is " + str(BedRoomTemp) + ".  Humidity is "+ str(BedRoomHumi)+ " ." \
                                        "Did you want another commands"
                    reprompt_text = "I am ready for new command?"	
                elif("KITCHEN" == Room):
                    speech_output = "Temperature is " + str(KitchenTemp) + ".  Humidity is "+ str(KitchenHumi)+ " ." \
                                        "Did you want another commands"
                    reprompt_text = "I am ready for new command?"						
						
		            

    #print ('UPLOADED TO IoT: ' + json.dumps(json.loads(myJSONPayload), separators=(',', ':')))
    session_attributes = {}
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def YesIntent_response(intent, session):
    # Set other defaults
    card_title = "YesIntent"
    should_end_session = False
    # Start the real task
    speech_output = "okay, ask me now"
    reprompt_text = "i'm ready"
    # Send response back to the Alexa Voice Skill
    session_attributes = {}
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def NoIntent_response(intent, session):
    # Set other defaults
    card_title = "NotReady"
    should_end_session = True
    # Start the real task
    speech_output = "Ok, ask me when you want."
    reprompt_text = ""
    # Send response back to the Alexa Voice Skill
    session_attributes = {}
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def Help_response():
    # Set other defaults
    card_title = "Help"
    should_end_session = False
    # Start the real task
    speech_output = "Let me help you, what action do you want? " \
                    "I can control Light, TV... report state of your home"
    reprompt_text = "What kind of action do you want? " \
      
    # Send response back to the Alexa Voice Skill
    session_attributes = {"Help"}
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def Stop_response():
    session_attributes = {}
    card_title = "Stop"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    CoffeeChoice = ''
    RegularStrength = ''
    NumberOfCups = ''
    speech_output = "Your coffee machine will power off. Have a nice day!"
    reprompt_text = None
    # Connect and publish to AWS IoT Shadow
    myJSONPayload = "{ \"state\" : {"\
                                "\"desired\": {"\
                                                    "\"WELCOME\": \"YES\", "\
                                                    "\"LivingRoomLight\": \"\", "\
                                                    "\"BedRoomLight\": \"\", "\
                                                    "\"ActionTv\": \"\", "\
                                                    "\"temperature\": \"NO\""\
                                            "} "\
                                "} "\
                "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, IoTShadowCallback_Update, 5)
    print ('UPLOADED TO IoT: ' + json.dumps(json.loads(myJSONPayload), separators=(',', ':')))

    session_attributes = create_attributes(CoffeeChoice,RegularStrength,NumberOfCups)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
# --------------- Helpers that build all of the responses ----------------------
def create_attributes(LivingRoomLight, BedRoomLight, ActionTv):
    return {"LivingRoomLight": LivingRoomLight.upper(), "BedRoomLight": BedRoomLight.upper(), "ActionTv": ActionTv.upper()}
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
