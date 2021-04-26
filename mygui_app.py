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
import pycurl,json
import time
import shutil
import json
import base64
import argparse
import tkinter

from platform import system
from tkinter import ttk,scrolledtext
from tkinter import messagebox as mb
from PIL import ImageTk,Image 
from io import BytesIO
from mygui_detect import prepareYolo,runYolo
## GUI Global ####################
frame = tkinter.Tk()
vdo_stream = ttk.Label()
server_res = ttk.Label()
scroll = scrolledtext.ScrolledText()
file_scroll = scrolledtext.ScrolledText()
###################

## Global ###################
video = 0
isVideoCreated = False
isVideoStop = False
vdo_slot = ImageTk.PhotoImage(Image.open("gui_data/goose.png").resize((480,360)))
pic_slot = ImageTk.PhotoImage(Image.open("gui_data/overwork.jpg").resize((480,360)))
icon = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"))
file_icon = [
    ImageTk.PhotoImage(Image.open("gui_data/folder.png").resize((64,64))),
    ImageTk.PhotoImage(Image.open("gui_data/view_mode.png").resize((32,32))),
    ImageTk.PhotoImage(Image.open("gui_data/capture_mode.png").resize((32,32))),
    ImageTk.PhotoImage(Image.open("gui_data/cap.png").resize((64,64))),
    ImageTk.PhotoImage(Image.open("gui_data/upload.png").resize((64,64)))
]
file_btn =[]
obj_count = 0
last_count = 0
device = list()
unknown_res = list()
curr_unk = 0
get_unknown_now = True
view_mode = False
capture_mode = False
MODEL_PATH = "./mine/cap_unk.pt"
server_path = "http://riorocker97.com"
#server_path = "127.0.0.1"
VERSION = "v1.5.1"
selected_model = tkinter.StringVar()
selected_raw_image = Image.new(mode="RGB",size=(480,360))
ser_model_start_at = 0
####################
def insertLog(msg,msgtype):
    global scroll
    scroll.configure(state='normal')
    scroll.insert(tkinter.END,msg + '\n',msgtype)
    scroll.configure(state='disabled')
    scroll.yview(tkinter.END)
def file_insertLog(msg,msgtype):
    global file_scroll
    file_scroll.configure(state='normal')
    file_scroll.insert(tkinter.END,msg + '\n',msgtype)
    file_scroll.configure(state='disabled')
    file_scroll.yview(tkinter.END)
def mywebcam():
    global isVideoCreated
    if(isVideoCreated):
        insertLog("...Begin detection...","info")
        vdo = threading.Thread(target=live_vdo)
        send_unknown_trigger = threading.Thread(target=time_trigger)
        vdo.start()
        send_unknown_trigger.start()
    else:
        insertLog("### Camera is not loaded ###","error")
def vdostop():
    global isVideoStop,unknown_res,curr_unk
    isVideoStop = True
    count_path = os.getcwd()+"/gui_data/count_info.txt"
    insertLog("...VDO streaming from camera is stopped...","warn")
    if(obj_count != 0):
        insertLog("Found Objects : "+str(obj_count),"ok")
        if not os.path.exists(count_path):
            count_log = open(count_path,"w")
            count_log.write(str(obj_count))
            count_log.close()
        else:
            count_log = open(count_path,"r")
            temp =int(count_log.read())
            count_log.close()
            new_count_log = open(count_path,"w")
            new_count_log.write(str(obj_count+temp))
            new_count_log.close()
    else:
        insertLog("...No Objects Found...","info")
    insertLog("Unknown Found :"+str(len(unknown_res)),"ok")
    curr_unk = len(unknown_res)-1
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

        vdo_stream.after(1,live_vdo)
def file_live_vdo(frame):
    global capture_mode,server_res,pic_slot,selected_raw_image
    if capture_mode:

        imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imageVDO2 = Image.fromarray(imageVDO).resize((480,360))
        imageVDO3 = ImageTk.PhotoImage(image=imageVDO2)
        pic_slot = imageVDO3
        selected_raw_image = imageVDO2
        server_res.configure(image=pic_slot)
def file_capture_vdo():
    global pic_slot,capture_mode
    cap_cam = cv2.VideoCapture(0)
    while True:
        _,frame = cap_cam.read()
        cv2.waitKey(1)
        file_live_vdo(frame)
        if not capture_mode:
            break
def buildGUI():
    global vdo_stream,server_res,vdo_slot,pic_slot,scroll,file_scroll,MODEL_PATH
    global device,selected_model,file_btn,ser_model_start_at
    count_path = os.getcwd()+"/gui_data/count_info.txt"
    model_log_path = os.getcwd()+"/gui_data/model_info.txt"
    model_path = os.getcwd()+"/mine/"
    total_count = 0
    if os.path.exists(count_path) :
        count_log = open(count_path)
        total_count = int(count_log.read())

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
    if not os.path.isfile(os.getcwd()+"/gui_data/login_info.txt"):
        device.append(tkinter.StringVar())
        device.append(tkinter.StringVar())
        device.append(tkinter.StringVar())

        label1 = ttk.Label(profile_frame,text="This Device is new !")
        box_label = ttk.Label(profile_frame,text="Factory Name")
        box_label2 = ttk.Label(profile_frame,text="Device Name")
        box_label3 = ttk.Label(profile_frame,text="Password")
        text_box = ttk.Entry(profile_frame,textvariable=device[0])
        text_box2 = ttk.Entry(profile_frame,textvariable=device[1])
        text_box3 = ttk.Entry(profile_frame,show="#",textvariable=device[2])
        register = ttk.Button(profile_frame,text="Register",command = thread_register,style="def.TButton")


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
        login_info = open(os.getcwd()+"/gui_data/login_info.txt","r")
        temp = login_info.readlines()
        info = [
            temp[0].split("\n")[0],
            temp[1].split("\n")[0],
        ]
        all_model = []
        ### get local model list ####
        all_model.append("/// LOCAL ///")
        for model_file in os.listdir(model_path):
            if(model_file.split('.')[1] == 'pt'):
                all_model.append(model_file.split('.')[0])
        ### get local model list ####
        ### get server model list ####
        all_model.append("/// SERVER ///")
        ser_model_start_at = len(all_model)
        all_model = listServerModel(all_model)
        print("Server Model start at : %i" % ser_model_start_at)
        ### get server model list ####
        label1 = ttk.Label(profile_frame,text="This Device is ready !")
        device = ttk.Label(profile_frame,text="Factory : "+info[0])
        device2 = ttk.Label(profile_frame,text="Device : "+info[1])
        device3 = ttk.Label(profile_frame,text="Password Secured !")
        selected_model = tkinter.StringVar(profile_frame)
        selected_model.set("cap_unk")
        ## get seletec model from file if exist ###
        if os.path.exists(model_log_path) :
            model_log = open(model_log_path)
            temp = model_log.read()
            selected_model.set(temp)
            MODEL_PATH = './mine/'+temp+'.pt'
            print("Now preparing "+MODEL_PATH)
            model_log.close()
        ## get seletec model from file if exist ###
        selected_model.trace('w',get_model)
        model_select = tkinter.OptionMenu(profile_frame,selected_model,*all_model)
    
        model_select.configure(width="15",font=("Courier",18))
        #send_new = ttk.Button(profile_frame,text="Send Image",command = send_raw_image,style="def.TButton")

        label1.config(font=("Courier", 24))
        device.config(font=("Courier", 20))
        device2.config(font=("Courier", 20))
        device3.config(font=("Courier", 20))

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
    btn1 = ttk.Button(file_frame,image=file_icon[0],command=collect_data,style="def.TButton")
    btn2 = ttk.Button(file_frame,image=file_icon[1],command=swapFileMode,style="def.TButton")
    btn3 = ttk.Button(file_frame,image=file_icon[2],command=swapFileMode2,style="def.TButton")
    before = ttk.Button(file_frame,text="<",command=left_swipe,style="def.TButton")
    cap = ttk.Button(file_frame,image=file_icon[3],command=cap_one,style="def.TButton")
    upload = ttk.Button(file_frame,image=file_icon[4],command=send50raw,style="def.TButton",state='disabled')
    after = ttk.Button(file_frame,text=">",command=right_swipe,style="def.TButton")
    label2 = ttk.Label(file_frame,text="Today Count")
    label3 = ttk.Label(file_frame,text=str(total_count))
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
    pro_x+=600
    btn1.place(x=pro_x,y=pro_y)
    pro_y+=80
    btn2.place(x=pro_x,y=pro_y)
    pro_x+=50
    btn3.place(x=pro_x,y=pro_y)
    pro_x-=100
    pro_y+=70
    label2.place(x=pro_x,y=pro_y)
    pro_y+=60
    label3.place(x=pro_x,y=pro_y)
    pro_x = 20
    pro_y = 450
    before.place(x=pro_x,y=pro_y)
    pro_x+= 200
    cap.place(x=pro_x,y=pro_y)
    pro_x+= 100
    after.place(x=pro_x,y=pro_y)
    pro_x+= 200
    upload.place(x=pro_x,y=pro_y)
    pro_x-=500
    pro_y+=80
    file_scroll.place(x=pro_x,y=pro_y)

    file_btn.append(btn2)
    file_btn.append(btn3)
    file_btn.append(cap)
    file_btn.append(upload)

    frame.iconphoto(False,icon)
def listServerModel(all_model):

    rep = BytesIO()
    detect_token = ""
    login_info = open(os.getcwd()+"/gui_data/login_info.txt","r")
    temp = login_info.readlines()
    info = [
        temp[1].split("\n")[0],
        temp[2].split("\n")[0]
    ]
    prep = pycurl.Curl()
    prep.setopt(pycurl.URL,server_path+"/api/login")
    prep.setopt(pycurl.HTTPAUTH,pycurl.HTTPAUTH_BASIC)
    prep.setopt(pycurl.USERNAME,info[0])
    prep.setopt(pycurl.PASSWORD,info[1])
    prep.setopt(pycurl.WRITEDATA,rep)
    t0 = time.time()
    prep.perform()
    print("Time used: %.2f" % (time.time()-t0))
    if(str(prep.getinfo(pycurl.HTTP_CODE)) == '200'):
        rep_body = json.loads(rep.getvalue())
        detect_token = rep_body['token']
    prep.close()

    get_model = pycurl.Curl()
    rep = BytesIO()
    get_model.setopt(pycurl.URL,server_path+"/api/listModel")
    get_model.setopt(pycurl.WRITEDATA,rep)
    get_model.setopt(pycurl.HTTPHEADER,
        ["API_TOKEN:"+ detect_token])
    get_model.perform()
    if(str(get_model.getinfo(pycurl.HTTP_CODE)) == '200'):
        rep_body = json.loads(rep.getvalue())
        ser_model = rep_body['RES']
        for i in ser_model:
            all_model.append(i)
    
    return all_model
def swapFileMode():
    global view_mode,file_btn,curr_unk
    view_mode = not view_mode
    if view_mode:
        file_insertLog("/////// VIEW MODE //////","info")
        file_insertLog("There are "+str(curr_unk)+" unknown images result from YOLO-server","ok")
        file_btn[0].config(state=tkinter.NORMAL)
        file_btn[1].config(state=tkinter.DISABLED)
        file_btn[2].config(state=tkinter.DISABLED)
    else:
        file_insertLog("/////// VIEW MODE END //////","info")
        file_btn[0].config(state=tkinter.NORMAL)
        file_btn[1].config(state=tkinter.NORMAL)
        file_btn[2].config(state=tkinter.NORMAL)
def swapFileMode2():
    global capture_mode,file_btn,file_scroll
    capture_mode = not capture_mode
    if capture_mode:
        file_insertLog("/////// CAPTURE MODE //////","info")
        file_btn[0].config(state=tkinter.DISABLED)
        file_btn[1].config(state=tkinter.NORMAL)
        file_btn[2].config(state=tkinter.NORMAL)

        small_task = threading.Thread(target=file_capture_vdo)
        small_task.start()
    else:
        file_insertLog("/////// CAPTURE MODE END //////","info")
        file_btn[0].config(state=tkinter.NORMAL)
        file_btn[1].config(state=tkinter.NORMAL)
        file_btn[2].config(state=tkinter.NORMAL)
def cap_one():
    global selected_raw_image,file_btn
    save_path = os.getcwd()+"\\unknown\\raw\\"
    num = len(os.listdir(save_path))+1
    selected_raw_image.save(save_path+"something"+str(num)+".jpg")
    file_insertLog("New raw image saved ! (%s/50)" % str(num),"ok")
    if num>=50 :
        file_btn[3].config(state=tkinter.NORMAL)
        file_insertLog("There enough raw images to be used.","warn")
        file_insertLog("You can exit the mode now !","warn")
def get_model(*args):
    global selected_model
    model_path = os.getcwd()+"/mine/"
    if selected_model.get() != "/// LOCAL ///" and selected_model.get() != "/// SERVER ///"  :
        model_log_path = os.getcwd()+"/gui_data/model_info.txt"
        print("selecting a new model : "+selected_model.get())
        model_log = open(model_log_path,'w')
        model_log.write(selected_model.get())
        model_log.close()

        if not os.path.exists(model_path+selected_model.get()+'.pt'):
            if mb.askokcancel("Server Model Seletected !!!","Do you want to download %s from YOLO-server ?" % selected_model.get()) :
                print("...Downloading Model from YOLO-server...")
                download_model(selected_model.get()+'.pt')
            else:
                print("Proceed to choose local model instead")
        mb.showinfo("New Model Selected !!!","Please close this program to take effect.")
    #task = threading.Thread(target=cameraYOLO)
    #task.start()
def download_model(filename):
    rep = BytesIO()
    detect_token = ""
    login_info = open(os.getcwd()+"/gui_data/login_info.txt","r")
    model_path = os.getcwd()+"/mine/"
    temp = login_info.readlines()
    info = [
        temp[1].split("\n")[0],
        temp[2].split("\n")[0]
    ]
    prep = pycurl.Curl()
    prep.setopt(pycurl.URL,server_path+"/api/login")
    prep.setopt(pycurl.HTTPAUTH,pycurl.HTTPAUTH_BASIC)
    prep.setopt(pycurl.USERNAME,info[0])
    prep.setopt(pycurl.PASSWORD,info[1])
    prep.setopt(pycurl.WRITEDATA,rep)
    t0 = time.time()
    prep.perform()
    print("Time used: %.2f" % (time.time()-t0))
    if(str(prep.getinfo(pycurl.HTTP_CODE)) == '200'):
        rep_body = json.loads(rep.getvalue())
        detect_token = rep_body['token']
    prep.close()

    get_model = pycurl.Curl()
    rep = BytesIO()
    get_model.setopt(pycurl.URL,server_path+"/api/getModel/"+filename)
    get_model.setopt(pycurl.WRITEDATA,rep)
    get_model.setopt(pycurl.HTTPHEADER,
        ["API_TOKEN:"+ detect_token])
    get_model.perform()
    if(str(get_model.getinfo(pycurl.HTTP_CODE)) == '200'):
        rep_body = rep.getvalue()
        model_file = open(model_path+filename,'wb')
        model_file.write(rep_body)
        model_file.close()
        print("Write Model file success !")
def send50raw():
    global file_btn

    file_btn[3].config(state=tkinter.DISABLED)
    rep = BytesIO()
    detect_token = ""
    login_info = open(os.getcwd()+"/gui_data/login_info.txt","r")
    model_path = os.getcwd()+"/mine/"
    temp = login_info.readlines()
    info = [
        temp[1].split("\n")[0],
        temp[2].split("\n")[0],
        temp[0].split("\n")[0]
    ]
    prep = pycurl.Curl()
    prep.setopt(pycurl.URL,server_path+"/api/login")
    prep.setopt(pycurl.HTTPAUTH,pycurl.HTTPAUTH_BASIC)
    prep.setopt(pycurl.USERNAME,info[0])
    prep.setopt(pycurl.PASSWORD,info[1])
    prep.setopt(pycurl.WRITEDATA,rep)
    t0 = time.time()
    prep.perform()

    if(str(prep.getinfo(pycurl.HTTP_CODE)) == '200'):
        rep_body = json.loads(rep.getvalue())
        detect_token = rep_body['token']
    prep.close()

    send50 = threading.Thread(target=send1raw(detect_token,info[2]))
    send50.start
def send1raw(token,info):
    save_path = os.getcwd()+"\\unknown\\raw\\"
    rep = BytesIO()
    send50 = pycurl.Curl()
    for raw in os.listdir(save_path):
        send50.setopt(pycurl.URL,server_path+"/api/send50raw")
        send50.setopt(pycurl.POST,1)
        send50.setopt(pycurl.HTTPPOST,[
            ("image",(pycurl.FORM_FILE,save_path+raw)),  
            ])
        send50.setopt(pycurl.HTTPHEADER,
            ["Content-Type: multipart/form-data",
            "API_TOKEN:"+ token,
            "FACTORY:"+ info,
            "OBJ-NAME:"+"something"
            ])
        send50.setopt(pycurl.WRITEDATA,rep)
        send50.perform()
        if(str(send50.getinfo(pycurl.HTTP_CODE)) == '200'):
            file_insertLog("%s had been sent to YOLO-server " % raw,"info")
            os.remove(save_path+raw)
    send50.close()
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
def detect_unknown_constant():
    global pic_slot,server_res,unknown_res
    print("sending unknown data to YOLO-Server")
    unknown_path = os.getcwd()+"/unknown/new_unknown.jpg"
    rep = BytesIO()
    detect_token = ""
    login_info = open(os.getcwd()+"/gui_data/login_info.txt","r")
    temp = login_info.readlines()
    info = [
        temp[1].split("\n")[0],
        temp[2].split("\n")[0]
    ]
    prep = pycurl.Curl()
    prep.setopt(pycurl.URL,server_path+"/api/login")
    prep.setopt(pycurl.HTTPAUTH,pycurl.HTTPAUTH_BASIC)
    prep.setopt(pycurl.USERNAME,info[0])
    prep.setopt(pycurl.PASSWORD,info[1])
    prep.setopt(pycurl.WRITEDATA,rep)
    t0 = time.time()
    prep.perform()
    print("Time used: %.2f" % (time.time()-t0))
    if(str(prep.getinfo(pycurl.HTTP_CODE)) == '200'):
        rep_body = json.loads(rep.getvalue())
        detect_token = rep_body['token']
    prep.close()
    ##
    ##
    curl = pycurl.Curl()
    rep = BytesIO()
    curl.setopt(pycurl.URL,server_path+"/api/detect")
    curl.setopt(pycurl.POST,1)
    curl.setopt(pycurl.HTTPPOST,[
        ("image",(pycurl.FORM_FILE,unknown_path)),  
        ])
    curl.setopt(pycurl.HTTPHEADER,
        ["Content-Type: multipart/form-data",
        "API_TOKEN:"+ detect_token])
    curl.setopt(pycurl.WRITEDATA,rep)
    t0 = time.time()
    curl.perform()
    print("Time used: %.2f" % (time.time()-t0))
    if(str(curl.getinfo(pycurl.HTTP_CODE)) == '200'):
        rep_body = json.loads(rep.getvalue())
        unknown_res.append(base64.b64decode(rep_body['image']))
        #buff = BytesIO(base64.b64decode(rep_body['image']))
    curl.close()
    os.remove(unknown_path)
def time_cooldown():
    global get_unknown_now 
    print("unknown found ! Begin to cooldown...")
    time.sleep(10)
    get_unknown_now = True
    print("cooldown over . getting new unknown...")
def time_trigger():
    global get_unknown_now,isVideoStop,unknown_res
    unknown_path = os.getcwd()+"/unknown/new_unknown.jpg"
    num =0
    while not isVideoStop:
        if os.path.exists(unknown_path) and get_unknown_now:
            get_unknown_now = False
            send_one = threading.Thread(target=detect_unknown_constant)
            send_one.start()
            time_cooldown()
            num+=1
        #else:
        #    print(str(num)+ " unknown not found yet..."+str(len(unknown_res)))
def switch_trigger():
    task_t2 = threading.Thread(target=time_trigger)
    task_t2.start()
def test_time_trigger():
    global get_unknown_now
    while get_unknown_now:
        print("Puppy",end="")
        time.sleep(0.5)
        print(" Puppy",end="")
        time.sleep(0.5)
        print(" Puppy",end="\n")
        time.sleep(0.5)
def clearUnknown():
    if os.path.exists("./unknown") :
        shutil.rmtree("./unknown")
    os.makedirs("./unknown")
    if os.path.exists("./unknown/raw") :
        shutil.rmtree("./unknown/raw")
    os.makedirs("./unknown/raw")
def collect_data():
    #print("Now Showing new image data to be trained in this model")
    subprocess.call("explorer "+os.path.join(os.path.abspath(os.getcwd()),'unknown\\'), shell=True)
def thread_register():
    small_task = threading.Thread(target=register_device)
    small_task.start()
def register_device():
    print("Now sending data to save in YOLO-server")
    global device

    data = json.dumps({
        "ids":"00",
        "factory":device[0].get(),
        "username":device[1].get(),
        "password":device[2].get(),
        "aType":"iot"
    })
    
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL,server_path+"/api/register")
    curl.setopt(pycurl.POST,1)
    curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json','Content-Type: application/json'])
    curl.setopt(pycurl.POSTFIELDS, data)
    print(data)
    curl.perform()
    
    if(str(curl.getinfo(pycurl.HTTP_CODE)) == '200'):
        print("Registeration Completed ! Saving profile...")
        login_info = open(os.getcwd()+"/gui_data/login_info.txt","x")
        login_info.write(device[0].get()+"\n")
        login_info.write(device[1].get()+"\n")
        login_info.write(device[2].get()+"\n")
        login_info.close()
        print("Writing completed...")
        mb.showinfo(title="Registeration",message="Please close a program to complete registeration.")
def send_raw_image():
    print("Now sending Raw image to be used to create new model to YOLO-server")
def left_swipe():
    global unknown_res,curr_unk,pic_slot
    #print("Swiping to left...")

    if(curr_unk==0):
        curr_unk=0
    else:
        curr_unk-=1
    buff = BytesIO(unknown_res[curr_unk])
    result = Image.open(buff).resize((480,360))
    res2 = ImageTk.PhotoImage(image=result)
    pic_slot = res2
    server_res.configure(image=pic_slot)
def right_swipe():
    global unknown_res,curr_unk,pic_slot
    #print("Swiping to Right...")

    if(curr_unk==len(unknown_res)-1):
        curr_unk=len(unknown_res)-1
    else:
        curr_unk+=1
    buff = BytesIO(unknown_res[curr_unk])
    result = Image.open(buff).resize((480,360))
    res2 = ImageTk.PhotoImage(image=result)
    pic_slot = res2
    server_res.configure(image=pic_slot)
def yolo_client():
    arg = ""
    if system() == 'Windows':
        arg = "cls"
    else:
        arg = "clear"
    subprocess.run([arg],shell=True)
    buildGUI()
    clearUnknown()
    task = threading.Thread(target=cameraYOLO)
    task.start()
    task2 = threading.Thread(target=frame.mainloop())
    task2.start()
    