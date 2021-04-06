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
from PIL import Image,ImageTk
from mygui_detect import prepareYolo,runYolo

if __name__ == '__main__':
    t0 = time.time()
    subprocess.call('cls',shell=True)
    raw = Image.open("./mine/cow.jpg")
    prepareYolo("yolov5s.pt",True,"./mine/cow.jpg")
    _,frame = runYolo(0)
    imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    imageVDO2 = Image.fromarray(imageVDO).resize((480,360))
    print(imageVDO2)
    #imageVDO2.save("cow2.jpg")
    print("time %.2f" % (time.time()-t0))
