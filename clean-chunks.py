import glob, os
from os import path

dir_path = os.path.dirname(__file__)
    
os.chdir(dir_path+"/output/")
for f in glob.glob("*.wav"):
    os.remove(f)

print('############## Directory output cleaned!!! ###################')
    