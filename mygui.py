import tkinter
from PIL import ImageTk,Image 
import logging
import threading
from tkinter import scrolledtext 

# TextHandler Credited to https://gist.github.com/moshekaplan
class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tkinter.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tkinter.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

def detect():
    print("Now Detecting some object...")

def stop_detect():
    print("Now Stopping Detecting")

def collect_data():
    print("Now Showing new image data to be trained in this model")

def retrain():
    print("Now Re-training my model...")


def my_gui():
    print("This is my GUI ")
    frame = tkinter.Tk()
    frame.title('IOT-Project')
    frame.geometry("1000x600")
    example = ImageTk.PhotoImage(Image.open("gui_data/goose.png"))
    icon = ImageTk.PhotoImage(Image.open("gui_data/icon.jpg"))
    detect_frame= tkinter.Frame(frame)
    train_frame= tkinter.Frame(frame)

    # Detect section
    label1 = tkinter.Label(detect_frame,text="Detect Zone")
    label1.config(font=("Courier", 36))
    box1 = tkinter.Label(detect_frame,image=example,borderwidth=5,relief='solid')
    btn1 = tkinter.Button(detect_frame,text="Detect",command = detect,font=("Courier", 16))
    btn2 = tkinter.Button(detect_frame,text="Stop",command = stop_detect,font=("Courier", 16))

    #Pack every widget in detect_frame
    label1.pack()
    box1.pack(pady="30")
    btn1.pack(side=tkinter.LEFT,padx="10",ipadx="20",ipady="10")
    btn2.pack(side=tkinter.LEFT,padx="10",ipadx="20",ipady="10")

    # Train section
    label2 = tkinter.Label(train_frame,text="Train Zone")
    label2.config(font=("Courier", 36))
    box2 = tkinter.Label(train_frame,image=example,borderwidth=5,relief='solid')
    btn3 = tkinter.Button(train_frame,text="Show Data",command = collect_data,font=("Courier", 16))
    btn4 = tkinter.Button(train_frame,text="Re-Train",command = retrain,font=("Courier", 16))

    #Pack every widgets in train_frame
    label2.pack()
    box2.pack(pady="30")
    btn3.pack(side=tkinter.LEFT,padx="10",ipadx="20",ipady="10")
    btn4.pack(side=tkinter.LEFT,padx="10",ipadx="20",ipady="10")

    # My TextHandler
    scroll = scrolledtext.ScrolledText(frame,state='disabled')
    scroll.configure(font='TkFixedFont')

    text_handler = TextHandler(scroll)
    logger = logging.getLogger()
    logger.addHandler(text_handler)

    #logger.debug('debug message')
    #logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    detect_frame.place(bordermode=tkinter.INSIDE,relheight=0.8,relwidth=0.5)
    train_frame.place(bordermode=tkinter.INSIDE,relheight=0.8,relwidth=0.5,relx=0.5)
    scroll.place(bordermode=tkinter.INSIDE,relheight=0.2,relwidth=0.7,rely=0.8)

    frame.iconphoto(False,icon)
    frame.mainloop()

if __name__ == '__main__':
    my_gui() 