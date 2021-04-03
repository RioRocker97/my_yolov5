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
import time
import shutil
from io import BytesIO
from mygui_detect import prepareYolo,runYolo
## GUI Global ####################
frame = tkinter.Tk()
vdo_stream = ttk.Label()
scroll = scrolledtext.ScrolledText()
###################

## Global ###################
video = 0
isVideoCreated = False
isVideoStop = False
vdo_slot = ImageTk.PhotoImage(Image.open("gui_data/goose.png").resize((480,360)))
pic_slot = ImageTk.PhotoImage(Image.open("gui_data/overwork.jpg").resize((480,360)))
icon = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"))
obj_count = 0
last_count = 0
MODEL_PATH = "./mine/cap_unk.pt"
# my main server (integrated with mongoDB)
#server_path = "http://104.199.135.213:5000"
server_path = "http://riorocker97.com"
# my backup server (integrated with mongoDB)
#server_path = "http://34.95.21.118:5000"
####################
def insertLog(msg,msgtype):
    global scroll
    scroll.configure(state='normal')
    scroll.insert(tkinter.END,msg + '\n',msgtype)
    scroll.configure(state='disabled')
    scroll.yview(tkinter.END)
def mywebcam():
    global isVideoCreated
    if(isVideoCreated):
        insertLog("...Begin detection...","info")
        live_vdo()
    else:
        insertLog("### Camera is not loaded ###","error")
def vdostop():
    global isVideoStop
    if(not isVideoStop):
        isVideoStop = True
        insertLog("...VDO streaming from camera is stopped...","warn")
        if(obj_count != 0):
            insertLog("Found Objects : "+str(obj_count),"ok")
        else:
            insertLog("...No Objects Found...","info")
def live_vdo():
    global isVideoStop,vdo_stream,vdo_slot,obj_count,last_count
    if(not isVideoStop):

        max_count,frame = runYolo(obj_count)
        imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imageVDO2 = Image.fromarray(imageVDO).resize((480,360))
        imageVDO3 = ImageTk.PhotoImage(image=imageVDO2)
        vdo_slot = imageVDO3
        vdo_stream.configure(image=vdo_slot)

        if last_count <= max_count:
            obj_count += (max_count - last_count)
            last_count = max_count
        if max_count == 0:
            last_count = 0

        vdo_stream.after(10,live_vdo)
def buildGUI():
    global vdo_stream
    global vdo_slot
    global scroll
    frame.title('IOT-Project : Client v1.0')
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
    vdo_stream = ttk.Label(detect_frame,image=vdo_slot,borderwidth=5,relief='solid')
    btn1 = ttk.Button(detect_frame,text="Detect",command = mywebcam,style="def.TButton")
    btn2 = ttk.Button(detect_frame,text="Stop",command = vdostop,style="def.TButton")

    scroll = scrolledtext.ScrolledText(detect_frame,state='disabled',borderwidth=5)
    scroll.configure(font=('TkFixedFont',12),background="black")
    scroll.tag_config('info',foreground='#15A0CA')
    scroll.tag_config('warn',foreground='#DE9B00')
    scroll.tag_config('error',foreground='#DA3C15')
    scroll.tag_config('ok',foreground='#00F942')

    label1.config(font=("Courier", 36))

    label1.pack()
    vdo_stream.pack(pady="10")
    btn1.pack(pady=10,ipadx="10",ipady="10")
    btn2.pack(ipadx="10",ipady="10")
    scroll.pack(padx=100,pady=20)

    #File Tab widget

    box3 = vdo_stream
    #vdo_slot2 =vdo_slot
    label1 = ttk.Label(file_frame,text="File Zone")
    box3 = ttk.Label(file_frame,image=pic_slot,borderwidth=5,relief='solid')
    btn1 = ttk.Button(file_frame,text="Open",command=collect_data,style="def.TButton")
    btn3 = ttk.Button(file_frame,text="Send",command=send_data,style="def.TButton")
    label1.config(font=("Courier", 36))

    label1.pack()
    box3.pack(pady="10")
    btn1.pack(pady=10,ipadx="10",ipady="10")
    btn3.pack(pady=10,ipadx="10",ipady="10")

    frame.iconphoto(False,icon)
def cameraYOLO():
    global isVideoCreated
    start = time.time()
    try:
        insertLog("...Preparing Camera && YOLOv5 model...","warn")
        prepareYolo(MODEL_PATH)
        insertLog("...Camera and YOLOv5 is ready...",'ok')
    except:
        insertLog("### Error loading camera && YoloV5 ###",'error')
    else:
        insertLog("Time used : (%.2fs)" % (time.time()-start) ,"ok")
        isVideoCreated = True
def send_data():
    print("Now send unknown data to Server")
    curl = pycurl.Curl()
    rep = BytesIO()
    #curl.setopt(pycurl.URL,server_path+"/send")
    curl.setopt(pycurl.URL,server_path+"/api/uploadunknown")
    curl.setopt(pycurl.POST,1)
    curl.setopt(pycurl.HTTPPOST,[
        ("image",(pycurl.FORM_FILE,os.path.join(os.getcwd(),'unknown\\new_unknown.jpg'))),  
        ])
    curl.setopt(pycurl.HTTPHEADER,["Content-Type: multipart/form-data"])
    curl.setopt(pycurl.WRITEDATA,rep)
    curl.perform()
    #print("status code :",curl.getinfo(pycurl.HTTP_CODE))
    if(str(curl.getinfo(pycurl.HTTP_CODE)) == '200'):
        subprocess.call("del "+os.path.join(os.path.abspath(os.getcwd()),'unknown\\new_unknown.jpg'),shell=True)
        subprocess.call("del "+os.path.join(os.path.abspath(os.getcwd()),'unknown\\new_unknown.txt'),shell=True)
        print("Delete sent Files")
        rep_body = rep.getvalue()
        print(rep_body.decode('iso-8859-1'))
    curl.close()
def clearUnknown():
    if os.path.exists("./unknown") :
        shutil.rmtree("./unknown")
    os.makedirs("./unknown")
def collect_data():
    #print("Now Showing new image data to be trained in this model")
    subprocess.call("explorer "+os.path.join(os.path.abspath(os.getcwd()),'unknown\\'), shell=True)
if __name__ == '__main__':
    buildGUI()
    clearUnknown()
    subprocess.run(["cls"],shell=True)
    task = threading.Thread(target=cameraYOLO)
    task.start()
    task2 = threading.Thread(target=frame.mainloop())
    task2.start()

