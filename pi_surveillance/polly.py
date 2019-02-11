import boto3
import pygame
import os
import time
import io
import subprocess 
import uuid
import psutil
import json

class Polly():
    OUTPUT_FORMAT='mp3'
    #SOX_COMMAND = 'sudo sox -d -t wavpcm -c 1 -b 16 -r 16000 -e signed-integer --endian little - silence 1 0 1% 5 0.3t 2% > /home/pi/home-surveillance/request.wav'
    SOX_COMMAND = 'sudo sox -t alsa default /home/pi/home-surveillance/request.wav silence 1 0.1 1% 5 0.3t 2%'
    conf = json.load(open("conf.json"))

    def __init__(self, voiceId):
        self.polly = boto3.client('polly') #access amazon web service
        self.VOICE_ID = voiceId

    def speak(self, textToSpeech): #get polly response and play directly
        pollyResponse = self.polly.synthesize_speech(Text=textToSpeech, OutputFormat=self.OUTPUT_FORMAT, VoiceId=self.VOICE_ID)
        
        pygame.mixer.init()
        pygame.init()  # this is needed for pygame.event.* and needs to be called after mixer.init() otherwise no sound is played 
        
        if os.name != 'nt':
            pygame.display.set_mode((1, 1)) #doesn't work on windows, required on linux
            
        with io.BytesIO() as f: # use a memory stream
            f.write(pollyResponse['AudioStream'].read()) #read audiostream from polly
            f.seek(0)
            pygame.mixer.music.load(f)
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            pygame.event.set_allowed(pygame.USEREVENT)
            pygame.mixer.music.play()
            pygame.event.wait() # play() is asynchronous. This wait forces the speaking to be finished before closing
            
        while pygame.mixer.music.get_busy() == True:
            pass

    def saveToFile(self, textToSpeech, fileName): #get polly response and save to file
        pollyResponse = self.polly.synthesize_speech(Text=textToSpeech, OutputFormat=self.OUTPUT_FORMAT, VoiceId=self.VOICE_ID)
        
        with open(fileName, 'wb') as f:
            f.write(pollyResponse['AudioStream'].read())
            f.close()

    def playBeep(self):
        file = 'beep.mp3'
        
        pygame.mixer.init()
        pygame.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        pygame.event.set_allowed(pygame.USEREVENT)
        pygame.mixer.music.play()
        pygame.event.wait()
        while pygame.mixer.music.get_busy() == True:
            pass
    
    
    

    def record(self):
        #print(self.SOX_COMMAND)
        proc=subprocess.Popen(self.SOX_COMMAND,shell=True)
        print(proc.pid)
        try:
            proc.wait(timeout=self.conf["max_voice_duration_in_seconds"])
        except subprocess.TimeoutExpired:
            process = psutil.Process(proc.pid)
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()

    