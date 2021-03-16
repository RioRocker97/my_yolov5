import tkinter
from tkinter import ttk
import argparse
from PIL import ImageTk,Image 
import logging
import threading
from tkinter import scrolledtext
import cv2 
from detect import detect as runyolo
from utils.datasets import LoadWebcam
import subprocess
import os
import pycurl
server_path = "http://35.236.179.116:5000"
# ------------------- messy Argprase from detect.py ----------------
parser = argparse.ArgumentParser()
parser.add_argument('--weights', nargs='+', type=str, default='mine/cap_unk.pt', help='model.pt path(s)')
parser.add_argument('--source', type=str, default='0', help='source')  # file/folder, 0 for webcam
parser.add_argument('--img-size', type=int, default=320, help='inference size (pixels)')
parser.add_argument('--conf-thres', type=float, default=0.65, help='object confidence threshold')
parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
parser.add_argument('--device', default='cpu', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
parser.add_argument('--view-img', action='store_true', help='display results')
parser.add_argument('--save-txt', action='store_true',default=True,help='save results to *.txt')
#parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
parser.add_argument('--save-dir', type=str, default='retrain/label', help='directory to save results')
parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
parser.add_argument('--augment', action='store_true', help='augmented inference')
parser.add_argument('--update', action='store_true', help='update all models')
arg = parser.parse_args()
# ------------------------------------------------------------------
# TextHandler Credited to https://gist.github.com/moshekaplan
class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tkinter.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tkinter.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

def detect():
    print("Now Detecting some object...")
    runyolo(opt=arg) 

def stop_detect():
    print("Now Stopping Detecting")

def send_data():
    print("Now send unknown data to Server")
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL,server_path+"/send")
    curl.setopt(pycurl.POST,1)
    curl.setopt(pycurl.HTTPPOST,[
        ("image",(pycurl.FORM_FILE,os.path.join(os.getcwd(),'retrain\\new_unknown.jpg'))),
        ("text",(pycurl.FORM_FILE,os.path.join(os.getcwd(),'retrain\\new_unknown.txt')))    
        ])
    curl.setopt(pycurl.HTTPHEADER,["Content-Type: multipart/form-data"])
    curl.perform()
    #print("status code :",curl.getinfo(pycurl.HTTP_CODE))
    if(str(curl.getinfo(pycurl.HTTP_CODE)) == '200'):
        subprocess.call("del "+os.path.join(os.path.abspath(os.getcwd()),'retrain\\new_unknown.jpg'),shell=True)
        subprocess.call("del "+os.path.join(os.path.abspath(os.getcwd()),'retrain\\new_unknown.txt'),shell=True)
        print("Delete sent Files")
    curl.close()

def collect_data():
    print("Now Showing new image data to be trained in this model")
    subprocess.call("explorer "+os.path.join(os.path.abspath(os.getcwd()),'retrain\\'), shell=True)

#def myWebcam():
def my_gui():
    print("This is my GUI ")
    frame = tkinter.Tk()
    frame.title('IOT-Project')
    frame.geometry("800x600")
    frame.resizable(width=False, height=False)
    tab_control = ttk.Notebook(frame)
    detect_frame= ttk.Frame(tab_control)
    file_frame = ttk.Frame(tab_control)
    tab_control.add(detect_frame,text='Detect Zone')
    tab_control.add(file_frame,text='File Zone ')
    tab_control.pack(expand=1,fill="both")

    example = ImageTk.PhotoImage(Image.open("gui_data/goose.png"))
    icon = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"))


    # Detect Tab widget
    button_style = ttk.Style().configure("def.TButton",font=("Courier",16))
    label1 = ttk.Label(detect_frame,text="Detect Zone")
    box1 = ttk.Label(detect_frame,image=example,borderwidth=5,relief='solid')
    btn1 = ttk.Button(detect_frame,text="Detect",command = detect,style="def.TButton")
    btn2 = ttk.Button(detect_frame,text="Stop",command = stop_detect,style="def.TButton")

    scroll = scrolledtext.ScrolledText(detect_frame,state='disabled',borderwidth=5)
    scroll.configure(font='TkFixedFont')
    text_handler = TextHandler(scroll)
    logger = logging.getLogger()
    logger.addHandler(text_handler)

    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    label1.config(font=("Courier", 36))

    label1.pack()
    box1.pack(pady="10")
    btn1.pack(pady=10,ipadx="10",ipady="10")
    btn2.pack(ipadx="10",ipady="10")
    scroll.pack(pady=20)

    #File Tab widget
    label1 = ttk.Label(file_frame,text="File Zone")
    box1 = ttk.Label(file_frame,image=example,borderwidth=5,relief='solid')
    btn1 = ttk.Button(file_frame,text="Open",command = collect_data,style="def.TButton")
    btn3 = ttk.Button(file_frame,text="Send",command = send_data,style="def.TButton")
    label1.config(font=("Courier", 36))

    label1.pack()
    box1.pack(pady="10")
    btn1.pack(pady=10,ipadx="10",ipady="10")
    btn3.pack(pady=10,ipadx="10",ipady="10")

    frame.iconphoto(False,icon)
    frame.mainloop()

if __name__ == '__main__':
    my_gui()