# SurfRCaT Documentation

![alt text](https://github.com/conlin-matt/SurfRCaT/blob/master/SurfRCaT_PickGCPs.PNG)

## What is it?

The surf-camera remote calibration tool (SurfRCaT) allows for the calibration of any U.S. coastal camera that views structures identifiable in lidar data. It does this by facilitating the co-location of points in an image from the camera and co-spatial airborn lidar observations (see image above). A calibrated camera can be used to make image measurements in real-world coordinates. 

## How do I use it?

SurfRCaT can be obtained and used in one of two ways: via the pre-compiled application or by building it from the source code. If you want to calibrate a camera from the WebCAT surfcam array deployed by the Southeastern Coastal Ocean Observing Regional Association ([see here](https://secoora.org/webcat/)), SurfRCaT will automatically get all inputs. NOTE: As of now, SurfRCaT will only work on Windows machines.

#### 1. SurfRCaT via precompiled app

SurfRCaT has been bundled into a standalone application. You won't need to do any coding to use it.

Steps for obtaining the SurfRCaT app:
1) [Download](https://www.dropbox.com/s/5devy19ja28ipqs/SurfRCaT_V2_5.exe?dl=1) the tool.
2) When the tool has finished downloading, click on it (Chrome) or select Run (Edge) to launch the installer.
3) Follow the prompts to install SurfRCaT. Note- you should install the tool to an easy-to-find directory, because output files will be saved to the same location as the tool itself. 

#### 2. SurfRCaT from source

If you want a bit more control over the code, you can create SurfRCaT via the source code provided in this repo. 

Steps for building SurfRCaT from source:
1) Clone or download the SurfRCaT repository into a folder of your choosing.
2) If you don't already have it, download the appropriate Anaconda distribution for your machine from [here](https://www.anaconda.com/distribution/). Use the Python 3.7 64-bit version. Anaconda is an all-in-one package and environment manager, and makes downloading and dealing with Python packages relatively painless.
3) Open an Anaconda prompt by searching for 'Anaconda' in the Windows search bar and selecting the prompt.
4) Create a new environment called SurfRCaT_env containing Python 3.6 and most of the package dependencies by running the following two commands in the Anaconda prompt (with an 'Enter' press between the commands):
```bash
conda create -n SurfRCaT_env -c conda-forge python=3.6 python-pdal pyqt numpy pandas matplotlib opencv json requests pyshp utm lxml
conda activate SurfRCaT_env
```
6) Pip install fbs, the package for running the GUI, and pptk, the Point Processing Toolkit by executing:
```bash
pip install fbs pptk
```
8) cd to the directory containing the contents of this repository by executing:
```bash
cd <your directory>
```
9) Invoke the tool by running:
```bash
fbs run 
```

## Test Example ##
Below is a step-by-step example to get you more familiar with using SurfRCaT after it is installed. This also functions as a test to ensure SurfRCaT is working properly on your machine. You should be able to complete all steps and get results that are reasonably similar to those presented below:

1) Invoke the tool, either as the app or from source (see above).
2) Choose the "Select WebCAT camera from list" option.
3) Select the "Folly Beach Pier (south) camera and press "Continue". The video should download followed by the seperation of unique views.
4) A window showing images from this camera's two views should appear (see below). Select the view from the dropdown list corresponding to the image showing the pier: view one (left image) or view two (right image). 
5) A table showing lidar datasets that cover this area will appear. Click the box next to the first listed dataset (ID: 5184) and press "Continue." 3 processes should now occur in the following order: tile sorting, data downloading, and point cloud generation. These three processes will take some time (depending on machine) to complete. Progress bars should show the status of the first two (though not continuously for the second). Press "Continue" when the processes complete.
6) You have now entered the GCP-picking module, the heart of SurfRCaT. First, watch [this](https://www.dropbox.com/s/jiogwhe14z5g9i4/GCPPicking_Trim.mp4?dl=0) video showing how to identify GCPs.
7) Now, try it yourself. Press "Go" to begin remote-GCP extraction. When the lidar point cloud opens (it can take up to 2 minutes to do so), zoom out slightly with the mouse scroll wheel. Then, rotate the view counter-clockwise by clicking and holding and moving the mouse until you can see the pier. Select the four points on the pier (in this order) shown in the image below. To select a point: hold control, click on the point, release control, wait 2 seconds, and then right click anywhere in the viewer. When done, close the lidar viewer window by x-ing out of it. 
![alt text](https://github.com/conlin-matt/SurfRCaT/blob/master/Example_LidarGCPs.png)

8) The text above the image should now change from "The lidar point cloud is opening..." to "Real-world coordinates of points saved!". In the image, click on the same four points, in the same order, as shown in the image below.
![alt text](https://github.com/conlin-matt/SurfRCaT/blob/master/Example_ImageGCPs.png)

9) Press "Done" when done and "Continue" to move on (or retry if you aren't happy with your point selection).
10) The Calibration Module window will now appear. Press "CALIBRATE" to perform the calibration. You should get results resembling those shown below. Note the RMS of control point residuals: 2.1 pixels. 
![alt text](https://github.com/conlin-matt/SurfRCaT/blob/master/Example_Results.png)


## Issues ##
Please report all issues to the Issues page in this repo. 

## Contributing ##
Contributions are welcome! Please create a new branch for your change, push your changes to that branch, and submit a pull request to merge it with the main branch.
