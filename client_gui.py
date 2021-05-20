import threading,cv2
from PIL import Image,ImageTk
from tkinter import Label,Button,StringVar,Tk
from tkinter.ttk import Combobox
from mygui_detect import prepareYolo,runYolo
from client_backend import *
# don't forget to remove fake initialize value in clientGUI
# don't forget to remove default value that in a part of tkinter 
# they all mess up tkinter internal function again

# might need to move global variable inside clientGUI
# don't know why but it should look more organized by putting everything essential in one place
###### Status Variable #########
IS_VDO_CREATED = False
IS_VDO_STOP = False
UNKNOWN_AVAILABLE = True
###### Status Variable #########
###### Regular Variable #########
OBJ_COUNT = {
    'current' : 0,
    'last' : 0,
    'unknown' : 0
}
###### Regular Variable #########
#Main Application's GUI building wil Tkinter
class clientGUI(Tk):
    __allImages = {}
    __allWidgets = {}
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
        self.unk_pos = 0
        self.raw_img = 0
        self.view_temp = 0

        self.modelList = self.fileHandler.getListLocalModels()
        self.objCount = self.fileHandler.getCount()
        self.regis_status,self.user_info = self.fileHandler.getUserInfo()


        self.__buildGUI(VERSION)

    ############### private Function #############################
    def __buildGUI(self,VERSION):
        self.__loadGUIphoto()
        self.view_temp = clientGUI.__allImages['screen_img']
        self.selected_model = StringVar(self)
        self.selected_model.set(self.fileHandler.getCurrentModel())

        self.title("YOLO-client v"+VERSION)
        self.geometry("800x600")
        self.resizable(width=False, height=False)
        self.iconphoto(False,clientGUI.__allImages['icon'])

        # build components (text,button,log,screen ETC.)
        clientGUI.__allWidgets['count'] = Label(self,text="Today Count : "+str(self.objCount))
        clientGUI.__allWidgets['screen'] = Label(self,image=clientGUI.__allImages['screen_img'])
        clientGUI.__allWidgets['screen-border'] = Label(self,image=clientGUI.__allImages['green_border'])
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
            isDeviceRegister=self.regis_status,
            userInfo=self.user_info,
            register_img = clientGUI.__allImages['Register'],
            api = self.yoloServer,
            filehandler= self.fileHandler
            )
        clientGUI.__allWidgets['cap_obj'] = input_box(self,'Object Name')
        
        # config style 
        clientGUI.__allWidgets['count'].config(font=('tahoma',24))
        clientGUI.__allWidgets['cap_obj'].config(font=('tahoma',18))
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
        clientGUI.__allWidgets['cap_obj'].place_forget()

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
        clientGUI.__allImages['green_border'] = ImageTk.PhotoImage(Image.new('RGB',(7,360),'#7CFC00'),master=self)
    def __checkLogin(self):
        if self.__checkServer() :
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
            return True
        else :
            clientGUI.__allWidgets['log'].info_msg('YOLO-server is down')
            clientGUI.__allWidgets['log'].warn_msg('Check your internet connection and restart YOLO-client')
            return False
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

            if temp_count > OBJ_COUNT['last']:
                OBJ_COUNT['current'] += (temp_count - OBJ_COUNT['last'])
            OBJ_COUNT['last'] = temp_count
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
            clientGUI.__allWidgets.get('detect').config(state='disabled')
            clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages['isWarn'])
            clientGUI.__allWidgets['model'].config(state='disabled')
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
                    clientGUI.__allWidgets.get('detect').config(state='normal')
                    clientGUI.__allWidgets['model'].config(state='readonly')
                    clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages['isOff'])
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
            clientGUI.__allWidgets.get('detect').config(state='normal')
            clientGUI.__allWidgets['model'].config(state='readonly')
            clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages['isOff'])
    def __time_cooldown(self):
        global UNKNOWN_AVAILABLE
        clientGUI.__allWidgets['log'].info_msg("unknown found ! Begin to cooldown...")
        time.sleep(self.cooldown_time)
        UNKNOWN_AVAILABLE  = True
        clientGUI.__allWidgets['log'].info_msg("cooldown over . getting new unknown...")
    def __time_trigger(self):
        global UNKNOWN_AVAILABLE,IS_VDO_STOP
        unknown_path = self.fileHandler.getUnknownPath()
        self.yoloServer.prepareUnknown(unknown_path)
        server_status = self.yoloServer.test_server()
        while not IS_VDO_STOP :
            if os.path.exists(unknown_path) and UNKNOWN_AVAILABLE:
                UNKNOWN_AVAILABLE = False
                send_one = threading.Thread(target=self.yoloServer.unknown)
                send_one.start()
                self.__time_cooldown()
    #view mode process
    def __getUnknownRes(self):
        for i in self.yoloServer.UnknownResult():
            self.unknown_res.append(i)
    def __hoverIn(self,*kw):
        self.activate_view = True
        clientGUI.__allWidgets['screen-border'].place(relx=0.001,rely=0.1)
    def __hoverOut(self,*kw):
        self.activate_view = False
        clientGUI.__allWidgets['screen-border'].place_forget()
    def __swipeLeft(self,*kw):
        if self.activate_view :
            print('going left')
            self.unk_pos-=1
            if self.unk_pos < 0:
                self.unk_pos = len(self.unknown_res)-1
            self.__base64ToImageTk()
            clientGUI.__allWidgets['screen'].configure(image=self.view_temp)
    def __swipeRight(self,*kw):
        if self.activate_view :
            print('going Right')
            self.unk_pos+=1
            if self.unk_pos > len(self.unknown_res)-1 :
                self.unk_pos = 0
            self.__base64ToImageTk()
            clientGUI.__allWidgets['screen'].configure(image=self.view_temp)
    def __base64ToImageTk(self):
        buff = BytesIO(self.unknown_res[self.unk_pos])
        result = Image.open(buff).resize((480,360))
        res2 = ImageTk.PhotoImage(image=result,master=self,size=(480,360))
        self.view_temp = res2
    #capture mode process
    def __cv2ToImageTk(self,frame):
        imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imageVDO2 = Image.fromarray(imageVDO).resize((480,360))
        imageVDO3 = ImageTk.PhotoImage(image=imageVDO2)
        clientGUI.__allWidgets['screen'].configure(image=imageVDO3)
        clientGUI.__allWidgets['screen'].update()
        self.raw_img = imageVDO2
    def __capture_VDO(self):
        cap_cam = cv2.VideoCapture(0)
        while True:
            _,frame = cap_cam.read()
            self.__cv2ToImageTk(frame)
            if not clientGUI.__allModes['capture'] or cv2.waitKey(1) & 0xFF == ord('x'):
                cap_cam.release()
                break
    def __sendRawImage(self):
        _,info = self.fileHandler.getUserInfo()
        raw_path = self.fileHandler.getRawPath()
        all_raw = self.fileHandler.getAllRaw()
        for idx,raw in enumerate(all_raw):
            try:
                self.yoloServer.send_raw1(info['factory'],raw_path,raw)
                clientGUI.__allWidgets.get('log').ok_msg(raw+' had been sent to YOLO-server (%s/%s)' 
                    %(str(idx+1),str(len(all_raw))))
            except Exception as e:
                print(e)
                clientGUI.__allWidgets.get('log').error_msg('an Error occured while sending '+raw+
                    ' to YOLO-server (%s/%s)' %(str(idx+1),str(len(all_raw))))
    def __activateRawImage(self,*kw):
        task = threading.Thread(target=self.__sendRawImage)
        task.start()
    def __capture_one(self,name='something'):
        save_path =self.fileHandler.getRawPath()
        num = len(os.listdir(save_path))+1
        new_name = clientGUI.__allWidgets['cap_obj'].get()
        if new_name == '' or new_name == 'Object Name':
            self.raw_img.save(save_path+'Blank_'+str(num)+'.jpg')
        else :
            self.raw_img.save(save_path+new_name+'_'+str(num)+'.jpg')
        clientGUI.__allWidgets.get('log').ok_msg("New raw image saved ! (%s/50)" % str(num))
        if num==50 :
            clientGUI.__allWidgets.get('log').warn_msg("There already enough raw images to be used.")
            clientGUI.__allWidgets.get('log').ok_msg("Hover around on black screen to send raw images")
            clientGUI.__allWidgets.get('log').ok_msg("Right Click to send raw images")
            clientGUI.__allWidgets['screen'].bind('<Button-3>',self.__activateRawImage)
    def __getRawImage(self,*kw):
        if self.activate_view:
            self.__capture_one()
    #other process
    def __clear_mode(self):
        clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets.get('view_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets.get('cap_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets['model'].config(state='disabled')
    def __swap_mode(self,btn,btn_status):
        if btn_status:
            btn.configure(image=clientGUI.__allImages.get('isOn'))
        else :
            btn.configure(image=clientGUI.__allImages.get('isOff'))
    def __change_mode_color(self,btn,status=''):
        status = status.lower()
        if status == 'on':
            btn.configure(image=clientGUI.__allImages.get('isOn'))
        elif status == 'off':
            btn.configure(image=clientGUI.__allImages.get('isOff'))
        elif status == 'warn':
            btn.configure(image=clientGUI.__allImages.get('isWarn'))
    
    def __detect_btn(self):
        global IS_VDO_CREATED,IS_VDO_STOP
        self.__clear_mode()
        clientGUI.__allModes['detect'] = not clientGUI.__allModes['detect']
        self.__swap_mode(clientGUI.__allWidgets['detect_isOn'],clientGUI.__allModes['detect'])
        clientGUI.__allWidgets['model'].config(state='readonly')
        if IS_VDO_CREATED :
            if clientGUI.__allModes['detect']:
                clientGUI.__allWidgets['view'].configure(state='disabled')
                clientGUI.__allWidgets['cap'].configure(state='disabled')
                task = threading.Thread(target=self.__detectProcess)
                task.start()
            else :
                IS_VDO_STOP = True
                clientGUI.__allWidgets['view'].configure(state='normal')
                clientGUI.__allWidgets['cap'].configure(state='normal')
                task = threading.Thread(target=self.__stopAndReloadliveYOLO)
                task.start()
    def __view_btn(self):
        self.__clear_mode()
        clientGUI.__allModes['view'] = not clientGUI.__allModes['view']
        if clientGUI.__allModes['view']:
            clientGUI.__allWidgets.get('view_isOn').configure(image=clientGUI.__allImages.get('isOn'))
            clientGUI.__allWidgets.get('log').info_msg('////////// VIEW MODE //////////')
            clientGUI.__allWidgets.get('log').info_msg('Hover around on black screen to activate swiping')
            clientGUI.__allWidgets.get('log').info_msg(' <<< Left Click || Right Click >>')

            self.__getUnknownRes()
            clientGUI.__allWidgets.get('log').ok_msg('There are %i images for unknown result' % len(self.unknown_res))

            clientGUI.__allWidgets['screen'].bind('<Enter>',self.__hoverIn)
            clientGUI.__allWidgets['screen'].bind('<Leave>',self.__hoverOut)
            clientGUI.__allWidgets['screen'].bind('<Button-1>',self.__swipeLeft)
            clientGUI.__allWidgets['screen'].bind('<Button-3>',self.__swipeRight)
            clientGUI.__allWidgets['detect'].configure(state='disabled')
            clientGUI.__allWidgets['cap'].configure(state='disabled')
        else :
            clientGUI.__allWidgets['screen'].unbind('<Enter>')
            clientGUI.__allWidgets['screen'].unbind('<Leave>')
            clientGUI.__allWidgets['screen'].unbind('<Button-1>')
            clientGUI.__allWidgets['screen'].unbind('<Button-3>')
            clientGUI.__allWidgets['detect'].configure(state='normal')
            clientGUI.__allWidgets['cap'].configure(state='normal')
            clientGUI.__allWidgets['screen'].configure(image=clientGUI.__allImages['screen_img'])
            clientGUI.__allWidgets.get('log').info_msg('////////// VIEW MODE END //////////')
    def __cap_btn(self):
        self.__clear_mode()
        clientGUI.__allModes['capture'] = not clientGUI.__allModes['capture']

        if clientGUI.__allModes['capture']:
            clientGUI.__allWidgets.get('cap_isOn').configure(image=clientGUI.__allImages.get('isOn'))
            clientGUI.__allWidgets.get('log').info_msg('////////// CAPTURE MODE //////////')
            clientGUI.__allWidgets.get('log').info_msg('Hover around on display screen to activate on-screen click')
            clientGUI.__allWidgets.get('log').info_msg('Left Click to capture raw image')

            clientGUI.__allWidgets['screen'].bind('<Enter>',self.__hoverIn)
            clientGUI.__allWidgets['screen'].bind('<Leave>',self.__hoverOut)
            clientGUI.__allWidgets['screen'].bind('<Button-1>',self.__getRawImage)
            clientGUI.__allWidgets['detect'].configure(state='disabled')
            clientGUI.__allWidgets['view'].configure(state='disabled')

            clientGUI.__allWidgets['cap_obj'].place(relx=0.63,rely=0.4)

            self.__capture_VDO()
        else :
            clientGUI.__allWidgets['screen'].unbind('<Enter>')
            clientGUI.__allWidgets['screen'].unbind('<Leave>')
            clientGUI.__allWidgets['screen'].unbind('<Button-1>')
            clientGUI.__allWidgets['screen'].unbind('<Button-3>')
            clientGUI.__allWidgets['detect'].configure(state='normal')
            clientGUI.__allWidgets['view'].configure(state='normal')
            clientGUI.__allWidgets['screen'].configure(image=clientGUI.__allImages['screen_img'])

            clientGUI.__allWidgets['cap_obj'].place_forget()
            clientGUI.__allWidgets.get('log').info_msg('////////// CAPTURE MODE END //////////')
    #Public function
    def pre_start(self,removeTextFile = False):
        pre_load_2 = threading.Thread(target=self.__checkLogin)
        pre_load_2.start()
        pre_load_3 = threading.Thread(target=self.__loadModel)
        pre_load_3.start()
        main_gui = threading.Thread(target=self.mainloop())
        main_gui.start()

def runApp(ver,ser='127.0.0.1'):
    program = clientGUI(ver,ser)
    program.pre_start()