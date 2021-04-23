
import io
import jwt
import time
import cv2
import base64
import os
import shutil
import subprocess

from flask import Flask,make_response,request,jsonify
from flask_mongoengine import MongoEngine
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from functools import wraps
from datetime import datetime,timedelta
from PIL import Image
from io import BytesIO
from mygui_detect import prepareYolo,runYolo

app = Flask(__name__)

database_name = "API-Detection"
mongodb_password = "Com75591;"

DB_URI = "mongodb+srv://ikanaporn:{}@cluster0.x8seg.mongodb.net/{}?retryWrites=true&w=majority".format(
    mongodb_password, database_name
)
FOLDER_IMAGE_UPLOADS = "/Users/mai/SeniorProject/flaskwebapi/env/assets/images"
SINGLE_MODEL_TEST = "./mine/pen_only.pt"
app.config['SECRET_KEY']='Th1s1ss3cr3t'
app.config["MONGODB_HOST"] = DB_URI
app.config["IMAGE_UPLOADS"] = FOLDER_IMAGE_UPLOADS

db = MongoEngine()
db.init_app(app)

client = MongoClient("mongodb+srv://ikanaporn:{}@cluster0.x8seg.mongodb.net/{}?retryWrites=true&w=majority".format(
    mongodb_password, database_name
))

deviceCollection = client['device']

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
   filename = db.StringField(unique=True)
   imgfile = db.ImageField(thumbnail_size=(256,256))
   labelfile = db.FileField()
   identify = db.StringField()
   labeledby = db.StringField()

   def to_json(self):

      return {
         "ids": self.ids,
         "filename": self.filename,
         "imgfile" : self.imgfile,
         "labelfile" : self.labelfile,
         "identify": self.identify,
         "labeledby": self.labeledby,
      }
class Device(db.Document):
   ids = db.StringField(unique=True)
   username = db.StringField(unique=True)
   aType = db.StringField()
   factory = db.StringField(nullable=True)
   password = db.StringField(nullable=True)
   uniqueName = db.StringField(nullable=True)

   def to_json(self):

      return {

         "ids": self.ids,
         "username": self.username,
         "aType": self.aType,
         "factory": self.factory,
         "password": self.password,
         "uniqueName": self.uniqueName,

      }
class Model(db.Document):
   name = db.StringField()
   pathfile = db.StringField()

   def to_json(self):

      return {

         "name": self.name,
         "pathfile": self.pathfile,
      
      }
class Total(db.Document):

   ids = db.StringField()
   daily = db.IntField()
   total = db.IntField()
 

   def to_json(self):

      return {
         "ids":self.ids,
         "daily": self.daily,
         "total": self.total,
        
      }

#######AUTHENTICATION########
def token_required(f):
   @wraps(f)
   def decorated(*args, **kwargs):
      token = request.headers['API_TOKEN']

      if not token:
         return jsonify({'message':'Token is missing!'}), 403
      try:
         data = jwt.decode(token, app.config['SECRET_KEY'],algorithms='HS256')
      except jwt.ExpiredSignatureError:
         return jsonify({'message' : 'Token is expired!'}),403
      except:
         return jsonify({'message':'Token is invalid!'}), 403
      
      return f(*args, **kwargs)

   return decorated
#######AUTHENTICATION########

##### Basic Routing ######
@app.route('/',methods=['GET'])
def hello():
   return "Hello, THIS IS YOLO-server V1.1 "
@app.route('/api/test/unprotected')
def unprotected():
   return jsonify({'message':'Anyone can view this!'})
@app.route('/api/test/protected')
@token_required
def protected():
   return jsonify({'message':'This is only available for people with valid tokens.'})
##### Basic Routing ######

###### Register & Login ################
@app.route('/api/register', methods=['POST','GET'])
def api_register():

   data = request.get_json()
   #auth_token = user.encode_auth_token(user.id)
   if str(data['aType']) == 'iot':
      new_id = str(int(client.get_database('API-Detection').get_collection('device').count())+1)
      hashed = generate_password_hash(data['password'], method='sha256')
      uniqueName = str(data['factory']+"_"+data['aType']+"_"+new_id)

      newDevice = Device(ids=new_id,username=data['username'],aType=data['aType'],factory=data['factory'],password=hashed,uniqueName=uniqueName)
      newDevice.save()

      return "Successfully appied! [ioT]\n"
     

   elif str(data['aType']) == 'mobile' :

      newDevice = Device(ids=data['ids'],username="",aType=data['aType'],factory="",password="",uniqueName="")
      newDevice.save()
      
      return "Successfully appied! [mobile]"
   
   else :
      return "Invalid data"
@app.route('/api/login', methods=['GET', 'POST'])
def login():

   auth = request.authorization

   if not auth or not auth.username or not auth.password:  
      return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

   user = Device.objects.get(username=auth.username)
    
   if check_password_hash(user.password, auth.password):  

      token = jwt.encode({'uniqueName': user.uniqueName, 'exp' : datetime.utcnow() + timedelta(days=1)}, app.config['SECRET_KEY'])  
      return jsonify({'token' : token}) 

   return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

   if auth and auth.password == 'password':
      token = jwt.encode({'user':auth.username,'ext':datetime.datetime.utcnow() + timedelta(days=1)}, app.config['SECRET_KEY'])
      return jsonify({'token': token})

   return make_response('Could not verify',401,{'API-Authentication':'Basic realm="Login Required"'})
###### Register & Login ################

###### Unknown Detection ###############
@app.route('/api/detect', methods=['POST'])
@token_required
def api_upload_unknown():

   if request.files:

      save_path = os.getcwd()+'/api_unknown/'
      num = len(os.listdir(save_path+'new/'))+1
      file = request.files["image"] 
      filename = "new_unknown_"+str(num)
      file.save(save_path+"new/"+filename+".jpg")
      print(file)
      
      t0 = time.time()
      prepareYolo(SINGLE_MODEL_TEST,True,save_path+"new/"+filename+".jpg")
      _,res = runYolo(0)
      image = cv2.cvtColor(res,cv2.COLOR_BGR2RGB)
      image2 = Image.fromarray(image).resize((480,360))
      print(image2)
      image2.save(save_path+"res/"+filename+".jpg")
      timestamp = int(datetime.timestamp(datetime.now()))
      buff = BytesIO()
      image2.save(buff, format="JPEG")
      unknown1 = Unknown(ids=num,filename=filename,times=timestamp,file=buff)
      unknown1.save()

      img_str = base64.b64encode(buff.getvalue()).decode('utf-8')
      
      return jsonify(
         result="Found Object",
         image=img_str
      )
###### Unknown Detection ###############

#### Upload Label ###############
@app.route('/api/working/label', methods=['POST','GET'])
#@token_required
def api_upload_label():

   if request.files:

      identify = request.form["identify"]
      labeledby = request.form["labeledby"]
      file = request.files["image"] 
      text = request.files["text"] 
      image_path = os.getcwd()+"/assets/labels/"
      label_path = os.getcwd()+"/assets/texts/"
      num = len(os.listdir(image_path))+1
         
      filename = "labeled_"+str(num)
      file.save(image_path+filename+".jpg")
      text.save(image_path+filename+".txt")
     
      ids = str(num)
      label1 = Labeled(ids=ids,filename=filename,imgfile=file,labelfile=text,identify=identify,labeledby=labeledby)
      label1.save()

      return "Label image have been saved!"
     
   else :
      return "please put a request file."
#### Upload Label ###############

### Re-train ####################
@app.route('/api/working/retrain', methods=['get'])
#@token_required
def retrain():
   pass
   # count = len(Labeled.identify(
   #    {"identify" : "bottle"}
   # ))
  
   #return count

   # for obj in Labeled:
   #    count = len(obj['bottle'])

   #return "retrain sessions"
### Re-train ####################
"""
@app.route('/api/labeled', methods=['GET','POST'])
def api_lebeled():
   pass
@app.route('/api/labeled/<ids>', methods=['POST'])
def api_each_labeled():
   pass


@app.route('/api/total', methods=['GET'])
def totallyDevices():
   pass;
@app.route('/api/info/getClient/<uniqueName>', methods=['GET'])
@token_required
def getClient(uniqueName):
   client = Device.objects.get(uniqueName=uniqueName)
   return jsonify({'result':client})
   # return Labeled.query.filter_by(uniqueName=data['uniqueName']).first()
@app.route('/api/info/addModel', methods=['POST'])
@token_required
def addModel():
   data = request.get_json()

   newModel = Model(name=data['name'],pathfile=data['pathfile'])
   newModel.save()

   return "Successfully model added!"
@app.route('/api/info/getAllModel', methods=['GET'])
@token_required
def getAllModel():
   output = []
   for model in Model.objects[:]:
      output.append(model)
   return jsonify({'result':output})
@app.route('/api/info/getOneModel/<name>', methods=['GET'])
@token_required
def getOneModel(name):
   model = Model.objects.get(name=name)
   return jsonify({'result':model})
@app.route('/api/info/addTotal', methods=['POST'])
@token_required
def addTotal():
   data = request.get_json()
   newTotal = Total(ids=data['ids'],daily=data['daily'],total=data['total'])
   newTotal.save()

   return "Successfully model added!"
@app.route('/api/info/total', methods=['GET'])
@token_required
def getTotal():
   output = []
   for total in Total.objects[:]:
      output.append(total)
   return jsonify({'result':output})
"""

"""
if __name__ == '__main__':

   subprocess.call("cls",shell=True)
   if os.path.exists('./api_unknown/new') :
      shutil.rmtree('./api_unknown/new') 
   os.makedirs('./api_unknown/new') 
   if os.path.exists('./api_unknown/res') :
      shutil.rmtree('./api_unknown/res') 
   os.makedirs('./api_unknown/res') 

   app.run(debug=True,host='0.0.0.0',port=80)
"""

