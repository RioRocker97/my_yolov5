###############################################
#                                             #
# Test any library if i have doubt            #
#                                             #
############################################### 
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

## GUI Global ####################
frame = tkinter.Tk()
vdo_stream = ttk.Label()
###################

## Global ###################
video = 0
isVideoCreated = False
example = ImageTk.PhotoImage(Image.open("gui_data/goose.png").resize((480,360)))
icon = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"))
####################

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
class ClientApp(tkinter.Tk):
    #example = ImageTk.PhotoImage(Image.open("gui_data/goose.png"))
    example = Image.open("gui_data/goose.png")
    #example = tkinter.PhotoImage(file="gui_data/goose.png")
    icon = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"))
    def __init__(self):
        super().__init__()

        self.title("IOT-Project : Client")
        self.geometry("800x600")
        self.resizable(width=False, height=False)
        #self.iconphoto(False,icon)
        #self.folder_path = os.getcwd()

        tab_control = ttk.Notebook(self)
        detect_frame= ttk.Frame(tab_control)
        file_frame = ttk.Frame(tab_control)

        tab_control.add(detect_frame,text='Detect Zone')
        tab_control.add(file_frame,text='File Zone ')
        tab_control.pack(expand=1,fill="both")

        button_style = ttk.Style().configure("def.TButton",font=("Courier",16))
        # Detect Zone
        label1 = ttk.Label(detect_frame,text="Detect Zone")
        label1.config(font=("Courier", 36))
        self.vdo_stream = ttk.Label(detect_frame,image=ImageTk.PhotoImage(self.example),borderwidth=5,relief='solid')
        btn1 = ttk.Button(detect_frame,text="Detect",command = changeIMG,style="def.TButton")
        btn2 = ttk.Button(detect_frame,text="Stop",style="def.TButton")

        scroll = scrolledtext.ScrolledText(detect_frame,state='disabled',borderwidth=5)
        scroll.configure(font='TkFixedFont')
        text_handler = TextHandler(scroll)
        logger = logging.getLogger()
        logger.addHandler(text_handler)

        logger.warning('warn message')
        logger.error('error message')
        logger.critical('critical message')

        label1.pack()
        self.vdo_stream.pack(pady="10")
        btn1.pack(pady=10,ipadx="10",ipady="10")
        btn2.pack(ipadx="10",ipady="10")
        scroll.pack(pady=20)

        #File Zone
        example2 =example
        label1 = ttk.Label(file_frame,text="File Zone")
        box3 = ttk.Label(file_frame,image=example2,borderwidth=5,relief='solid')
        btn1 = ttk.Button(file_frame,text="Open",style="def.TButton")
        btn3 = ttk.Button(file_frame,text="Send",style="def.TButton")
        label1.config(font=("Courier", 36))

        label1.pack()
        box3.pack(pady="10")
        btn1.pack(pady=10,ipadx="10",ipady="10")
        btn3.pack(pady=10,ipadx="10",ipady="10")
def setImage_To_Video():
    global video
    global isVideoCreated
    if(isVideoCreated):
        _,frame = video.read()
        frame = cv2.flip(frame,1)
        image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGBA)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image=image)
        return image

    else:
        example = ImageTk.PhotoImage(Image.open("gui_data/goose.png"))
        return example
def mywebcam():
    global video
    global isVideoCreated
    try:
        if(video.isOpened()):
            print("Camera is on")
    except:
        print("### Camera is not loaded ###")
        #default = ImageTk.PhotoImage(Image.open("gui_data/goose.png"))
    else:
        _,frame = video.read()
        frame = cv2.flip(frame,1)
        imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGBA)
        imageVDO = Image.fromarray(imageVDO)
        imageVDO = ImageTk.PhotoImage(image=imageVDO)
        vdo_stream.configure(image=imageVDO)
def cameraOn():
    print("...Try opening camera...")
    global video
    global isVideoCreated
    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH,320)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT,320)
    if(video.isOpened()):
        print("...Camera is wokring...")
        isVideoCreated = True
def changeIMG():
    print("Changing image ")
    global example
    global vdo_stream
    example = ImageTk.PhotoImage(Image.open("gui_data/overwork.jpg").resize((480,360)))
    vdo_stream.configure(image=example)
def changeIMG2():
    print("Changing image ")
    global example
    global vdo_stream
    example = ImageTk.PhotoImage(Image.open("gui_data/goose.png").resize((480,360)))
    vdo_stream.configure(image=example)
def buildGUI():
    global vdo_stream
    global example
    print("This is my GUI ")
    frame.title('IOT-Project')
    frame.geometry("800x800")
    frame.resizable(width=False, height=False)
    tab_control = ttk.Notebook(frame)
    detect_frame= ttk.Frame(tab_control)
    file_frame = ttk.Frame(tab_control)
    tab_control.add(detect_frame,text='Detect Zone')
    tab_control.add(file_frame,text='File Zone ')
    tab_control.pack(expand=1,fill="both")

    # Detect Tab widget
    button_style = ttk.Style().configure("def.TButton",font=("Courier",16))
    label1 = ttk.Label(detect_frame,text="Detect Zone")
    vdo_stream = ttk.Label(detect_frame,image=example,borderwidth=5,relief='solid')
    btn1 = ttk.Button(detect_frame,text="Detect",command = changeIMG,style="def.TButton")
    btn2 = ttk.Button(detect_frame,text="Stop",command = changeIMG2,style="def.TButton")

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
    vdo_stream.pack(pady="10")
    btn1.pack(pady=10,ipadx="10",ipady="10")
    btn2.pack(ipadx="10",ipady="10")
    scroll.pack(pady=20)

    #File Tab widget

    box3 = vdo_stream
    example2 =example
    label1 = ttk.Label(file_frame,text="File Zone")
    box3 = ttk.Label(file_frame,image=example2,borderwidth=5,relief='solid')
    btn1 = ttk.Button(file_frame,text="Open",style="def.TButton")
    btn3 = ttk.Button(file_frame,text="Send",style="def.TButton")
    label1.config(font=("Courier", 36))

    label1.pack()
    box3.pack(pady="10")
    btn1.pack(pady=10,ipadx="10",ipady="10")
    btn3.pack(pady=10,ipadx="10",ipady="10")

    frame.iconphoto(False,icon)

if __name__ == '__main__':
    buildGUI()
    subprocess.run(["cls"],shell=True)
    task = threading.Thread(target=cameraOn)
    task.start()
    task2 = threading.Thread(target=frame.mainloop())
    task2.start()

