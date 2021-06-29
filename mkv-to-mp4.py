import glob, os
from os import path

dir_path = os.path.dirname(__file__)

os.chdir(dir_path+"/interviews/")
for f in glob.glob("*.mkv"):
    os.system("ffmpeg -i "+f+" -codec copy "+f[:-4]+".mp4")
    os.remove(f)

print('############## MkV files are convert to MP4!!! ###################')