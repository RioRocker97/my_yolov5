###############################################
#                                             #
# Only work on Linux . i didn't do flexibility coding yet. #
#                                             #
############################################### 
import subprocess
import shutil
import os
from raw_server import app
from platform import system
if __name__ == '__main__':

   if system() == 'Windows':
      arg = "cls"
   else:
      arg = "clear"
   subprocess.run([arg],shell=True)
   if os.path.exists('./api_unknown/new') :
      shutil.rmtree('./api_unknown/new') 
   os.makedirs('./api_unknown/new') 
   if os.path.exists('./api_unknown/res') :
      shutil.rmtree('./api_unknown/res') 
   os.makedirs('./api_unknown/res')

   if not os.path.exists('./assets/labels'): 
      os.makedirs('./assets/labels')
   if not os.path.exists('./assets/texts'): 
      os.makedirs('./assets/texts')
   if not os.path.exists('./api_unknown/model'): 
      os.makedirs('./api_unknown/model')
   if not os.path.exists('./train/images'): 
      os.makedirs('./train/images')
   if not os.path.exists('./train/labels'):
      os.makedirs('./train/labels')
   if not os.path.exists('./test/images'):
      os.makedirs('./test/images')
   if not os.path.exists('./test/labels'): 
      os.makedirs('./test/labels')

   
   app.run(debug=True,host='0.0.0.0',port=80)
