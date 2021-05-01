import threading,cv2,os,time,pycurl,json,base64
from platform import system
from PIL import Image,ImageTk
from io import BytesIO
from tkinter import Label,scrolledtext,Button,StringVar,LabelFrame,Entry,Tk,messagebox
from tkinter.ttk import Combobox
from mygui_detect import prepareYolo,runYolo

# don't forget to remove fake initialize value in clientGUI
# don't forget to remove default value that in a part of tkinter 
# they all mess up tkinter internal function again
###### Status Variable #########
IS_VDO_CREATED = False
IS_VDO_STOP = False
UNKNOWN_AVAILABLE = False
###### Status Variable #########
###### Regular Variable #########
OBJ_COUNT = {
    'current' : 0,
    'last' : 0,
    'unknown' : 0
}
###### Regular Variable #########
#Client to YOLO-server connection
class useYOLOserver():
    def __init__(self,server='127.0.0.1'):
        self.api = pycurl.Curl()
        self.server = server
        self.rep = BytesIO()
        self.token = ''
        self.tempRes = list()
        self.unknown_path= ''
    def test_server(self):
        self.rep = BytesIO()
        self.api = pycurl.Curl()
        self.api.setopt(pycurl.URL,self.server)
        self.api.setopt(pycurl.WRITEDATA,self.rep)
        t0 = time.time()
        try:
            self.api.perform()
            print("Time used: %.2f" % (time.time()-t0))
            if(str(self.api.getinfo(pycurl.HTTP_CODE)) == '200'):
                print("Server is UP !")
                self.api.close()
                self.rep.close()
                return True
        except:
            print("error at calling API (Test-Server)")
            return False
    def login(self,user,pas):
        self.rep = BytesIO()
        self.api = pycurl.Curl()
        self.api.setopt(pycurl.URL,self.server+"/api/login")
        self.api.setopt(pycurl.HTTPAUTH,pycurl.HTTPAUTH_BASIC)
        self.api.setopt(pycurl.USERNAME,user)
        self.api.setopt(pycurl.PASSWORD,pas)
        self.api.setopt(pycurl.WRITEDATA,self.rep)
        t0 = time.time()
        try:
            self.api.perform()
            print("Time used: %.2f" % (time.time()-t0))
            if(str(self.api.getinfo(pycurl.HTTP_CODE)) == '200'):
                print("Login success !")
                body = json.loads(self.rep.getvalue())
                self.token = body['token']
                print('at login: '+self.token)
            elif(str(self.api.getinfo(pycurl.HTTP_CODE)) == '401'):
                print('Bad Login. Are you unregister ?')
            else:
                print("Server is DOWN !")
        except:
            print('API Error (Login Device)')
        else:
            self.api.close()
            self.rep.close()
    def register(self,data=[]):
        # will do data/file handling later
        data = json.dumps({
            "factory":data[0],
            "username":data[1],
            "password":data[2],
            "aType":"iot"
        })
        self.rep = BytesIO()
        self.api = pycurl.Curl()
        self.api.setopt(pycurl.URL,self.server+"/api/register")
        self.api.setopt(pycurl.POST,1)
        self.api.setopt(pycurl.HTTPHEADER,[
            'Accept: application/json',
            'Content-Type: application/json'])
        self.api.setopt(pycurl.POSTFIELDS, data)
        self.api.setopt(pycurl.WRITEDATA,self.rep)
        t0 = time.time()
        # will do API's respone handling later
        try:
            self.api.perform()
            print("Time used: %.2f" % (time.time()-t0))
            if(str(self.api.getinfo(pycurl.HTTP_CODE)) == '200'):
                print("Register success !")
            else:
                print("Server is DOWN !")
        except:
            print("error at calling API (Register)")
        else:
            self.api.close()
            self.rep.close()
    def unknown(self):
        # will do file/data handling later
        self.rep = BytesIO()
        self.api = pycurl.Curl()
        self.api.setopt(pycurl.URL,self.server+"/api/detect")
        self.api.setopt(pycurl.POST,1)
        self.api.setopt(pycurl.HTTPPOST,[
            ("image",(pycurl.FORM_FILE,self.unknown_path)),  
            ])
        self.api.setopt(pycurl.HTTPHEADER,
            ["Content-Type: multipart/form-data",
            "API_TOKEN:"+ self.token])
        self.api.setopt(pycurl.WRITEDATA,self.rep)
        t0 = time.time()
        try:
            self.api.perform()
            print("Time used: %.2f" % (time.time()-t0))
            if(str(self.api.getinfo(pycurl.HTTP_CODE)) == '200'):
                print("Unknown Detection success !")
                body = json.loads(self.rep.getvalue())
                self.tempRes.append(base64.b64decode(body['image']))
            else:
                print("Server is DOWN !")
        except:
            print("error at calling API (Unknown Detection)")
        else:
            self.api.close()
            self.rep.close()
            os.remove(self.unknown_path)
    def send_raw1(self,token,info):
        save_path = 'filepath'
        raw = 'filename'
        total_time = 0
        # will do file handling later
        self.rep = BytesIO()
        self.api = pycurl.Curl()
        self.api.setopt(pycurl.URL,self.server+"/api/send50raw")
        self.api.setopt(pycurl.POST,1)
        self.api.setopt(pycurl.HTTPPOST,[
            ("image",(pycurl.FORM_FILE,save_path+raw)),  
            ])
        self.api.setopt(pycurl.HTTPHEADER,
            ["Content-Type: multipart/form-data",
            "API_TOKEN:"+ token,
            "FACTORY:"+ info,
            "OBJ-NAME:"+"something"
            ])
        self.api.setopt(pycurl.WRITEDATA,rep)
        t0 = time.time()
        # will do API's respone handling later
        try:
            self.api.perform()
            total_time = time.time()-t0
            if(str(self.api.getinfo(pycurl.HTTP_CODE)) == '200'):
                print("Login success !")
                body = json.loads(self.rep.getvalue())
                self.token = body['token']
            else:
                print("Server is DOWN !")
        except:
            print("error at calling API")
        else:
            self.api.close()
            self.rep.close()
    def getServerModel(self,list_model=[]):
        list_model.append('/// SERVER ///')
        print('at getServer: '+self.token)
        self.rep = BytesIO()
        self.api = pycurl.Curl()
        self.api.setopt(pycurl.URL,self.server+"/api/listModel")
        self.api.setopt(pycurl.WRITEDATA,self.rep)
        self.api.setopt(pycurl.HTTPHEADER,
        ["APK_TOKEN:"+ self.token])
        t0 = time.time()
        # will do API's respone handling later
        try:
            self.api.perform()
            print("Time used: %.2f" % (time.time()-t0))
            if(str(self.api.getinfo(pycurl.HTTP_CODE)) == '200'):
                print("get Server Model List success !")
                rep_body = json.loads(self.rep.getvalue())
                ser_model = rep_body['RES']
                for i in ser_model:
                    list_model.append(i)
            elif str(self.api.getinfo(pycurl.HTTP_CODE)) == '401':
                print('Bad Token')
                list_model.append('### ERROR ####')
            elif str(self.api.getinfo(pycurl.HTTP_CODE)) == '500':
                print('Bad Server')
                list_model.append('### ERROR ####')
            else:
                print("Server is DOWN !")
                list_model.append('### ERROR ####')
        except:
            print('API Error (List Server Model)')
            list_model.append('### ERROR ####')
            return list_model
        else:
            self.api.close()
            self.rep.close()
            
            return list_model
    def downloadServerModel(self,model_path,filename):
        self.rep = BytesIO()
        self.api = pycurl.Curl()
        self.api.setopt(pycurl.URL,self.server+"/api/getModel/"+filename+'.pt')
        self.api.setopt(pycurl.HTTPHEADER,
        ["API_TOKEN:"+ self.token])
        self.api.setopt(pycurl.WRITEDATA,self.rep)
        t0 = time.time()
        try:
            self.api.perform()
            print("Time used: %.2f" % (time.time()-t0))
            if(str(self.api.getinfo(pycurl.HTTP_CODE)) == '200'):
                print("download "+filename+" from YOLO-server success !")
                rep_body = self.rep.getvalue()
                model_file = open(model_path+filename+'.pt','wb')
                model_file.write(rep_body)
                model_file.close()
                print("Write Model file success !")
            else:
                print("Server is DOWN !")
        except:
            print("error at calling API")
        else:
            self.api.close()
            self.rep.close()

    def prepareUnknown(self,path):
        self.unknown_path = path
    def UnknownResult(self):
        temp = self.tempRes
        self.tempRes = list()
        return temp
#Client File Handler
# (except Image/icon data. those things will be handled by clientGUI coz'
# TK's stupid internal function won't let me call ImageTK data before TK() exist)
class clientFileData():
    def __init__(self):
        self.mainPath = os.getcwd()
        self.folder ={
            'GUIData': self.mainPath+"/gui_data/",
            'ModelData' : self.mainPath+"/mine/",
            'UnknownData': self.mainPath+"/unknown/",
            'RawData': self.mainPath+"/unknown/raw/"
        }
        self.all_file = {
            'count':self.folder['GUIData']+'count_info.txt',
            'device':self.folder['GUIData']+'login_info.txt',
            'model':self.folder['GUIData']+'model_info.txt',
        }
        self.currModelPath = "./mine/cap_unk.pt"
        self.currModel = "cap_unk"
        for path in self.folder:
            if not os.path.exists(self.folder[path]):
                print(path+' Folder not found. creating new one')
                os.makedirs(self.folder[path])
            else:
                print(path+' Folder found.')
        for path in self.all_file:
            if not os.path.isfile(self.all_file[path]):
                print(path+' File not found. creating new one')
                new_file = open(self.all_file[path],'w')
                new_file.close()
            else:
                print(path+' File found.')
        _ = self.getCurrentModel()

    def getCurrentModel(self):
        model_file = open(self.all_file['model'],'r')
        if model_file.read() == '':
            model_file = open(self.all_file['model'],'w')
            model_file.write(self.currModel)
        model_file = open(self.all_file['model'],'r')
        self.currModel = model_file.read()
        self.currModelPath = './mine/'+self.currModel+'.pt'
        model_file.close()
        return self.currModel
    def setCurrentModel(self,new_model=''):
        model_file = open(self.all_file['model'],'w')
        self.currModel = new_model
        self.currModelPath = './mine/'+self.currModel+'.pt'
        model_file.write(self.currModel)
        model_file.close()
    def getCurrentModelPath(self):
        return self.currModelPath
    def getListLocalModels(self):
        local_model =['/// LOCAL ///']
        for file in os.listdir(self.folder['ModelData']):
            if file.split('.')[1] == 'pt':
                local_model.append(file.split('.')[0])
        return local_model
    def checkModel(self,model=''):
        if os.path.exists(self.folder['ModelData']+model+'.pt'):
            return True
        return False
    def getModelPath(self):
        return self.folder['ModelData']
    def getUnknownPath(self):
        return self.folder['UnknownData']+"new_unknown.jpg"

    def getCount(self):
        count_file =open(self.all_file['count'])
        if count_file.read() == '':
            count_file = open(self.all_file['count'],'w')
            count_file.write('0')
        count_file =open(self.all_file['count'])
        #print(self.all_file['count'],count_file.read())
        self.last_count = int(count_file.read())
        count_file.close()
        return self.last_count
    def setCount(self,total_count=0):
        count_file =open(self.all_file['count'],'w')
        self.last_count = total_count
        count_file.write(str(total_count))
        count_file.close()

    #should do password encryption too.. but i DON'T WANT TO
    def getUserInfo(self):
        user_file =open(self.all_file['device'])
        temp = user_file.readlines()
        user_file.close()
        if len(temp) != 0 :
            return True,{
        'factory': temp[0].split('\n')[0],
        'user':    temp[1].split('\n')[0],
        'pass':    temp[2].split('\n')[0],
        }
        return False,{}
    def setUserInfo(self,info={}):
        user_file =open(self.all_file['device'],'w')
        user_file.write(info['factory']+"\n")
        user_file.write(info['user']+"\n")
        user_file.write(info['pass']+"\n")
        user_file.close()
#input box with placeholder
class input_box(Entry):
    def __init__(self, master=None,placeholder='',isPassword=False,**kw):
        super().__init__(master=master,**kw)
        self.placeholder = placeholder
        self.isPassword = isPassword
        self.value = ''

        self.config(fg="#808080")
        self.insert(0,self.placeholder)
        self.bind('<FocusIn>',self.__focus_in)
        self.bind('<FocusOut>',self.__focus_out)
        #self.bind('<Leave>',self.__leave)
        if self.isPassword:
            self.bind('<Enter>',self.__enter_pass)
            self.bind('<Leave>',self.__leave_pass)

    def __focus_in(self,*kw):
        if self.get() != self.value:
            self.config(fg="#000000")
            self.delete('0','end')
    def __focus_out(self,*kw):
        if self.isPassword :
            self.config(show="#")
        else:
            self.config(show='')
        if self.get() == '':
            self.config(show='')
            self.config(fg="#808080")
            self.insert(0,self.placeholder)
        else:
            self.value = self.get()
            self.config(fg="#228B22")   
    def __enter_pass(self,*kw):
        self.config(show='')
    def __leave_pass(self,*kw):
        self.__leave()
        if self.get() != '' and self.get() != 'Password':
            self.config(show='#')
    def __leave(self,*kw):
        self.value = self.get()
    def getValue(self):
        return self.value
#Client Log with msg function
class clientLog(scrolledtext.ScrolledText):
    INFO = 'info'
    WARN = 'warn'
    ERROR = 'error'
    OK = 'ok'
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)

        self.configure(font=('TkFixedFont',12),background="black")
        self.tag_config(clientLog.INFO,foreground='#15A0CA')
        self.tag_config(clientLog.WARN,foreground='#DE9B00')
        self.tag_config(clientLog.ERROR,foreground='#DA3C15')
        self.tag_config(clientLog.OK,foreground='#00F942')

    def info_msg(self,msg):
        self.__put_msg(msg,clientLog.INFO)
    def warn_msg(self,msg):
        self.__put_msg(msg,clientLog.WARN)
    def error_msg(self,msg):
        self.__put_msg(msg,clientLog.ERROR)
    def ok_msg(self,msg):
        self.__put_msg(msg,clientLog.OK)
    def __put_msg(self,msg,msgtype):
        self.config(state='normal')
        self.insert('end',msg + '\n',msgtype)
        self.configure(state='disabled')
        self.yview('end')
#Client Registeration & Login Widget
class clientUserInfo(LabelFrame):
    def __init__(self, master=None,isDeviceRegister=True,userInfo={},register_img=None,api=useYOLOserver(),filehandler=None,**kw):
        super().__init__(master=master,**kw)
        self.parent = master
        self.userInfo = userInfo
        self.api = api
        self.fileHandler = filehandler
        if isDeviceRegister:
            factory = Label(self,text=self.userInfo['factory'])
            deviceID = Label(self,text=self.userInfo['user'])
            server_status = Label(self,text="YOLO-Server : Online")

            factory.config(font=('tahoma',14))
            deviceID.config(font=('tahoma',14))
            server_status.config(font=('tahoma',14))

            factory.place(relx=0.02,rely=0.01)
            deviceID.place(relx=0.02,rely=0.2)
            server_status.place(relx=0.02,rely=0.4)
        else:
            self.config(text='!!! Unregistered !!!')

            self.factory = input_box(self,'Factory Name')
            self.device = input_box(self,'Device Name')
            self.secret = input_box(self,'Password',True)
            register_btn = Button(self,image=register_img,command=self.__doRegister)

            self.factory.config(font=('tahoma',14))
            self.device.config(font=('tahoma',14))
            self.secret.config(font=('tahoma',14))

            self.factory.place(relx=0.02,rely=0.1)
            self.device.place(relx=0.02,rely=0.4)
            self.secret.place(relx=0.02,rely=0.7)
            register_btn.place(relx=0.78,rely=0.0)
    def __doRegister(self):
        msg = "The Following Device Info will be registered\n"
        msg += "Factory : "+ self.factory.getValue() +"\n"
        msg += "Device : "+ self.device.getValue() +"\n"
        msg += "Password : "+ self.secret.getValue() +"\n"
        msg += "Are these OK to be registered ?"
        if messagebox.askokcancel('New Device Register !!!',msg):
            self.api.register(data=[
                self.factory.getValue(),
                self.device.getValue(),
                self.secret.getValue(),
            ])
            self.userInfo = {
                'factory': self.factory.getValue(),
                'user': self.device.getValue(),
                'pass': self.secret.getValue()
            }
            self.fileHandler.setUserInfo(self.userInfo)
            self.__init__(self.parent,userInfo=self.userInfo)
        else :
            print('Register canceled')

##############################################################
#Main Application's GUI building wil Tkinter
class clientGUI(Tk):
    __allImages = {}
    __allWidgets = {
        #'log' : clientLog(),
        #'screen' : Label(),
        #'detect' : Button(),
        #'detect_isOn' : Label(),
        #'model': Combobox()
    }
    __allModes ={
        'detect' : False,
        'view' : False,
        'capture' : False
    }
    def __init__(self,VERSION,server='127.0.0.1'):
        super().__init__()
        self.fileHandler = clientFileData()
        self.yoloServer = useYOLOserver(server=server)
        self.unknown_res = list()
        self.cooldown_time = 10

        self.modelList = self.fileHandler.getListLocalModels()
        self.objCount = self.fileHandler.getCount()
        self.regis_status,self.user_info = self.fileHandler.getUserInfo()


        self.__buildGUI(VERSION)

    
    ############### private Function #############################
    def __buildGUI(self,VERSION):
        self.__loadGUIphoto()
        self.selected_model = StringVar(self)
        self.selected_model.set(self.fileHandler.getCurrentModel())

        self.title("YOLO-client v"+VERSION)
        self.geometry("800x600")
        self.resizable(width=False, height=False)
        self.iconphoto(False,clientGUI.__allImages['icon'])

        # build components (text,button,log,screen ETC.)
        clientGUI.__allWidgets['count'] = Label(self,text="Today Count : "+str(self.objCount))
        clientGUI.__allWidgets['screen'] = Label(self,image=clientGUI.__allImages['screen_img'])
        clientGUI.__allWidgets['log'] = clientLog(self,borderwidth=10)
        clientGUI.__allWidgets['detect'] = Button(self,command=self.__detect_btn,image=clientGUI.__allImages['detect'])
        clientGUI.__allWidgets['view'] = Button(self,command=self.__view_btn,image=clientGUI.__allImages['view'])
        clientGUI.__allWidgets['cap'] = Button(self,command=self.__cap_btn,image=clientGUI.__allImages['cap'])
        clientGUI.__allWidgets['detect_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['view_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['cap_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['model'] = Combobox(self,textvariable=self.selected_model,state='readonly')
        clientGUI.__allWidgets['model']['values'] = self.modelList
        clientGUI.__allWidgets['model'].bind('<<ComboboxSelected>>',self.__swapModelYOLO)
        clientGUI.__allWidgets['user_info'] = clientUserInfo(
            self,
            text="Device Info",
            isDeviceRegister=self.regis_status,
            userInfo=self.user_info,
            register_img = clientGUI.__allImages['Register'],
            api = self.yoloServer,
            filehandler= self.fileHandler
            )
        
        # config style 
        clientGUI.__allWidgets['count'].config(font=('tahoma',24))
        #suggestion_label.config(font=('tahoma',20))
        clientGUI.__allWidgets['model'].configure(width="15",font=("tahoma",18))

        # place components
        clientGUI.__allWidgets['count'].place(relx=0.01,rely=0.01)

        clientGUI.__allWidgets['screen'].place(relx=0.01,rely=0.1)

        clientGUI.__allWidgets['detect'].place(relx=0.63,rely=0.01)
        clientGUI.__allWidgets['view'].place(relx=0.77,rely=0.01)
        clientGUI.__allWidgets['cap'].place(relx=0.90,rely=0.01)
        clientGUI.__allWidgets['detect_isOn'].place(relx=0.63,rely=0.13)
        clientGUI.__allWidgets['view_isOn'].place(relx=0.77,rely=0.13)
        clientGUI.__allWidgets['cap_isOn'].place(relx=0.90,rely=0.13)

        clientGUI.__allWidgets['model'].place(relx=0.68,rely=0.2)
        #suggestion_label.place(relx=0.65,rely=0.3)

        clientGUI.__allWidgets['log'].place(relx=0.01,rely=0.72,width=500,height=150)
        clientGUI.__allWidgets['user_info'].place(relx=0.64,rely=0.72,width=280,height=150) 
    def __loadModel(self):
        global IS_VDO_CREATED,IS_VDO_STOP
        start = time.time()

        clientGUI.__allWidgets.get('detect').config(state='disabled')
        clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages['isWarn'])
        clientGUI.__allWidgets['model'].config(state='disabled')
        try:
            clientGUI.__allWidgets.get('log').warn_msg("... Preparing Camera && YOLOv5 model ...")
            clientGUI.__allWidgets.get('log').warn_msg("... Using Model : "+self.fileHandler.getCurrentModel()+' ...')
            prepareYolo(self.fileHandler.getCurrentModelPath())
        except:
            clientGUI.__allWidgets.get('log').error_msg("### Error loading camera && YoloV5 ###")
            clientGUI.__allWidgets.get('log').error_msg("### Plug in any camera and Restart YOLO-Client ###")
            clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages['isError'])
            IS_VDO_CREATED = False
        else:
            clientGUI.__allWidgets.get('log').ok_msg("...Camera and YOLOv5 is ready...")
            clientGUI.__allWidgets.get('log').ok_msg("Time used : (%.2fs)" % (time.time()-start))
            clientGUI.__allWidgets.get('detect').config(state='normal')
            clientGUI.__allWidgets['model'].config(state='readonly')
            clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages['isOff'])
            IS_VDO_CREATED = True
            IS_VDO_STOP = False   
    def __loadGUIphoto(self):
        clientGUI.__allImages['icon'] = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"),master=self)
        clientGUI.__allImages['screen_img'] = ImageTk.PhotoImage(Image.new('RGB',(480,360)),master=self)
        clientGUI.__allImages['detect'] = ImageTk.PhotoImage(Image.open("gui_data/cap.png").resize((64,64)),master=self)
        clientGUI.__allImages['view'] = ImageTk.PhotoImage(Image.open("gui_data/view_mode.png").resize((64,64)),master=self)
        clientGUI.__allImages['cap'] = ImageTk.PhotoImage(Image.open("gui_data/capture_mode.png").resize((64,64)),master=self)
        clientGUI.__allImages['isOn'] = ImageTk.PhotoImage(Image.new('RGB',(64,20),'#22FF00'),master=self)
        clientGUI.__allImages['isWarn'] = ImageTk.PhotoImage(Image.new('RGB',(64,20),'#FFD700'),master=self)
        clientGUI.__allImages['isError'] = ImageTk.PhotoImage(Image.new('RGB',(64,20),'#FF4500'),master=self)
        clientGUI.__allImages['isOff'] = ImageTk.PhotoImage(Image.new('RGB',(64,20)),master=self)
        clientGUI.__allImages['Register'] = ImageTk.PhotoImage(Image.open("gui_data/register.png").resize((50,120)),master=self)
    def __checkLogin(self):
        if self.regis_status :
            self.yoloServer.login(user=self.user_info['user'],pas=self.user_info['pass'])
            self.modelList = self.yoloServer.getServerModel(self.modelList)
            clientGUI.__allWidgets['model']['values'] = self.modelList
        else :
            clientGUI.__allWidgets['log'].error_msg('!!!! Unregistered Device !!!!')
            clientGUI.__allWidgets['log'].error_msg('Device must be registerd to gain access to YOLO-Server')
            clientGUI.__allWidgets['log'].error_msg('!!!! Unregistered Device !!!!')
    def __checkServer(self):
        if self.yoloServer.test_server() :
            clientGUI.__allWidgets['log'].info_msg('YOLO-server is up and running')
        else :
            clientGUI.__allWidgets['log'].info_msg('YOLO-server is down')
            clientGUI.__allWidgets['log'].warn_msg('Check your internet connection and restart YOLO-client')
    # detect mode process
    def __detectProcess(self):
        global IS_VDO_CREATED,IS_VDO_STOP
        clientGUI.__allWidgets['log'].warn_msg('////////// Detect Mode //////////')
        if IS_VDO_CREATED:
            clientGUI.__allWidgets['log'].ok_msg('.......... Begin Detection ............')
            live_yolo = threading.Thread(target=self.__liveYOLO)
            unknown_trigger = threading.Thread(target=self.__time_trigger)
            live_yolo.start()
            unknown_trigger.start()
    def __liveYOLO(self):
        global IS_VDO_STOP,OBJ_COUNT
        while not IS_VDO_STOP:
            temp_count,frame = runYolo(OBJ_COUNT['current'])
            vdo_slot = self.__convertImageToTk(frame)
            clientGUI.__allWidgets['screen'].configure(image=vdo_slot)

            if OBJ_COUNT['last'] <= temp_count:
                OBJ_COUNT['current'] += (temp_count - OBJ_COUNT['last'])
                OBJ_COUNT['last'] = temp_count
            if temp_count == 0:
                OBJ_COUNT['last'] = 0
            clientGUI.__allWidgets['count'].configure(text="Today Count : "+str(self.objCount + OBJ_COUNT['current']))
        if IS_VDO_STOP:
            self.fileHandler.setCount(total_count=self.objCount + OBJ_COUNT['current'])
            vdo_slot = clientGUI.__allImages['screen_img']
            clientGUI.__allWidgets['screen'].configure(image=vdo_slot)
    def __convertImageToTk(self,frame):
        imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imageVDO2 = Image.fromarray(imageVDO).resize((480,360))
        imageVDO3 = ImageTk.PhotoImage(image=imageVDO2,master=self)
        return imageVDO3
    def __stopAndReloadliveYOLO(self):
        clientGUI.__allWidgets['log'].warn_msg("...VDO streaming from camera is stopped...")
        clientGUI.__allWidgets['log'].warn_msg('...... Reloading a model .......')
        self.unknown_res = self.yoloServer.UnknownResult()
        if len(self.unknown_res) != 0:
            clientGUI.__allWidgets['log'].ok_msg("Unknown Found :"+str(len(self.unknown_res)))
        self.__loadModel()
    def __swapModelYOLO(self,*kw):
        selected = self.selected_model.get()
        if selected != "/// LOCAL ///" and selected != "/// SERVER ///"  :
            if not self.fileHandler.checkModel(selected):
                top = "New Server Model Selected !!!"
                msg = "Do you want to download %s from YOLO-server ?" % selected
                if messagebox.askokcancel(top,msg):
                    print('loading Model...')
                    self.yoloServer.downloadServerModel(
                        self.fileHandler.getModelPath(),
                        selected
                    )
                    self.__swapModelMSG(selected)
                else:
                    print("New Model not found .Using old one instead")
                    self.selected_model.set(self.fileHandler.getCurrentModel())
            else:
                self.__swapModelMSG(selected)
    def __swapModelMSG(self,selected):
        top = "New Model Selected !!!"
        msg = "Do you want to use %s now ?" % selected
        if messagebox.askokcancel(top,msg):
            print('reloading model...')
            task = threading.Thread(target=self.__loadModel)
            task.start()
            self.fileHandler.setCurrentModel(selected)
        else:
            print('model swap cancel. using old one instead')
            self.selected_model.set(self.fileHandler.getCurrentModel())
    def __time_cooldown(self):
        global UNKNOWN_AVAILABLE,IS_VDO_STOP
        while not IS_VDO_STOP: 
            clientGUI.__allWidgets['log'].info_msg("unknown found ! Begin to cooldown...")
            time.sleep(self.cooldown_time)
            UNKNOWN_AVAILABLE  = True
            clientGUI.__allWidgets['log'].info_msg("cooldown over . getting new unknown...")
    def __time_trigger(self):
        global UNKNOWN_AVAILABLE,IS_VDO_STOP
        unknown_path = self.fileHandler.getUnknownPath()
        self.yoloServer.prepareUnknown(unknown_path)
        server_status = self.yoloServer.test_server()
        num =0
        while not IS_VDO_STOP and server_status:
            if os.path.exists(unknown_path) and UNKNOWN_AVAILABLE:
                UNKNOWN_AVAILABLE = False
                send_one = threading.Thread(target=self.yoloServer.unknown)
                send_one.start()
                self.__time_cooldown()


    def __clear_mode(self):
        clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets.get('view_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets.get('cap_isOn').configure(image=clientGUI.__allImages.get('isOff'))
    def __swap_mode(self,btn,btn_status):
        if btn_status:
            btn.configure(image=clientGUI.__allImages.get('isOn'))
        else :
            btn.configure(image=clientGUI.__allImages.get('isOff'))
    def __chang_mode_color(self,btn,status=''):
        status = status.lower()
        if status == 'on':
            btn.configure(image=clientGUI.__allImages.get('isOn'))
        elif status == 'off':
            btn.configure(image=clientGUI.__allImages.get('isOff'))
        elif status == 'warn':
            btn.configure(image=clientGUI.__allImages.get('isWarn'))
    def __default_screen(self):
        pass
    
    def __detect_btn(self):
        global IS_VDO_CREATED,IS_VDO_STOP
        self.__clear_mode()
        clientGUI.__allModes['detect'] = not clientGUI.__allModes['detect']
        self.__swap_mode(clientGUI.__allWidgets['detect_isOn'],clientGUI.__allModes['detect'])

        if IS_VDO_CREATED :
            if clientGUI.__allModes['detect']:
                task = threading.Thread(target=self.__detectProcess)
                task.start()
            else :
                IS_VDO_STOP = True
                self.__default_screen()
                task = threading.Thread(target=self.__stopAndReloadliveYOLO)
                task.start()
    def __view_btn(self):
        self.__clear_mode()
        clientGUI.__allWidgets.get('view_isOn').configure(image=clientGUI.__allImages.get('isOn'))
        clientGUI.__allWidgets.get('log').info_msg('////////// VIEW MODE //////////')
    def __cap_btn(self):
        self.__clear_mode()
        clientGUI.__allWidgets.get('cap_isOn').configure(image=clientGUI.__allImages.get('isOn'))
        clientGUI.__allWidgets.get('log').info_msg('////////// CAPTURE MODE //////////')

    #Public function
    def pre_start(self):
        #pre_load_2 = threading.Thread(target=self.__checkLogin)
        #pre_load_2.start()
        pre_load_1 = threading.Thread(target=self.__checkServer)
        pre_load_1.start()
        pre_load_3 = threading.Thread(target=self.__loadModel)
        pre_load_3.start()
        main_gui = threading.Thread(target=self.mainloop())
        main_gui.start()

def runApp(ver,ser):
    program = clientGUI(ver,ser)
    program.pre_start()