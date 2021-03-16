**DISCLAIMER:This repository is based to [Ultralytics/Yolov5](https://github.com/ultralytics/yolov5) . I do not own or claim to be the creator of their implemented YOLO object detection technology.**

# IOT-project for counting product
This project's goal is to integrated YOLO object detection into my basic GUI python-based program for counting product . 

## About me

<img src="https://i.imgur.com/zqvv7ke.jpg" width="25%">

Kasin Yamsri 
Student NO.6010613518

This is part of the final project of computer engineering at Thammsart University.

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
## New File Location

- Base_DIR\retrain : for saving images and labels for detected image 



<img src="https://i.imgur.com/VkV3hD4.png" width="75%">
