# -*- coding: utf8 -*-
import httplib
import subprocess
import alsaaudio, wave, numpy
import os, sys
import time
import json
import codecs
import urllib2
import vlc
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
#define some pin numbers
pinLivingRoomLight = 17
pinKitchenLight = 27
pinBedRoomLight = 22
pinButton = 20
pinButton2 = 21
#Variables
p = ""
position = 0
audioplaying = False
button_pressed = False
button_pressed2 = False
GPIO.cleanup()
#we have to clean up to reset pin definitions
GPIO.setwarnings(False)
#set the software to use the Broadcom numbers
GPIO.setmode(GPIO.BCM)
#set up the  pins definitions
GPIO.setup(pinLivingRoomLight,GPIO.OUT)
GPIO.setup(pinKitchenLight,GPIO.OUT)
GPIO.setup(pinBedRoomLight,GPIO.OUT)
GPIO.setup(pinButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinButton2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

recordFile = "smarthome.wav"
sendFlac = "smarthome.flac"
del_flac = False
GOOGLE_SPEECH_URL_V2 = "https://www.google.com/speech-api/v2/recognize?output=json&lang=vi_VN&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw";
GOOGLE_SPEECH_URL_V2_EN = "https://www.google.com/speech-api/v2/recognize?output=json&lang=en_US&key=AIzaSyAcalCzUvPmmJ7CZBFOEWx2Z1ZSn4Vs1gg";
FLAC_CONV = 'flac -f'  # We need a WAV to FLAC converter. 
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
def pinSet(pin, setState):
        """set pin number to given state"""
        GPIO.output(pin, setState)
def pinRead(pin):
        """Read pin number state"""
        return GPIO.input(pin)
#Colors for logging
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def record_microphone():
    DEVICE = "plughw:1"
    RATE = 44100
    CHANNEL = 1
    print("{}Recording...{}".format(bcolors.OKBLUE, bcolors.ENDC))
    play_audio(path+"audio/sound_start.mp3")
    start = time.time()
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,  alsaaudio.PCM_NORMAL, DEVICE)
    inp.setchannels(1)
    inp.setrate(44100)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(1024)
    w = wave.open('smarthome.wav', 'w')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(44100)
    while ((time.time() - start) < 4):
        # print((time.time() - start))
        l, data = inp.read()
        a = numpy.fromstring(data, dtype='int16')
        w.writeframes(data)
    print("{}Recording Finished.{}".format(bcolors.OKBLUE, bcolors.ENDC))
    play_audio(path+"audio/sound_stop.mp3")
    converFlac(recordFile)
def detect_button(channel):
    global button_pressed
    button_pressed = True
    time.sleep(.5) # time for the button input to settle down
    while (GPIO.input(pinButton)==0): #button seems to still be pressed
        button_pressed = True
        time.sleep(.1)
    button_pressed = False
    time.sleep(.5) # more time for the button to settle down
def detect_button2(channel):
    global button_pressed2
    button_pressed2 = True
    time.sleep(.5) # time for the button input to settle down
    while (GPIO.input(pinButton2)==0): #button seems to still be pressed
        button_pressed2 = True
        time.sleep(.1)
    button_pressed2 = False
    time.sleep(.5) # more time for the button to settle down
def converFlac(recordFile):
        if 'flac' not in recordFile:
                del_flac = True
                os.system(FLAC_CONV + ' ' + recordFile)
                recordFile = recordFile.split('.')[0] + '.flac'
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
        p.audio_set_volume(80)
    else:
        p.audio_set_volume(overRideVolume)
    p.play()
    while audioplaying:
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
def stt_google(GOOGLE_SPEECH_URL):
	f = open(sendFlac, 'rb')
	flac_cont = f.read()
	f.close()
	 # Headers. A common Chromium (Linux) User-Agent
	hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
	'Content-type': 'audio/x-flac; rate=44100'} 
	 
	req = urllib2.Request(GOOGLE_SPEECH_URL, data=flac_cont, headers=hrs)
	print "Sending request to Google TTS"
	p = urllib2.urlopen(req)
	response = p.read()
	response = response.split('\n', 1)[1]
	print response
	 # Try to get something out of the complicated json response:
	try:
		res = json.loads(response)['result'][0]['alternative'][0]['transcript']
	except ValueError, e:
		res = ""
        return res
def setLight(result,client):

	strOff = u"tắt"
	strOff2 = u"bắt"
	strOff3 = u"tất"
	strOn = u"bật"
	strAll= u"cả"
	strLivingRoom = u"khách"
	strBedRoom = u"ngủ"
	strKitchen = u"bếp"
	if (strOn in result):
			if(strAll in result):
					onOffAllLight(1)
					client.publish("/Living/Light/Status", "ON")
					client.publish("/Kitchen/Light/Status", "ON")	
					client.publish("/Bedroom/Light/Status", "ON")	
			if(strLivingRoom in result):
					pin = pinLivingRoomLight
					state = pinRead(pin)
					responseVoiceOn(pin,state)
					client.publish("/Living/Light/Status", "ON")
			elif(strBedRoom in result):
					pin = pinKitchenLight
					state = pinRead(pin)
					responseVoiceOn(pin,state)
					client.publish("/Kitchen/Light/Status", "ON")
			elif(strKitchen in result):
					pin = pinBedRoomLight
					state = pinRead(pin)
					responseVoiceOn(pin,state)
					client.publish("/Bedroom/Light/Status", "ON")
	elif ((strOff in result) or (strOff2 in result) or (strOff3 in result) ):
			if(strAll in result):
					onOffAllLight(0)
					client.publish("/Living/Light/Status", "OFF")
					client.publish("/Kitchen/Light/Status","OFF")	
					client.publish("/Bedroom/Light/Status", "OFF")	
			elif(strLivingRoom in result):
					pin = pinLivingRoomLight
					state = pinRead(pin)
					responseVoiceOff(pin,state)
					client.publish("/Living/Light/Status", "OFF")
			elif(strBedRoom in result):
					pin = pinKitchenLight
					state = pinRead(pin)
					responseVoiceOff(pin,state)
					client.publish("/Kitchen/Light/Status", "OFF")
			elif(strKitchen in result):
					pin = pinBedRoomLight
					state = pinRead(pin)
					responseVoiceOff(pin,state)
					client.publish("/Bedroom/Light/Status", "OFF")
def setLight2(result,client):
	
	strOff = u"off"
	strOn = u"on"
	strAll= u"all"
	strLivingRoom = u"living room"
	strBedRoom = u"bedrom"
	strKitchen = u"kitchen"
	if (strOn in result):
			if(strAll in result):
					onOffAllLight(1)
					client.publish("/Living/Light/state", 1)
					client.publish("/Kitchen/Light/state", 1)	
					client.publish("/Bedroom/Light/state", 1)	
			if(strLivingRoom in result):
					pin = pinLivingRoomLight
					state = pinRead(pin)
					responseVoiceOn(pin,state)
					client.publish("/Living/Light/state", 1)
			elif(strBedRoom in result):
					pin = pinKitchenLight
					state = pinRead(pin)
					responseVoiceOn(pin,state)
					client.publish("/Kitchen/Light/state", 1)
			elif(strKitchen in result):
					pin = pinBedRoomLight
					state = pinRead(pin)
					responseVoiceOn(pin,state)
					client.publish("/Bedroom/Light/state", 1)
	elif (strOff in result):
			if(strAll in result):
					onOffAllLight(0)
					client.publish("/Living/Light/state", 0)
					client.publish("/Kitchen/Light/state", 0)	
					client.publish("/Bedroom/Light/state", 0)	
			elif(strLivingRoom in result):
					pin = pinLivingRoomLight
					state = pinRead(pin)
					responseVoiceOff(pin,state)
					client.publish("/Living/Light/state", 0)
			elif(strBedRoom in result):
					pin = pinKitchenLight
					state = pinRead(pin)
					responseVoiceOff(pin,state)
					client.publish("/Kitchen/Light/state", 0)
			elif(strKitchen in result):
					pin = pinBedRoomLight
					state = pinRead(pin)
					responseVoiceOff(pin,state)
					client.publish("/Bedroom/Light/state", 0)
def onOffAllLight(state):
	if state: 
		pinSet(pinLivingRoomLight,True) 
		pinSet(pinKitchenLight,True) 
		pinSet(pinBedRoomLight,True)
                play_audio(path+"audio/sound_AllOn.mp3")		
	else:
				
		pinSet(pinLivingRoomLight,False) 
		pinSet(pinKitchenLight,False) 
		pinSet(pinBedRoomLight,False) 
                play_audio(path+"audio/sound_AllOff.mp3")		

def responseVoiceOff(pin,state):
	if state:
			pinSet(pin,False)
			if pin == 17:       
				play_audio(path+"audio/sound_OkOffLiving.mp3")
			if pin == 27:       
				play_audio(path+"audio/sound_OkOffKitchen.mp3")
			if pin == 22:       
				play_audio(path+"audio/sound_OkOffBed.mp3")


	else:
			play_audio(path+"audio/sound_NoOff.mp3")
def responseVoiceOn(pin,state):
	if state:
			play_audio(path+"audio/sound_NoOn.mp3")
	else:
			pinSet(pin,True)
			if pin == 17:       
				play_audio(path+"audio/sound_OkOnLiving.mp3")
			if pin == 27:       
				play_audio(path+"audio/sound_OkOnKitchen.mp3")
			if pin == 22:       
				play_audio(path+"audio/sound_OkOnBed.mp3")

def running(client):
        global button_pressed,record_audio, button_pressed2
        GPIO.add_event_detect(pinButton2, GPIO.RISING, callback=detect_button2, bouncetime=100) # threaded detection of button press
        GPIO.add_event_detect(pinButton, GPIO.FALLING, callback=detect_button, bouncetime=100) # threaded detection of button press
        while True:
                # client.on_message = on_message
                # record_audio = False
                # while record_audio == False:
                    # time.sleep(.1)

                if button_pressed:
                        print ("VIETNAM")
                        if audioplaying: p.stop()
##                        record_audio = True	
                        record_microphone()
			button_pressed = False
                        result = stt_google(GOOGLE_SPEECH_URL_V2)
                        print(result.lower())
                        setLight(result.lower(),client)
		elif button_pressed2:
                        print ("ENGLISH")
			button_pressed2 = False
                        if audioplaying: p.stop()
                        record_microphone()
                        result = stt_google(GOOGLE_SPEECH_URL_V2_EN)
                        print(result.lower())
                        setLight2(result.lower(),client)		


if __name__ == '__main__':

    try:
        client = mqtt.Client()
        client.subscribe("/Living/Light")
        client.subscribe("/Kitchen/Light")
        client.subscribe("/Bedroom/Light")
        client.connect(host="192.168.100.20", port=1883, keepalive=60)
        print 'SmartHome started, Press Ctrl-C to quit.'
        running(client)
    finally:
        GPIO.cleanup()
        print 'SmartHome stopped.'
