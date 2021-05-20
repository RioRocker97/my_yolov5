###############################################
#                                             #
# Test any library if i have doubt            #
#                                             #
############################################### 
from datetime import datetime
import os
from mygui_detect import prepareYolo
if __name__ == '__main__':
    """
    if os.path.exists('./gui_data/set_model.chang'):
        r = open('./gui_data/set_model.chang')
        info = r.readlines()
        for obj in info:
            print(obj.split("\n")[0])
        r.close()
    """
    prepareYolo('./mine/35obj.pt',loadFromImage=True,imageSource='./mine/cow.jpg')

