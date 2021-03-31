#!/usr/bin/env python3
from flask import Flask,make_response,request,jsonify
from flask_mongoengine import MongoEngine
import os
from IPython.display import Image
from PIL import Image
import io
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from functools import wraps
import datetime
#from api_constants import mongodb_password


app = Flask(__name__)


#database_name = "Images"
#database_name = "Clients"
database_name = "API-Detection"
mongodb_password = "Com75591;"

DB_URI = "mongodb+srv://ikanaporn:{}@cluster0.x8seg.mongodb.net/{}?retryWrites=true&w=majority".format(
    mongodb_password, database_name
)
FOLDER_IMAGE_UPLOADS = "/Users/mai/SeniorProject/flaskwebapi/env/assets/images"

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
      token = request.args.get('token') #http://127.0.0.1:5000/routes?token=akdjkjfjfdd

      if not token:
         return jsonify({'message':'Token is missing!'}), 403
      try:
         data = jwt.decode(token, app.config['SECRET_KEY'])
      except:
         return jsonify({'message':'Token is invalid!'}), 403
      
      return f(*args, **kwargs)

   return decorated

@app.route('/api/auth/unprotected')
def unprotected():
   return jsonify({'message':'Anyone can view this!'})

@app.route('/api/auth/protected')
@token_required
def protected():
   return jsonify({'message':'This is only available for people with valid tokens.'})

@app.route('/api/auth/login', methods=['GET', 'POST'])
def login():

   auth = request.authorization

   if not auth or not auth.username or not auth.password:  
      return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

   user = Device.objects.get(username=auth.username)
    
   if check_password_hash(user.password, auth.password):  

      token = jwt.encode({'uniqueName': user.uniqueName, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=120)}, app.config['SECRET_KEY'])  
      return jsonify({'token' : token.decode('utf-8')}) 

   return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

   if auth and auth.password == 'password':
      token = jwt.encode({'user':auth.username,'ext':datetime.datetime.utcnow() + datetime.timedalta(minutes=120)}, app.config['SECRET_KEY'])
   
      return jsonify({'token': token.decode('utf-8')})

   return make_response('Could not verify',401,{'API-Authentication':'Basic realm="Login Required"'})


# it's work -  
@app.route('/api/working/image-detect', methods=['POST'])
@token_required
def api_upload_unknown():

   if request.files:

      num = len(os.listdir("/Users/mai/SeniorProject/flaskwebapi/env/assets/images"))+1
      file = request.files["image"] 
      filename = "new_unknown_"+str(num)
      time = 0

      file.save(os.path.join(app.config["IMAGE_UPLOADS"], "/Users/mai/SeniorProject/flaskwebapi/env/assets/images/new_unknown_"+str(num)+".jpg"))
      
      unknown1 = Unknown(ids=num,filename=filename,times=time,file=file)
      
      unknown1.save()

      return "UnknownImage have been Saved!"


# @app.route('/api/dbImages', methods=['POST'])
# def db_images():
#    lebeled1 = Labeled(ids="0001",filename="mitpol0.png",identify="bottle",lebeledBy="admin1")
#    lebeled2 = Labeled(ids="0002",filename="mitpol1.png",identify="bottle",lebeledBy="admin2")
   
#    lebeled1.save()
#    lebeled2.save()
#    return "Created"

@app.route('/api/labeled', methods=['GET','POST'])
def api_lebeled():
   pass

@app.route('/api/labeled/<ids>', methods=['POST'])
def api_each_labeled():
   pass

@app.route('/',methods=['GET'])
def hello():
   unknown = Unknown.objects(ids=8)
   return 
   #return "Hello"

@app.route('/api/initiate/register', methods=['POST','GET'])
def api_register():

   data = request.get_json()
   #auth_token = user.encode_auth_token(user.id)
   if data['aType'] == 'iot':
      hashed = generate_password_hash(data['password'], method='sha256')
      uniqueName = str(data['factory']+"_"+data['aType']+"_"+data['ids']+"_")

      newDevice = Device(ids=data['ids'],username=data['username'],aType=data['aType'],factory=data['factory'],password=hashed,uniqueName=uniqueName)
      newDevice.save()

      return "Successfully appied! [ioT]"
     

   elif data['aType'] == 'mobile' :

      newDevice = Device(ids=data['ids'],username="",aType=data['aType'],factory="",password="",uniqueName="")
      newDevice.save()
      
      return "Successfully appied! [mobile]"
   
   else :
      return "Invalid data"
 
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



   


# @app.route('/api/info/getClient/', methods=['GET'])
# def getAllClient(uniqueName):
#   # client = Device.objects(uniqueName=)
#     output = []
#    for client in Device.objects[:]:
#       output.append(client)
#    return jsonify({'result':output})




#JWT AUTH

#MODEL



if __name__ == '__main__':
    app.run(debug=True)


