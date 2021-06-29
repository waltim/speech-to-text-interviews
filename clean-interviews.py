import glob, os
from os import path

dir_path = os.path.dirname(__file__)

os.chdir(dir_path+"/interviews/")
for f in glob.glob("*.wav"):
    os.remove(f)

print('############## Directory interviews cleaned!!! ###################')
    