# -*- coding: utf8 -*-
import urllib2
import os
import sys
import json
import httplib
import wave
import subprocess
import codecs
from time import sleep
 
FLAC_CONV = "\"C:\\Program Files\FLAC\\flac\" -f" # Path to the flac command line tool
GOOGLE_SPEECH_URL_V2 = "https://www.google.com/speech-api/v2/recognize?output=json&lang=vi_VN&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw";
# FLAC_CONV = 'flac -f'  # We need a WAV to FLAC converter. flac is available
                       on Linux

# audio_fname = "xinchao.wav"
# print "Sending ", audio_fname
Convert to flac first
filename = "xinchao.flac"
# del_flac = False
if 'flac' not in filename:
	del_flac = True
	print "Converting to flac"
	print FLAC_CONV + filename
	os.system(FLAC_CONV + ' ' + filename)
	filename = filename.split('.')[0] + '.flac'
def stt_google(filename):
 f = open(filename, 'rb')
 flac_cont = f.read()
 f.close()
 
 # Headers. A common Chromium (Linux) User-Agent
 hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
 'Content-type': 'audio/x-flac; rate=16000'} 
 
 req = urllib2.Request(GOOGLE_SPEECH_URL_V2, data=flac_cont, headers=hrs)
 print "Sending request to Google TTS"
 p = urllib2.urlopen(req)
 response = p.read()
 response = response.split('\n', 1)[1]
 print response
 # Try to get something out of the complicated json response:
 res = json.loads(response)['result'][0]['alternative'][0]['transcript']
 
 return res
xx = stt_google(filename)
print(xx)
haha = u"Tắt đèn phòng khách"
if (xx == haha):
	s = u"Thành Công"
	print(s)
def convert_to_flac(filename):
 print "Converting ", filename
 if '.flac' not in filename: # Check it's not already a flac file
   print "Converting to flac"
   command = FLAC_CONV + ' ' + filename # prepare the command that uses the command line tool
   subprocess.call(command, shell=True) # Run the command
   filename = filename.split('.')[0] + '.flac' # Get the new file's name
   return filename
 else:
   return filename
 
def split_wav_by_silence(filename, min_length_secs = 5):
 w = wave.open(filename, 'r')
 count = 0
 indices = []
 start_frame = 0
 end_frame = 0
 for i in range(w.getnframes()):
   ### read 1 frame and the position will updated ###
   frame = w.readframes(1)
 
   quiet = True
   for j in range(len(frame)):
     # check if amplitude is greater than 1
     if ord(frame[j]) > 1:
       quiet = False
       break
 
   if quiet:
     count += 1
   else:
     count = 0
 
 last = (i == w.getnframes()-1)
 if count > 1 or last: # Detected a silent part
   end_frame = w.tell()
   start_second = start_frame/w.getframerate()
   end_second = end_frame/w.getframerate()
   if end_second - start_second > min_length_secs:
     indices.append({'start':start_frame, 'end':end_frame})
     start_frame = end_frame
   elif last: # If it's the last frame, we need to add that last part.
     indices[-1]['end'] = end_frame
 
 files = []
 count = 0
 for location in indices:
   start = location['start']
   end = location['end']
   print str(start) + ' to ' + str(end)
   w.setpos(start) # Set position on the original wav file
   chunkData = w.readframes(end-start) # And read to where we need
 
   chunkAudio = wave.open('file_'+str(count)+".wav",'w')
   chunkAudio.setnchannels(w.getnchannels())
   chunkAudio.setsampwidth(w.getsampwidth())
   chunkAudio.setframerate(w.getframerate())
   chunkAudio.writeframes(chunkData)
   chunkAudio.close()
   files.append('file_'+str(count)+".wav")
   count+=1
 
 return files
