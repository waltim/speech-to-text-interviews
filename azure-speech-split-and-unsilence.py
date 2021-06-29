import glob, os
from os import path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SUBSCRIPTION = os.environ.get("SUBSCRIPTION")
REGION = os.environ.get("REGION")

dir_path = os.path.dirname(__file__)

os.system('audioconvert convert interviews/ interviews/ --output-format .wav')

print('############## Audio Transcribe initiate ###################')

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

os.chdir(dir_path+"/interviews/")
for file in glob.glob("*.wav"):
    print(file)
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "interviews/"+file)
    
    os.system('unsilence ' + AUDIO_FILE + ' ' + AUDIO_FILE + ' -ao -y')

    from pydub import AudioSegment
    from pydub.silence import split_on_silence

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
       
    import azure.cognitiveservices.speech as speechsdk

    f= open(dir_path+"/transcriptions/splited-"+file[:-4]+".txt","w+")
    
    from tkinter import Tcl
    os.chdir(dir_path+'/output/')
    chunks = glob.glob("*.wav")
    for chunkfile in Tcl().call('lsort', '-dict', chunks):
        print(chunkfile)
        audio = dir_path+'/output/'+chunkfile
        # print(audio)
        def from_file():
            speech_config = speechsdk.SpeechConfig(subscription=SUBSCRIPTION, region=REGION, speech_recognition_language="pt-BR")
            audio_input = speechsdk.AudioConfig(filename=audio)
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
            result = speech_recognizer.recognize_once_async().get()
            f.write(" "+result.text)
        from_file()
    f.close()
    exec(open(dir_path+'/clean-chunks.py').read())
    
exec(open(dir_path+'/clean-interviews.py').read())
print('############## Finished ###################')
