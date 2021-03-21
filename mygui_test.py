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
import subprocess
import os
import pycurl

## GUI Global ####################
frame = tkinter.Tk()
vdo_stream = ttk.Label()
scroll = scrolledtext.ScrolledText()
###################

## Global ###################
video = 0
isVideoCreated = False
isVideoStop = False
example = ImageTk.PhotoImage(Image.open("gui_data/goose.png").resize((480,360)))
icon = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"))
####################
def insertLog(msg,msgtype):
    global scroll
    scroll.configure(state='normal')
    scroll.insert(tkinter.END,msg + '\n',msgtype)
    scroll.configure(state='disabled')
    scroll.yview(tkinter.END)
def mywebcam():
    global video

    try:
        if(video.isOpened()):
            insertLog("...Camera is ready...","info")
    except:
        insertLog("### Camera is not loaded ###","error")
    else:
        live_vdo()
        """
        _,frame = video.read()
        frame = cv2.flip(frame,1)
        imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imageVDO_2 = Image.fromarray(imageVDO)
        imageVDO_3 = ImageTk.PhotoImage(image=imageVDO_2)
        example = imageVDO_3
        vdo_stream.configure(image=example)
        """
def vdostop():
    global isVideoStop
    global vdo_stream
    global video
    if(not isVideoStop):
        isVideoStop = True
        insertLog("...VDO streaming from camera is stopped...","info")
        video.release()
def live_vdo():
    global video
    global isVideoStop
    global vdo_stream
    global example

    if(not isVideoStop):
        _,frame = video.read()
        frame = cv2.flip(frame,1)
        imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imageVDO_2 = Image.fromarray(imageVDO).resize((480,360))
        imageVDO_3 = ImageTk.PhotoImage(image=imageVDO_2)
        example = imageVDO_3
        vdo_stream.configure(image=example)
        vdo_stream.after(10,live_vdo)
def cameraOn():
    global video
    global isVideoCreated
    insertLog("...Opening Camera...","warn")

    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH,480)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT,360)
    if(video.isOpened()):
        #print("...Camera is wokring...")
        insertLog("...Camera is up and running...","info")
        isVideoCreated = True
def buildGUI():
    global vdo_stream
    global example
    global scroll
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
    btn1 = ttk.Button(detect_frame,text="Detect",command = mywebcam,style="def.TButton")
    btn2 = ttk.Button(detect_frame,text="Stop",command = vdostop,style="def.TButton")

    scroll = scrolledtext.ScrolledText(detect_frame,state='disabled',borderwidth=5)
    scroll.configure(font=('TkFixedFont',12),background="black")
    scroll.tag_config('info',foreground='#15A0CA')
    scroll.tag_config('warn',foreground='#DE9B00')
    scroll.tag_config('error',foreground='#DA3C15')

    label1.config(font=("Courier", 36))

    label1.pack()
    vdo_stream.pack(pady="10")
    btn1.pack(pady=10,ipadx="10",ipady="10")
    btn2.pack(ipadx="10",ipady="10")
    scroll.pack(padx=100,pady=20)

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

