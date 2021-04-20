###############################################
#                                             #
# Main Client Program V1.1                    #
#                                             #
############################################### 
import logging
import threading
import cv2 
import subprocess
import os
import pycurl
import time
import shutil
import json
import base64
import argparse
import tkinter
from platform import system

from tkinter import ttk,scrolledtext
from PIL import ImageTk,Image 
from io import BytesIO
from mygui_detect import prepareYolo,runYolo
## GUI Global ####################
frame = tkinter.Tk()
vdo_stream = ttk.Label()
server_res = ttk.Label()
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
server_path = "http://riorocker97.com"
VERSION = "v1.1"
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
    global vdo_stream,server_res
    global vdo_slot,pic_slot
    global scroll
    frame.title('IOT-Project : Client '+VERSION)
    frame.geometry("800x800")
    frame.resizable(width=False, height=False)
    tab_control = ttk.Notebook(frame)
    detect_frame= ttk.Frame(tab_control)
    file_frame = ttk.Frame(tab_control)
    profile_frame = ttk.Frame(tab_control)
    tab_control.add(profile_frame,text='Client Profile')
    tab_control.add(detect_frame,text='Detection')
    tab_control.add(file_frame,text='Single Data Sending')
    tab_control.pack(expand=1,fill="both")

    #Style
    button_style = ttk.Style().configure("def.TButton",font=("Courier",16))

    # Profile Tab Widget
    #If there a login info created in program
    if True:
        label1 = ttk.Label(profile_frame,text="This Device is new !")
        box_label = ttk.Label(profile_frame,text="Factory Name")
        box_label2 = ttk.Label(profile_frame,text="Device Name")
        box_label3 = ttk.Label(profile_frame,text="Password")
        text_box = ttk.Entry(profile_frame)
        text_box2 = ttk.Entry(profile_frame)
        text_box3 = ttk.Entry(profile_frame,show="#")
        register = ttk.Button(profile_frame,text="Register",command = register_device,style="def.TButton")


        label1.config(font=("Courier", 24))
        box_label.config(font=("Courier", 18))
        box_label2.config(font=("Courier", 18))
        box_label3.config(font=("Courier", 18))
        text_box.config(font=("Courier", 20))
        text_box2.config(font=("Courier", 20))
        text_box3.config(font=("Courier", 20))

        label1.pack(pady="20")
        pro_x = 20
        pro_y = 100
        box_label.place(x=pro_x,y=pro_y)
        pro_y+=40
        text_box.place(x=pro_x,y=pro_y)
        pro_y+=50
        box_label2.place(x=pro_x,y=pro_y)
        pro_y+=40
        text_box2.place(x=pro_x,y=pro_y)
        pro_y+=50
        box_label3.place(x=pro_x,y=pro_y)
        pro_y+=40
        text_box3.place(x=pro_x,y=pro_y)
        pro_x = 500
        pro_y = 200
        register.place(x=pro_x,y=pro_y)
    else :
        # will implement model listing from yolo-server later #
        all_model = [
            "Model 1",
            "Model 2",
            "Model 3"
        ]
        ##########################################
        label1 = ttk.Label(profile_frame,text="This Device is ready !")
        device = ttk.Label(profile_frame,text="Factory : ...")
        device2 = ttk.Label(profile_frame,text="Device : ...")
        device3 = ttk.Label(profile_frame,text="Password Secured !")
        selected_model = tkinter.StringVar(profile_frame)
        selected_model.set(all_model[0])
        model_select = tkinter.OptionMenu(profile_frame,selected_model,*all_model)
    
        model_select.config(width="10",font=("Courier",18))
        #send_new = ttk.Button(profile_frame,text="Send Image",command = send_raw_image,style="def.TButton")

        label1.config(font=("Courier", 24))
        device.config(font=("Courier", 20))
        device2.config(font=("Courier", 20))
        device3.config(font=("Courier", 20))
        model_select.config(width="10",font=("Courier",18))

        label1.pack(pady="20")
        pro_x = 20
        pro_y = 100
        device.place(x=pro_x,y=pro_y)
        pro_y+=50
        device2.place(x=pro_x,y=pro_y)
        pro_y+=50
        device3.place(x=pro_x,y=pro_y)
        pro_x+=380
        pro_y=100
        model_select.place(x=pro_x,y=pro_y)
        pro_y+=60
        #send_new.place(x=pro_x,y=pro_y)

    # Detect Tab widget
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

    #vdo_slot2 =vdo_slot
    label1 = ttk.Label(file_frame,text="File Zone")
    server_res = ttk.Label(file_frame,image=pic_slot,borderwidth=5,relief='solid')
    btn1 = ttk.Button(file_frame,text="Open",command=collect_data,style="def.TButton")
    btn3 = ttk.Button(file_frame,text="Send",command=send_data,style="def.TButton")
    before = ttk.Button(file_frame,text="<",command=left_swipe,style="def.TButton")
    after = ttk.Button(file_frame,text=">",command=right_swipe,style="def.TButton")
    label2 = ttk.Label(file_frame,text="Today Count")
    label3 = ttk.Label(file_frame,text="000")
    file_scroll = scrolledtext.ScrolledText(file_frame,state='disabled',borderwidth=5,width=55, height=10)

    file_scroll.configure(font=('TkFixedFont',12),background="black")
    file_scroll.tag_config('info',foreground='#15A0CA')
    file_scroll.tag_config('warn',foreground='#DE9B00')
    file_scroll.tag_config('error',foreground='#DA3C15')
    file_scroll.tag_config('ok',foreground='#00F942')
    label1.config(font=("Courier", 36))
    label2.config(font=("Courier", 24))
    label3.config(font=("Courier", 22))

    pro_x = 20
    pro_y = 80

    label1.pack()
    server_res.place(x=pro_x,y=pro_y)
    pro_x+=550
    btn1.place(x=pro_x,y=pro_y)
    pro_y+=50
    btn3.place(x=pro_x,y=pro_y)
    pro_y+=70
    label2.place(x=pro_x,y=pro_y)
    pro_y+=60
    label3.place(x=pro_x,y=pro_y)
    pro_x = 20
    pro_y = 450
    before.place(x=pro_x,y=pro_y)
    pro_x+= 300
    after.place(x=pro_x,y=pro_y)
    pro_x-=300
    pro_y+=80
    file_scroll.place(x=pro_x,y=pro_y)

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
    global pic_slot,server_res
    print("Now send unknown data to Server")
    curl = pycurl.Curl()
    rep = BytesIO()
    #curl.setopt(pycurl.URL,server_path+"/send")
    curl.setopt(pycurl.URL,server_path+"/api/detect")
    curl.setopt(pycurl.POST,1)
    curl.setopt(pycurl.HTTPPOST,[
        ("image",(pycurl.FORM_FILE,os.path.join(os.getcwd(),'unknown\\new_unknown.jpg'))),  
        ])
    curl.setopt(pycurl.HTTPHEADER,["Content-Type: multipart/form-data"])
    curl.setopt(pycurl.WRITEDATA,rep)
    curl.perform()
    if(str(curl.getinfo(pycurl.HTTP_CODE)) == '200'):
        rep_body = json.loads(rep.getvalue())
        buff = BytesIO(base64.b64decode(rep_body['image']))
        result = Image.open(buff).resize((480,360))
        res2 = ImageTk.PhotoImage(image=result)
        pic_slot = res2
        server_res.configure(image=pic_slot)

    curl.close()
def clearUnknown():
    if os.path.exists("./unknown") :
        shutil.rmtree("./unknown")
    os.makedirs("./unknown")
def collect_data():
    #print("Now Showing new image data to be trained in this model")
    subprocess.call("explorer "+os.path.join(os.path.abspath(os.getcwd()),'unknown\\'), shell=True)
def register_device():
    print("Now sending data to save in YOLO-server")
def send_raw_image():
    print("Now sending Raw image to be used to create new model to YOLO-server")
def left_swipe():
    print("Swiping to left...")
def right_swipe():
    print("Swiping to right...")


def yolo_client():
    buildGUI()
    clearUnknown()
    arg = ""
    if system() == 'Windows':
        arg = "cls"
    else:
        arg = "clear"
    subprocess.run([arg],shell=True)
    #task = threading.Thread(target=cameraYOLO)
    #task.start()
    task2 = threading.Thread(target=frame.mainloop())
    task2.start()
