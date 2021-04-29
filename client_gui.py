import threading,cv2,os,time
from PIL import Image,ImageTk
from tkinter import Label,scrolledtext,Button,OptionMenu,StringVar,LabelFrame,Entry,Tk
class clientGUI(Tk):
    __allImages = {}
    __allWidgets = {}
    def __init__(self,VERSION):
        super().__init__()
        self.loadGUIphoto()
        selected_model = StringVar(self)
        selected_model.set("Something")

        self.title("YOLO-client v"+VERSION)
        self.geometry("800x600")
        self.resizable(width=False, height=False)
        self.iconphoto(False,clientGUI.__allImages['icon'])

        # build components (text,button,log,screen ETC.)
        count_label = Label(self,text="Today Count : 000")
        clientGUI.__allWidgets['screen'] = Label(self,image=clientGUI.__allImages['screen_img'])
        clientGUI.__allWidgets['log'] = scrolledtext.ScrolledText(self,state='disabled',borderwidth=10)
        clientGUI.__allWidgets['detect'] = Button(self,command=self.__detect_btn,image=clientGUI.__allImages['detect'])
        clientGUI.__allWidgets['view'] = Button(self,command=self.__view_btn,image=clientGUI.__allImages['view'])
        clientGUI.__allWidgets['cap'] = Button(self,command=self.__cap_btn,image=clientGUI.__allImages['cap'])
        clientGUI.__allWidgets['detect_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['view_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['cap_isOn'] = Label(self,image=clientGUI.__allImages['isOff'])
        clientGUI.__allWidgets['model'] = OptionMenu(self,selected_model,['1','2'])
        suggestion_label = Label(self,text="Recommend Model : \n ABC-123")
        clientGUI.__allWidgets['user_info'] = self.device_info_box()
        
        # config style 
        count_label.config(font=('tahoma',24))
        suggestion_label.config(font=('tahoma',20))
        clientGUI.__allWidgets['log'].configure(font=('TkFixedFont',12),background="black")
        clientGUI.__allWidgets['log'].tag_config('info',foreground='#15A0CA')
        clientGUI.__allWidgets['log'].tag_config('warn',foreground='#DE9B00')
        clientGUI.__allWidgets['log'].tag_config('error',foreground='#DA3C15')
        clientGUI.__allWidgets['log'].tag_config('ok',foreground='#00F942')
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

    def loadGUIphoto(self):
        clientGUI.__allImages['icon'] = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"),master=self)
        clientGUI.__allImages['screen_img'] = ImageTk.PhotoImage(Image.new('RGB',(480,360)),master=self)
        clientGUI.__allImages['detect'] = ImageTk.PhotoImage(Image.open("gui_data/cap.png").resize((64,64)),master=self)
        clientGUI.__allImages['view'] = ImageTk.PhotoImage(Image.open("gui_data/view_mode.png").resize((64,64)),master=self)
        clientGUI.__allImages['cap'] = ImageTk.PhotoImage(Image.open("gui_data/capture_mode.png").resize((64,64)),master=self)
        clientGUI.__allImages['isOn'] = ImageTk.PhotoImage(Image.new('RGB',(64,20),'#22FF00'),master=self)
        clientGUI.__allImages['isOff'] = ImageTk.PhotoImage(Image.new('RGB',(64,20)),master=self)
    
    def device_info_box(self):
        frame = LabelFrame(self,text="Device Info")

        factory = Label(frame,text="Somewhere 123")
        deviceID = Label(frame,text="SomeDevice 456")
        server_status = Label(frame,text="YOLO-Server : Online")
        #test_box = input_box(frame,"ABC")

        factory.config(font=('tahoma',14))
        deviceID.config(font=('tahoma',14))
        server_status.config(font=('tahoma',14))

        factory.place(relx=0.02,rely=0.01)
        deviceID.place(relx=0.02,rely=0.2)
        server_status.place(relx=0.02,rely=0.4)
        #test_box.place(relx=0.02,rely=0.6)
        return frame

    def start(self):
        self.mainloop()
    
    def __clear_mode(self):
        clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets.get('view_isOn').configure(image=clientGUI.__allImages.get('isOff'))
        clientGUI.__allWidgets.get('cap_isOn').configure(image=clientGUI.__allImages.get('isOff'))
    def __detect_btn(self):
        self.__clear_mode()
        clientGUI.__allWidgets.get('detect_isOn').configure(image=clientGUI.__allImages.get('isOn'))
    def __view_btn(self):
        self.__clear_mode()
        clientGUI.__allWidgets.get('view_isOn').configure(image=clientGUI.__allImages.get('isOn'))
    def __cap_btn(self):
        self.__clear_mode()
        clientGUI.__allWidgets.get('cap_isOn').configure(image=clientGUI.__allImages.get('isOn'))
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