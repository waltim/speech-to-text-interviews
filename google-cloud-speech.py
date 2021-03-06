#!/usr/bin/env python3
import glob, os
from os import path
from os.path import join, dirname
import speech_recognition as sr
from multiprocessing.dummy import Pool
import json

pool = Pool(8) # Number of concurrent threads

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

GOOGLE_CLOUD_SPEECH_CREDENTIALS = os.environ.get("GOOGLE_CLOUD_SPEECH_CREDENTIALS")

with open(GOOGLE_CLOUD_SPEECH_CREDENTIALS) as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()

dir_path = os.path.dirname(__file__)

# exec(open(dir_path+'/mkv-to-mp4.py').read()) #able this command if you need to convert all mkv's to mp4 files.

os.system('audioconvert convert interviews/ interviews/ --output-format .wav')

print('############## Audio Transcribe initiate ###################')

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

os.chdir(dir_path+"/interviews/")
for file in glob.glob("*.wav"):
    print(file)
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "interviews/"+file)
    
    os.system('unsilence ' + AUDIO_FILE + ' ' + AUDIO_FILE + ' -ao -y') #this command remove silence and reduce time of the interview

    from pydub import AudioSegment
    from pydub.silence import split_on_silence
    
    print('############## Chunking audio ###################')

    sound_file = AudioSegment.from_wav(AUDIO_FILE)
    audio_chunks = split_on_silence(sound_file, min_silence_len=500, silence_thresh=-40)

    for i, chunk in enumerate(audio_chunks): 
        # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
       silence_chunk = AudioSegment.silent(duration=500)
       # Add the padding chunk to beginning and end of the entire chunk.
       audio_chunk = silence_chunk + chunk + silence_chunk
       # Normalize the entire chunk.
       normalized_chunk = match_target_amplitude(audio_chunk, -20.0)
               
       out_file = "{0}.wav".format(i)
    #    print("exporting", out_file)
       output = path.join(path.dirname(path.realpath(__file__)), 'output/'+out_file)
       normalized_chunk.export(output, bitrate = "192k", format = "wav")

    print('############## Chunking finished ###################')
    
    # exec(open(dir_path+'/unsilence-chunks.py').read()) # this code implies a small improviment to the recognition, but the process time are so greater
    
    r = sr.Recognizer()
    from tkinter import Tcl
    os.chdir(dir_path+'/output/')
    chunks = glob.glob("*.wav")
    files = Tcl().call('lsort', '-dict', chunks)

    def transcribe(data):
        idx, file = data
        name = dir_path+'/output/'+file
        print(name + " started")
        # Load audio file
        with sr.AudioFile(name) as source:
            audio = r.record(source)
        # Transcribe audio file
        text = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, language='pt-BR', show_all=True) #ignore some erros ocurred and generate a json row on transcript
        # text = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, language='pt-BR')
        
        print(name + " done")
        return {
            "idx": idx,
            "text": text
        }

    all_text = pool.map(transcribe, enumerate(files))

    transcript = ""
    for t in sorted(all_text, key=lambda x: x['idx']):
        total_seconds = t['idx'] * 30
        # Cool shortcut from:
        # https://stackoverflow.com/questions/775049/python-time-seconds-to-hms
        # to get hours, minutes and seconds
        m, s = divmod(total_seconds, 60)
        h, m = divmod(m, 60)

        # Format time as h:m:s - 30 seconds of text
        # transcript = transcript + "{:0>2d}:{:0>2d}:{:0>2d} {}\n".format(h, m, s, t['text'])
        transcript = transcript + "{}\n".format(t['text'])

    with open(dir_path+"/transcriptions/gc-"+file[:-4]+".txt", "w") as f:
        f.write(transcript)
    f.close()
    
    new_transcript = ""
    new_transcript2 = ""
    file1 = open(dir_path+"/transcriptions/gc-"+file[:-4]+".txt", 'r')
    Lines = file1.readlines()
    count = 0
    for line in Lines:
        count += 1
        
        line = line.replace("{'","{\"")
        line = line.replace("':","\":")
        line = line.replace(" '"," \"")
        line = line.replace("',","\",")
        line = line.replace("'}","\"}")
        
        jsonLine = json.loads(line, strict=False)
        if not 'results' in jsonLine:
            continue
        else:
            for alternatives in jsonLine['results']:
                for item in alternatives['alternatives']:
                    new_transcript2 = new_transcript2 + " "+item['transcript'] #concatenate all strings generating a long text
                    new_transcript = new_transcript + item['transcript']+"\n" #create a new line by each string
                    
    file1.close()

    with open(dir_path+"/transcriptions/google-cloud-"+file[:-4]+".txt", "w") as f:
        f.write(new_transcript)
    f.close()
    
    with open(dir_path+"/transcriptions/google-cloud-2-"+file[:-4]+".txt", "w") as h:
        h.write(new_transcript2)
    h.close()
    
    os.remove(dir_path+"/transcriptions/gc-"+file[:-4]+".txt")
    exec(open(dir_path+'/clean-chunks.py').read())

pool.close()
pool.join()

exec(open(dir_path+'/clean-interviews.py').read())
print('############## Finished ###################')