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
#Client Screen handler
class clientScreen(Label):
    def __init__(self, master=None,**kw):
        super().__init__(master=master,**kw)
    
    def detectMode(self):
        pass

##############################################################
#Main Application
class clientGUI(Tk):
    __allImages = {}
    __allWidgets = {
        'log' : clientLog(),
        'screen' : clientScreen()
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
        clientGUI.__allWidgets['screen'] = clientScreen(self,image=clientGUI.__allImages['screen_img'])
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

    def __loadModel(self):
        global IS_VDO_CREATED,MODEL_PATH
        start = time.time()
        try:
            print("load model")
            clientGUI.__allWidgets.get('log').warn_msg("...Preparing Camera && YOLOv5 model...")
            prepareYolo(MODEL_PATH)
            clientGUI.__allWidgets.get('log').ok_msg("...Camera and YOLOv5 is ready...")
        except:
            clientGUI.__allWidgets.get('log').error_msg("### Error loading camera && YoloV5 ###")
            print('error loading model')
            IS_VDO_CREATED = False
        else:
            clientGUI.__allWidgets.get('log').ok_msg("Time used : (%.2fs)" % (time.time()-start))
            print("Time used : (%.2fs)" % (time.time()-start))
            IS_VDO_CREATED = True   
    # private Function
    def __loadGUIphoto(self):
        clientGUI.__allImages['icon'] = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"),master=self)
        clientGUI.__allImages['screen_img'] = ImageTk.PhotoImage(Image.new('RGB',(480,360)),master=self)
        clientGUI.__allImages['detect'] = ImageTk.PhotoImage(Image.open("gui_data/cap.png").resize((64,64)),master=self)
        clientGUI.__allImages['view'] = ImageTk.PhotoImage(Image.open("gui_data/view_mode.png").resize((64,64)),master=self)
        clientGUI.__allImages['cap'] = ImageTk.PhotoImage(Image.open("gui_data/capture_mode.png").resize((64,64)),master=self)
        clientGUI.__allImages['isOn'] = ImageTk.PhotoImage(Image.new('RGB',(64,20),'#22FF00'),master=self)
        clientGUI.__allImages['isOff'] = ImageTk.PhotoImage(Image.new('RGB',(64,20)),master=self)
    def __clear_mode(self):
        clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets.get('view_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets.get('cap_isOn').configure(image=clientGUI.__allImages.get('isOff'))
    def __detect_btn(self):
        self.__clear_mode()
        clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages.get('isOn'))
        clientGUI.__allWidgets.get('log').info_msg('////////// DETECTION MODE //////////')
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

def runApp(ver):
    program = clientGUI(ver)
    program.pre_start()