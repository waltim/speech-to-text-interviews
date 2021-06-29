#!/usr/bin/env python3
import glob, os

dir_path = os.path.dirname(__file__)

os.chdir(dir_path+'/output/')
for unsilenceChunk in glob.glob("*.wav"):
    os.system('unsilence ' + dir_path+'/output/'+unsilenceChunk + ' ' + dir_path+'/output/'+unsilenceChunk + ' -ao -y')

print('############## Unsilence all chunk files ###################')