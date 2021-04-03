from flask import Flask,make_response,request
from flask_mongoengine import MongoEngine
import os
import subprocess


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
        num = len(os.listdir(save_path))+1
        file = request.files["image"] 
        filename = "new_unknown_"+str(num)
        time = 0

        file.save(os.path.join(app.config["IMAGE_UPLOADS"], save_path +filename+".jpg"))
        
        unknown1 = Unknown(ids=num,filename=filename,times=time,file=file)
        
        unknown1.save()

        subprocess.call("python3 detect.py "+ 
        "--source " +save_path+filename+".jpg " +
        "--project api_unknown "+
        "--name yolo_result"
        ,shell=True)

        return "new_unknown_"+str(num)+".jpg have been Saved!"


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
   return "Something is coming"
if __name__ == '__main__':
    subprocess.call("clear",shell=True)
    app.run(debug=True,host='0.0.0.0',port=80)