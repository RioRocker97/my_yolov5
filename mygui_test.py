###############################################
#                                             #
# Test any library if i have doubt            #
#                                             #
############################################### 
import threading
import cv2 
import subprocess
import os
import pycurl
import time
import platform
import torch
from mygui_detect import prepareYolo,runYolo

if __name__ == '__main__':
    subprocess.call('cls',shell=True)
    print(platform.system())
    print(torch.cuda.is_available())
    print(torch.cuda.device_count())
    print(torch.cuda.get_device_name(0))

