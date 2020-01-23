# SurfRCaT Documentation

![alt text](https://github.com/conlin-matt/SurfRCaT/blob/master/SurfRCaT_PickGCPs.PNG)

## What is it?

The surf-camera remote calibration tool (SurfRCaT) allows for the calibration of any U.S. coastal camera that views structures identifiable in lidar data. It does this by facilitating the co-location of points in an image from the camera and co-spatial airborn lidar observations (see image above).

## How do I use it?

SurfRCaT can be obtained and used in one of two ways: via the pre-compiled application or by building it from the source code. Either way, you must first have images from your camera to feed to the program. This is with the exception of the WebCAT surfcam array deployed by the Southeastern Coastal Ocean Observing Regional Association ([see here](https://secoora.org/webcat/)). If you want to use one of these cameras, SurfRCaT will get the imagery for you. 

### 1. SurfRCaT via precompiled app

SurfRCaT has been bundled into a (mostly) standalone application. You won't need to do any coding to use it. However, the application is quite bulky and can take some time to download and install. DISCLAIMER: The app can only be run on computers running Windows. Additionally, while the app has been tested to run well on a number of different machines, I cannot guarantee that it will run without error on all Windows machines. Any issues should be reported to the Issues page, and I will do my best to amend them.

Steps for obtaining the SurfRCaT app:
1) [Download](https://www.dropbox.com/s/kg7c3kzon0zl96p/SurfRCaT_V2_1.exe?dl=1) the tool.
2) When the tool has finished downloading, click on it (Chrome) or select Run (Edge) to launch the installer.
3) Follow the prompts to install SurfRCaT. Note- you should install the tool to an easy-to-find directory, because output files will be saved to the same location as the tool itself. 

### 2. SurfRCaT from source

If you want a bit more control over the code, are not running Windows, or don't want to deal with a clunky executable, you can create SurfRCaT via the source code provided in this repo. While you will likely need to do some (pip) installations to make it work, the GUI tool will work the same as in the app once created. 

Steps for building SurfRCaT from source:
1) Clone or download the SurfRCaT repository into a folder of your choosing.
2) If you don't already have it, download the appropriate Anaconda distribution for your machine from [here](https://www.anaconda.com/distribution/). Use the Python 3.7 64-bit version. Anaconda is an all-in-one package and environment manager, and makes downloading and dealing with Python packages relatively painless.
3) Open an Anaconda prompt by searching for 'Anaconda' in the Windows search bar and selecting the prompt. On a Mac, open a terminal window.
4) Create a new environment called SurfRCaT_env containing Python 3.6 and the pdal package by running the following two commands in the Anaconda prompt (with an 'Enter' press between the commands):
```bash
conda create -n SurfRCaT_env -c conda-forge python=3.6 python-pdal
conda activate SurfRCaT_env
```
6) Pip install PyQt5, the Python binding for the QT GUI package, as well as fbs, the package for running the GUI, by executing:
```bash
pip install fbs PyQt5==5.9.2
```
7) Conda install some necessary packages by executing:
```bash
conda install numpy pandas matplotlib opencv
```
8) Pip install the other necessary packages by executing:
```bash
pip install pptk pickle requests ftplib pyshp utm json
```
9) Download [this](https://drive.google.com/open?id=1Pm4rXlXWJM-hBGHD12g2SBL67E5K2new) compressed folder, and copy the folder into the directory containing the contents of this repository.
9) cd to the directory containing the contents of this repository by executing:
```bash
cd <your directory>
```
Create a new fbs project by executing the following (you can use defaults for all options):
```bash
fbs startproject 
```
10) Copy the main.py file, SurfRCaT.py file, and LaunchPPTKwin folder into the newly created src/main/python directory within the directory containing the contents of this repository. 
11) You're all set up to run the tool! Execute the following to run the tool:
```bash
fbs run 
```

## FAQ
1) How do I use the lidar point cloud viewer window to identify points?    
Answer: The point cloud viewer window is a functionality of the Point Processing Toolkit (pptk), an open-source python package. See the pptk documentation [here](https://heremaps.github.io/pptk/viewer.html) for instructions. We recommend rotating/translating/zooming your view until the point cloud looks similar to the image to help you identify corresponding features. **Important note: You must zoom the view in/out before translating/rotating it to maintain your view position.**
2) SurfRCaT seems like it froze. What do I do?  
Answer: SurfRCaT launches and runs some processes without any visual signature of doing so, making it look like the app has frozen when it really hasn't. So, give it a few minutes. If it still seems frozen, just close and re-launch. Note: The incorporation of a spinning wheel (or similar) while background processes run would be a welcome pull request!

