**DISCLAIMER:This repository is based on [Ultralytics/Yolov5](https://github.com/ultralytics/yolov5) . I do not own or claim to be the creator of their implemented YOLO object detection technology.**

# IOT-project for counting product
This project's goal is to integrated YOLO object detection into my basic GUI python-based program for counting product . 

## About me

<img src="https://i.imgur.com/zqvv7ke.jpg" width="25%">

Kasin Yamsri 
Student NO.6010613518

This is part of the final project of computer engineering at Thammsart University.

## Result
| old UI (pre v1.7) | new UI (v1.7+)
| - | - |
| <img src="https://i.imgur.com/NRknPKA.jpg" width="100%"> | <img src="https://i.imgur.com/8KFlaUQ.jpg" width="100%"> |

## Progression Note
- 22/11/2020
    - already train solid model for specific task(3 cap type + 1 unknows)
    - Try to modify detect.py in order to work with mygui.py (kinda hard)
    - very lazy implementation (do what minimum)
- 26/11/2020
    - understanding Threading in YOLOv5
    - try to use threading in order to save detected image to some specific location
    - lazy implementation (do what it should)
- 27/12/2020
    - look into detect.py again so i would modify it to be used with mygui.py
    - new feature proposal (count,live video feed in 1 Giant GUI)
    - exploring Machine learning and essentail library to complete this project
    - i have no idea how to do next step 
- 25/1/2021
    - disable saving image after finding 'unknown' object (for performance later // will fix later)
    - can count now (lazy implmentation)
    - will try to squeeze all feature in GUI (still don't know what to do )    
- 14/3/2021
    - i filped it all !!!!! reconstuction all my work into 3 seperate unit
    - my part is only handling client side so..... no more re-train yea !
- 16/3/2021
    - finished reconstucting GUI .now seperating into 2 tab .
    - awaiting API endpoint from server side
    - still can't integrate CV2 live video output into myGUI
    - try using API with my own server (can send/get result of unknown image)
- 20/3/2021
    - VDO streaming within window application is available !!!
    - try to manipulate detect.py to be used inside mygui.py as a function
- 21/3/2021 
    - success ! now using mygui_detect.py for directly using YOLOv5 for this project
    - successfully seperate preparation code and detection code so i could work around with loading time
    - using thread for sure !
    - YOLOv5 implementation is almost completed. 
- 22/3/2021
    - MyGUI.py is good to go ! . no more using subprocess to call Yolov5
    - Server YOLOv5 is up and running !
- 31/3/2021
    - Cleaning Repo from clean_work branch 
    - try to delete non-essential file out of this project coz' it too messy!
- 3/4/2021
    - Cleaning completed !
    - now client+server code can work together in single Repo
- 6/4/2021
    - can send image to detect at yolo-server 
    - time to process result is pretty good (0.2 sec)
- 19/4/2021
    - fix server file because why not ? it a part of my job
    - using token is available now
    - need to integrate registration and login into myGUI

    - first implement GUI for login and register . Quick and simple
    - put black box behind count indicator
- 20/4/2021
    - new UI
    - new function (yet to implement)
- 21/4/2021
    - registration ok
    - constant unknown data to be sent to YOLO-server ok (poor performance)
    - will do image "swiping" later
- 24/4/2021
    - can swap model now
    - waiting for model downloading from YOLO-server when it finished
    - daily count is possible 
    - not sure how to collect new image to be re-train tho..

    - prototyping "collect new image" feature . not sure if it working correctly...
    - new folder path defined again.
- 26/4/2021
    - can swap model (from server) now
    - can send 50 image for re-training
    - what do now ?
- 29/4/2021
    - overhaul UI (so customer could use my program easily)
- 1/5/2021
    - detection is possible
    - applicaiton structure feel like it too complexed.... but it work fine
- 2/5/2021
    - from now on , update will be appear down below
## New File Location

- BASE_DIR\unknown : for saving unknown image to be sent to server
- BASE_DIR\unknown\raw : for saving raw image to be sent to server
- BASE_DIR\gui_data : for saving file to be used in building GUI
- BASE_DIR\mine : for saving local model file

## OVERHAUL UI Progression (v1.7+)

| Status | Feature | Status | Feature | 
| :-: | :-: | :-: | :-: | 
| :white_check_mark: | preload YOLO model | :white_check_mark: | detect and stop |
| :white_check_mark: | login to YOLO-server | :white_check_mark: | folder & file for GUI |
| :white_check_mark: | list all Model (Local&Sever) | :white_check_mark: | download server model |
| :white_check_mark: | Swap a new model | :white_check_mark: | register to YOLO-server |
| :white_check_mark: | send unknown | :white_check_mark: | swiping in view mode |
| :white_check_mark: | one click capture | :white_check_mark: | send unknown |
| :white_check_mark: | file handling | :hourglass: | test connection |
| :hourglass: | get unknown result | :hourglass: | view mode |
| :hourglass: | capture mode | :x: | something else |

<img src="https://i.imgur.com/VkV3hD4.png" width="75%">
