import threading,cv2,os,time
from PIL import Image,ImageTk
from tkinter import Label,scrolledtext,Button,OptionMenu,StringVar,LabelFrame,Entry,Tk
from mygui_detect import prepareYolo,runYolo

# don't forget to remove fake initialize value in clientGUI
# don't forget to remove default value that in a part of tkinter 
# they all mess up tkinter internal function again
###### Status Variable #########
IS_VDO_CREATED = False
IS_VDO_STOP = False
MODEL_PATH = "./mine/cap_unk.pt"
###### Status Variable #########
###### Regular Variable #########
OBJ_COUNT = {
    'current' : 0,
    'last' : 0,
    'unknown' : 0
}
###### Regular Variable #########
#input box with placeholder
class input_box(Entry):
    def __init__(self,placeholder=''):
        super().__init__()
        self.bind('<Enter>',self.focus_in)
        self.bind('<Leave>',self.focus_out)
        self.placeholder = placeholder

    def focus_in(self,*kw):
        print("go in")
        self.delete('0','end')
    def focus_out(self,*kw):
        print("go out")
        self.insert(0,self.placeholder)   
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
    def __init__(self, master=None,**kw):
        super().__init__(master=master,**kw)

        self.factory = Label(self,text="Somewhere 123")
        self.deviceID = Label(self,text="SomeDevice 456")
        self.server_status = Label(self,text="YOLO-Server : Online")
        #test_box = input_box(frame,"ABC")

        self.factory.config(font=('tahoma',14))
        self.deviceID.config(font=('tahoma',14))
        self.server_status.config(font=('tahoma',14))

        self.factory.place(relx=0.02,rely=0.01)
        self.deviceID.place(relx=0.02,rely=0.2)
        self.server_status.place(relx=0.02,rely=0.4)

##############################################################
#Main Application
class clientGUI(Tk):
    __allImages = {}
    __allWidgets = {
        #'log' : clientLog(),
        #'screen' : Label(),
        #'detect' : Button(),
        #'detect_isOn' : Label()
    }
    __allModes ={
        'detect' : False,
        'view' : False,
        'capture' : False
    }
    def __init__(self,VERSION):
        super().__init__()
        self.__loadGUIphoto()
        selected_model = StringVar(self)
        selected_model.set("Something")

        self.title("YOLO-client v"+VERSION)
        self.geometry("800x600")
        self.resizable(width=False, height=False)
        self.iconphoto(False,clientGUI.__allImages['icon'])

        # build components (text,button,log,screen ETC.)
        count_label = Label(self,text="Today Count : 000")
        clientGUI.__allWidgets['screen'] = Label(self,image=clientGUI.__allImages['screen_img'])
        clientGUI.__allWidgets['log'] = clientLog(self,state='disabled',borderwidth=10)
        clientGUI.__allWidgets['detect'] = Button(self,command=self.__detect_btn,image=clientGUI.__allImages['detect'])
        clientGUI.__allWidgets['view'] = Button(self,command=self.__view_btn,image=clientGUI.__allImages['view'])
        clientGUI.__allWidgets['cap'] = Button(self,command=self.__cap_btn,image=clientGUI.__allImages['cap'])
        clientGUI.__allWidgets['detect_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['view_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['cap_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['model'] = OptionMenu(self,selected_model,['1','2'])
        suggestion_label = Label(self,text="Recommend Model : \n ABC-123")
        clientGUI.__allWidgets['user_info'] = clientUserInfo(self,text="Device Info")
        
        # config style 
        count_label.config(font=('tahoma',24))
        suggestion_label.config(font=('tahoma',20))
        clientGUI.__allWidgets['model'].configure(width="15",font=("tahoma",18))

        # place components
        count_label.place(relx=0.01,rely=0.01)

        clientGUI.__allWidgets['screen'].place(relx=0.01,rely=0.1)

        clientGUI.__allWidgets['detect'].place(relx=0.63,rely=0.01)
        clientGUI.__allWidgets['view'].place(relx=0.77,rely=0.01)
        clientGUI.__allWidgets['cap'].place(relx=0.90,rely=0.01)
        clientGUI.__allWidgets['detect_isOn'].place(relx=0.63,rely=0.13)
        clientGUI.__allWidgets['view_isOn'].place(relx=0.77,rely=0.13)
        clientGUI.__allWidgets['cap_isOn'].place(relx=0.90,rely=0.13)

        clientGUI.__allWidgets['model'].place(relx=0.68,rely=0.2)
        suggestion_label.place(relx=0.65,rely=0.3)

        clientGUI.__allWidgets['log'].place(relx=0.01,rely=0.72,width=500,height=150)
        clientGUI.__allWidgets['user_info'].place(relx=0.64,rely=0.72,width=280,height=150)

    # private Function
    def __loadModel(self):
        global IS_VDO_CREATED,MODEL_PATH,IS_VDO_STOP
        start = time.time()
        model_name = MODEL_PATH.split('/')[2]

        clientGUI.__allWidgets.get('detect').config(state='disabled')
        clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages['isWarn'])
        try:
            clientGUI.__allWidgets.get('log').warn_msg("...Preparing Camera && YOLOv5 model...")
            clientGUI.__allWidgets.get('log').warn_msg("...Using Model : "+model_name)
            prepareYolo(MODEL_PATH)
        except:
            clientGUI.__allWidgets.get('log').error_msg("### Error loading camera && YoloV5 ###")
            clientGUI.__allWidgets.get('log').error_msg("### Plug in any camera and Restart YOLO-Client ###")
            IS_VDO_CREATED = False
        else:
            clientGUI.__allWidgets.get('log').ok_msg("...Camera and YOLOv5 is ready...")
            clientGUI.__allWidgets.get('log').ok_msg("Time used : (%.2fs)" % (time.time()-start))
            clientGUI.__allWidgets.get('detect').config(state='normal')
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
        clientGUI.__allImages['isOff'] = ImageTk.PhotoImage(Image.new('RGB',(64,20)),master=self)
    
    def __detectProcess(self):
        global IS_VDO_CREATED,IS_VDO_STOP
        clientGUI.__allWidgets['log'].warn_msg('////////// Detect Mode //////////')
        if IS_VDO_CREATED:
            clientGUI.__allWidgets['log'].ok_msg('.......... Begin Detection ............')
            live_yolo = threading.Thread(target=self.__liveYOLO)
            live_yolo.start()
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
        if IS_VDO_STOP:
            vdo_slot = clientGUI.__allImages['screen_img']
            clientGUI.__allWidgets['screen'].configure(image=vdo_slot)
    def __convertImageToTk(self,frame):
        imageVDO = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        imageVDO2 = Image.fromarray(imageVDO).resize((480,360))
        imageVDO3 = ImageTk.PhotoImage(image=imageVDO2,master=self)
        return imageVDO3
    def __stopAndReloadliveYOLO(self):
        clientGUI.__allWidgets['log'].warn_msg('...... Reload a model .......')
        self.__loadModel()
    
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
        pre_load_1 = threading.Thread(target=self.__loadModel)
        pre_load_1.start()
        
        main_gui = threading.Thread(target=self.mainloop())
        main_gui.start()

############
#program = clientGUI('V1.7.1 Alpha')
############

def runApp(ver):
    program = clientGUI(ver)
    program.pre_start()