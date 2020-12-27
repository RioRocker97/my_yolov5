###############################################
#                                             #
# Test any library if i have doubt            #
#                                             #
############################################### 
import threading
import cv2 
from utils.datasets import LoadWebcam

def mywebcam():
    for img_path, img, img0,cap in LoadWebcam():
        cv2.namedWindow('YOLO', cv2.WINDOW_AUTOSIZE) #make specific window close
        cv2.imshow('YOLO', img0)
        print(img_path)
        if cv2.waitKey(1) == ord('q'):  # q to quit
            cv2.destroyWindow('YOLO') # might be useful later in tkinter
            #raise StopIteration

if __name__ == '__main__':
    task = threading.Thread(target=mywebcam())
    task.start()