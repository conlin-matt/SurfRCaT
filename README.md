# SurfRCaT

## What is it?

The surf-camera remote calibration tool (SurfRCaT) allows for the calibration of any U.S. coastal camera that views structures identifiable in lidar data.

## How do I use it?

SurfRCaT can be obtained and used in one of two ways: via the pre-compiled application or by building it from the source code. Either way, you must first have images from your camera to feed to the program. This is with the exception of the WebCAT surfcam array deployed by the Southeastern Coastal Ocean Observing Regional Association ([see here](https://secoora.org/webcat/)). If you want to use one of these cameras, SurfRCaT will get the imagery for you. 

#### 1. SurfRCaT via precompiled app

SurfRCaT has been bundled into a (mostly) standalone application. You won't need to do any coding to use it. However, the application is quite bulky and can take some time to download and install. DISCLAIMER: The app can only be run on computers running Windows. Additionally, while the app has been tested to run well on a number of different machines, I cannot guarentee that it will run without error on all Windows machines. Any issues should be reported to the Issues page, and I will do my best to ammend them.

Steps for obtaining the SurfRCaT app:
1) Go to [this](https://drive.google.com/open?id=1os126s7bYrGzTo3P4jyUQcrrfWirl70l) link and click on the 'Download' button in the top right corner of the screen. 
2) If using Microsoft Edge/Internet Explorer, select 'Open' on the bottom of the screen to open the application folder after it downloads. If using Chrome, click on the folder in the lower-left corner of the screen when it finishes downloading.
3) In the Explorer window that opens, select 'Extract all', and choose a location to extract the folder too. The location must already exist. Click 'Extract'.
4) Go to the extracted SurfRCaT folder, and double click to see its contents.
5) Scroll down until you find the file called SurfRCaT or SurfRCaT.exe (it is of type "application").
6) Double click on this file to launch SurfRCaT. Follow the onscreen instructions. 

Note: In some cases, the program can encounter an issue after the GCPs are identified in the lidar data. In this case, please download [this]() folder, extract it, and copy it into the "LaunchPPTKwin" folder within the SurfRCaT folder.

#### 2. SurfRCaT from source


## FAQ
1) How do I use the lidar point cloud viewer window to identify points?    
Answer: The point cloud viewer window is a functionality of the Point Processing Toolkit (pptk), an open-source python package. See the pptk documentation [here](https://heremaps.github.io/pptk/viewer.html) for instructions. We recommend rotating/translating/zooming your view until the point cloud looks similar to the image to help you identify corresponding features. **Important note: You must zoom the view in/out before translating/rotating it to maintain your view position.**
2) SurfRCaT seems like it froze. What do I do?  
Answer: SurfRCaT launches and runs some processes without any visual signature of doing so, making it look like the app has frozen when it really hasn't. So, give it a few minutes. If it still seems frozen, just close and re-launch. Note: The incorporation of a spinning wheel (or similar) while background processes run would be a welcome pull request!

