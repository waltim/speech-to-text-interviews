#!/usr/bin/env python3
import glob, os
from os import path
from os.path import join, dirname
import speech_recognition as sr
from multiprocessing.dummy import Pool

pool = Pool(8) # Number of concurrent threads

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

GOOGLE_CLOUD_SPEECH_CREDENTIALS = os.environ.get("GOOGLE_CLOUD_SPEECH_CREDENTIALS")

with open(GOOGLE_CLOUD_SPEECH_CREDENTIALS) as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()

dir_path = os.path.dirname(__file__)

r = sr.Recognizer()
from tkinter import Tcl
chunks = os.listdir('output/')
files = Tcl().call('lsort', '-dict', chunks)

def transcribe(data):
    idx, file = data
    name = dir_path+'/output/'+file
    print(name + " started")
    # Load audio file
    with sr.AudioFile(name) as source:
        audio = r.record(source)
    # Transcribe audio file
    text = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, language='pt-BR', show_all=True)
    print(name + " done")
    return {
        "idx": idx,
        "text": text
    }

all_text = pool.map(transcribe, enumerate(files))
pool.close()
pool.join()

transcript = ""
for t in sorted(all_text, key=lambda x: x['idx']):
    total_seconds = t['idx'] * 30
    # Cool shortcut from:
    # https://stackoverflow.com/questions/775049/python-time-seconds-to-hms
    # to get hours, minutes and seconds
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)

    # Format time as h:m:s - 30 seconds of text
    transcript = transcript + "{:0>2d}:{:0>2d}:{:0>2d} {}\n".format(h, m, s, t['text'])

print(transcript)

with open("transcript.txt", "w") as f:
    f.write(transcript)