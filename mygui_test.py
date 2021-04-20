###############################################
#                                             #
# Test any library if i have doubt            #
#                                             #
############################################### 
from datetime import datetime
import os
if __name__ == '__main__':
    now = datetime.now()

    timestamp = datetime.timestamp(now)
    print("timestamp =", int(timestamp))
    print(os.getcwd())
