---
layout: default
title: Extensions
nav_order: 6
---
# Re-calibration #

Perhaps you have completed a calibration for a camera, but you are unhappy with it. SurfRCaT facilitates re-calibrations by allowing you to load products
from when you previously calibrated the camera. If you want to begin the re-calibration with the same video as when you initially calibrated the camera, make
sure you set your working directory as the directory in which the subdirectory *caibration_<video_name>* lives. Enter all the user inputs as you
did during the initial calibration. When you click "Continue" in the Inputs and Imagery window, SurfRCaT will recognize that a calibration has been completed
previously using this video, and will give you the options to use the same calibration image and/or lidar point cloud as the initial calibration.

Alternatively, you may have videos from many different times for a single camera, and wish to calibrate the camera for each video time. TUTORIAL 2
provides an example of this situation. In this case, you can load the lidar point cloud that was downloaded for the first camera calibration by 
checking Yes in the "Used saved lidar point cloud?" field in the Imagery and Inputs window. This way, you only need to take the time to download
a lidar point cloud once. 
 

# Exporting products to Python/Matlab #

For the purposes of precise analyses (e.g. automatic shoreline extraction), SurfRCaT saves rectified images as .mat (Matlab) and .pkl (Python) files. These
can be imported into your preferred programming language for analysis. 

The .mat file is intended to be structured the same way as rectified products from the [Coastal Imaging Research Network (CIRN) routines](link). To import 
the .mat file into Matlab:

'''matlab
load('<path_to_image>/<im>_rectif.mat');
frameRect.x = x; frameRect.y = y; frameRect.I = I;
'''
This will produce a frameRect struct that is similar in structure to those returned and read by the CIRN codes.
___

The Python .pkl file is a compressed binary verison of a Python dict that contains the rectified product. The dict is structured similarly to the Matlab 
struct produced by the above code. To import the .pkl file in Python:

'''python
import pickle

f = open('<path_to_image>/<im>_rectif.pkl','rb')
frameRect = pickle.load(f)
'''


# Other potential applications #
The facilities within SurfRCaT may be useful for applications that it was not specifically designed for. These could include:
### Extraction of frames from any video at a user specified rate ###

To do this for any video, simply invoke the tool, choose the 'Rectify images' option in the first window and input the video file
and save directory in the Step 1 box. This will open the video decimator window where you can specify the decimation rate. You can
repeat this process for as many video as you want.

Alternatively, to do this programmatically in Python for 2 frames/second you can run:

```python
import SurfRCaT
import cv2
	
vid = 'C:/path/to/video.mp4'
saveDir = 'C:/directory/to/save/frames/to'

cap = cv2.VideoCapture(vid)
numFrames = int(cap.get(7))
fps = cap.get(5)
vidLen = int(numFrames/fps)

secondsPerFrame = 1 # Leave as 1 to ignore this parameter #
rate = 2 # 2 frames/second #

SurfRCaT.getImagery_GetStills(vid,secondsPerFrame,rate,vidLen,saveDir)
```


### Automatic assesment of airborne lidar datasets for a location ###

SurfRCaT could be used to determine available/download airborne lidar datasets for a given coastal location. The graphical
user interface was not designed for this directly, however it is possible. You'll have to provide a video and extract a frame 
from it, however you won't actually care about these in this case.

This could also be done programmatically using the following code:

```python  
import SurfRCaT
import ftplib
import numpy as np

camera_latitude = <input latitude (WGS84) here>
camera_longitude = <input longitude (WGS84) here>

# Get the IDs of datasets that are near this location (same state and/or coast) #
closeIDs = SurfRCaT.getLidar_FindPossibleIDs(camera_latitude,camera_longitude)

# Search these close datasets to find those that cover this location #
ftp = ftplib.FTP('ftp.coast.noaa.gov',timeout=1000000)
ftp.login('anonymous','anonymous')
ftp.cwd('/pub/DigitalCoast')
dirs = [i for i in ftp.nlst() if 'lidar' in i]
alldirs = []
for ii in dirs:
    ftp.cwd(ii)
    alldirs.append([ii+'/'+i for i in ftp.nlst() if 'geoid' in i])
    ftp.cwd('../')  

appropID = list() # Initiate list of IDs that contain the camera location #
i = 0
for ID in IDs:  
i = i+=1
    check = SurfRCaT.getLidar_TryID(ftp,alldirs,ID,camera_latitude,camera_longitude)
    ftp.cwd('../../../../')

    if check:
        if len(check)>0:       
            appropID.append(ID)

# Choose a dataset #
IDToDownload = appropID[<Choose which dataset you want>]

# Determine the tiles that are close enough to the camera to download #
sf = SurfRCaT.getLidar_GetShapefile(IDToDownload)
poly = SurfRCaT.getLidar_CalcViewArea(30,20,1000,camera_latitude,camera_longitude)
        
tilesKeep = list()
for shapeNum in range(0,len(sf)):
    out = SurfRCaT.getLidar_SearchTiles(sf,poly,shapeNum,camera_latitude,camera_longitude)
    if out:
        tilesKeep.append(out)

# Download the portion of the dataset close to the camera #
lidarDat = np.empty([0,3])
for thisFile in tilesKeep:
    lidarXYZsmall = SurfRCaT.getLidar_Download(thisFile,IDToDownload,camera_latitude,camera_longitude)
    lidarDat = np.append(lidarDat,lidarXYZsmall,axis=0)

# Format the point cloud as a Pandas DataFrame (coordinates relative to input location) #
pc = SurfRCaT.getLidar_CreatePC(lidarDat,camera_latitude,camera_longitude)
```

### Others? Let us know if you have ideas! ###





