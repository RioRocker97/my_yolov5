###############################################
#                                             #
# Only work on Linux . i didn't do flexibility coding yet. #
#                                             #
############################################### 
import subprocess
import shutil
import os
from raw_server import app

if __name__ == '__main__':

   subprocess.call("clear",shell=True)
   if os.path.exists('./api_unknown/new') :
      shutil.rmtree('./api_unknown/new') 
   os.makedirs('./api_unknown/new') 
   if os.path.exists('./api_unknown/res') :
      shutil.rmtree('./api_unknown/res') 
   os.makedirs('./api_unknown/res') 
   
   app.run(debug=True,host='0.0.0.0',port=80)
