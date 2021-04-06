###############################################
#                                             #
# Only work on Linux . i didn't do flexibility coding yet. #
#                                             #
############################################### 

from flask import Flask,make_response,request,jsonify
from flask_mongoengine import MongoEngine
import os
import subprocess
import time
import cv2
import shutil
import base64
from PIL import Image
from io import BytesIO
from mygui_detect import prepareYolo,runYolo

app = Flask(__name__)


database_name = "Images"
mongodb_password = "Com75591;"

DB_URI = "mongodb+srv://ikanaporn:{}@cluster0.x8seg.mongodb.net/{}?retryWrites=true&w=majority".format(
    mongodb_password, database_name
)
FOLDER_IMAGE_UPLOADS = "/Users/mai/SeniorProject/flaskwebapi/env/assets/images"

app.config["MONGODB_HOST"] = DB_URI
app.config["IMAGE_UPLOADS"] = FOLDER_IMAGE_UPLOADS

db = MongoEngine()
db.init_app(app)

class Unknown(db.Document):

   ids = db.IntField()
   filename = db.StringField()
   times = db.IntField()
   file = db.ImageField(thumbnail_size=(256,256))

   def to_json(self):

      return {

         "ids": self.ids,
         "filename": self.filename,
         "times": self.times,
         "file": self.file,

      }
class Labeled(db.Document):
   ids = db.StringField()
   filename = db.StringField()
   identify = db.StringField()
   lebeledBy = db.StringField()

   def to_json(self):

      return {

         "ids": self.ids,
         "filename": self.filename,
         "identify": self.identify,
         "lebeledBy": self.lebeledBy,

      }
# it's work -  
@app.route('/api/uploadunknown', methods=['POST'])
def api_upload_unknown():
   if request.files:
         save_path = os.getcwd()+'/api_unknown/'
         num = len(os.listdir(save_path+'new/'))+1
         file = request.files["image"] 
         filename = "new_unknown_"+str(num)
         file.save(save_path+"new/"+filename+".jpg")

         t0 = time.time()
         prepareYolo("./mine/yolov5s.pt",True,save_path+"new/"+filename+".jpg")
         _,res = runYolo(0)
         image = cv2.cvtColor(res,cv2.COLOR_BGR2RGB)
         image2 = Image.fromarray(image).resize((480,360))
         print(image2)
         image2.save(save_path+"res/"+filename+".jpg")
         #unknown1 = Unknown(ids=num,filename=filename,times=time,file=file)
         #unknown1.save()

         buff = BytesIO()
         image2.save(buff, format="JPEG")
         img_str = base64.b64encode(buff.getvalue()).decode('utf-8')

         return jsonify(
            result="Found Object",
            image=img_str
         )


@app.route('/api/dbImages', methods=['POST'])
def db_images():
   lebeled1 = Labeled(ids="0001",filename="mitpol0.png",identify="bottle",lebeledBy="admin1")
   lebeled2 = Labeled(ids="0002",filename="mitpol1.png",identify="bottle",lebeledBy="admin2")
   
   lebeled1.save()
   lebeled2.save()
   return "Created"

@app.route('/api/labeled', methods=['GET','POST'])
def api_lebeled():
   pass

@app.route('/api/labeled/<ids>', methods=['POST'])
def api_each_labeled():
   pass

@app.route('/',methods=['GET'])
def index():
   return "Something is coming..."
if __name__ == '__main__':
   subprocess.call("clear",shell=True)
   if os.path.exists('./api_unknown/new') :
      shutil.rmtree('./api_unknown/new') 
   os.makedirs('./api_unknown/new') 
   if os.path.exists('./api_unknown/res') :
      shutil.rmtree('./api_unknown/res') 
   os.makedirs('./api_unknown/res') 
   app.run(debug=True,host='0.0.0.0',port=80)