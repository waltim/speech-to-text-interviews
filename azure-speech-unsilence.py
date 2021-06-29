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

os.chdir(dir_path+"/interviews/")
for file in glob.glob("*.wav"):
    print(file)
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "interviews/"+file)

    os.system('unsilence ' + AUDIO_FILE + ' ' + AUDIO_FILE + ' -ao -y')
    
    import azure.cognitiveservices.speech as speechsdk
    
    f=open(dir_path+"/transcriptions/unsilenced-"+file[:-4]+".txt","w+")

    def from_file():
        
        speech_config = speechsdk.SpeechConfig(subscription=SUBSCRIPTION, region=REGION, speech_recognition_language="pt-BR")
        audio_input = speechsdk.AudioConfig(filename=AUDIO_FILE)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
        result = speech_recognizer.recognize_once_async().get()
        f.write(result.text)
        
    from_file()
    f.close()
   
exec(open(dir_path+'/clean-interviews.py').read())
print('############## Finished ###################')