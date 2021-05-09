import pycurl,os,shutil,time,json,base64
from tkinter import Label,messagebox,Button,Entry,scrolledtext,LabelFrame
from io import BytesIO

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
        except Exception as e:
            print("error at calling API (Test-Server)")
            print(type(e))
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
                print("Register success .")
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
    def send_raw1(self,info,save_path,raw):
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
            "API_TOKEN:"+ self.token,
            "FACTORY:"+ info,
            "OBJ-NAME:"+raw.split('_')[0]
            ])
        self.api.setopt(pycurl.WRITEDATA,self.rep)
        t0 = time.time()
        # will do API's respone handling later
        try:
            self.api.perform()
            total_time = time.time()-t0
            if(str(self.api.getinfo(pycurl.HTTP_CODE)) == '200'):
                print("Send Raw Image Success !")
                os.remove(save_path+raw)
            else:
                print("Server is DOWN !")
        except:
            print("error at calling API (send raw)")
        else:
            self.api.close()
            self.rep.close()
    def getServerModel(self,list_model=[]):
        list_model.append('/// SERVER ///')
        self.rep = BytesIO()
        self.api = pycurl.Curl()
        self.api.setopt(pycurl.URL,self.server+"/api/listModel")
        self.api.setopt(pycurl.WRITEDATA,self.rep)
        self.api.setopt(pycurl.HTTPHEADER,
        ["API_TOKEN:"+ self.token])
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
        self.currModelPath = "./mine/default.pt"
        self.currModel = "default"

        if os.path.exists(self.folder['UnknownData']) :
            shutil.rmtree(self.folder['UnknownData'])
        if os.path.exists(self.folder['RawData']) :
            shutil.rmtree(self.folder['RawData'])

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
    def getRawPath(self):
        return self.folder['RawData']
    def getAllRaw(self):
        return os.listdir(self.folder['RawData'])
    
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
        if self.get() != self.value or self.get() != 'Password':
            self.delete('0','end')
        self.config(show='')
    def __leave_pass(self,*kw):
        self.__leave()
        if self.get() != '' and self.get() != 'Password':
            self.config(fg="#228B22") 
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

        self.configure(font=('TkFixedFont',10),background="black")
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
            self.__makeFrame()
        else:
            self.config(text='!!! Unregistered !!!')

            self.factory = input_box(self,'Factory Name')
            self.device = input_box(self,'Device Name')
            self.secret = input_box(self,'Password',True)
            self.register_btn = Button(self,image=register_img,command=self.__doRegister)

            self.factory.config(font=('tahoma',14))
            self.device.config(font=('tahoma',14))
            self.secret.config(font=('tahoma',14))

            self.factory.place(relx=0.02,rely=0.1)
            self.device.place(relx=0.02,rely=0.4)
            self.secret.place(relx=0.02,rely=0.7)
            self.register_btn.place(relx=0.78,rely=0.0)
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
            self.api.login(self.device.getValue(),self.secret.getValue())
            self.fileHandler.setUserInfo(self.userInfo)
            self.__clearFrame()
            _,self.userInfo=self.fileHandler.getUserInfo()
            self.__makeFrame()
            messagebox.showinfo("Register","Registeration for "+self.userInfo['user']+" completed !")
        else :
            print('Register canceled')
    def __makeFrame(self):
            self.configure(text="Device Info")
            factory = Label(self,text="Factory : "+self.userInfo['factory'])
            deviceID = Label(self,text="Device : "+self.userInfo['user'])
            server_status = Label(self,text="YOLO-Server : Online")

            factory.config(font=('tahoma',18))
            deviceID.config(font=('tahoma',18))
            server_status.config(font=('tahoma',18))

            factory.place(relx=0.02,rely=0.01)
            deviceID.place(relx=0.02,rely=0.25)
            server_status.place(relx=0.02,rely=0.5)
    def __clearFrame(self):
            self.factory.place_forget()
            self.device.place_forget()
            self.secret.place_forget()
            self.register_btn.place_forget()

