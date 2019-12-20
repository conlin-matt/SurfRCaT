# SurfRCaT

## What is it?

The surf-camera remote calibration tool (SurfRCaT) allows for the calibration of any U.S. coastal camera that views structures identifiable in lidar data.

## How do I use it?

SurfRCaT can be obtained and used in one of two ways: via the pre-compiled application or by building it from the source code. Either way, you must first have images from your camera to feed to the program. This is with the exception of the WebCAT surfcam array deployed by the Southeastern Coastal Ocean Observing Regional Association ([see here](https://secoora.org/webcat/)). If you want to use one of these cameras, SurfRCaT will get the imagery for you. 

### 1. SurfRCaT via precompiled app

SurfRCaT has been bundled into a (mostly) standalone application. You won't need to do any coding to use it. However, the application is quite bulky and can take some time to download and install. DISCLAIMER: The app can only be run on computers running Windows. Additionally, while the app has been tested to run well on a number of different machines, I cannot guarentee that it will run without error on all Windows machines. Any issues should be reported to the Issues page, and I will do my best to ammend them.

Steps for obtaining the SurfRCaT app:
1) Go to [this](https://drive.google.com/open?id=1os126s7bYrGzTo3P4jyUQcrrfWirl70l) link and click on the 'Download' button in the top right corner of the screen. 
2) If using Microsoft Edge/Internet Explorer, select 'Open' on the bottom of the screen to open the application folder after it downloads. If using Chrome, click on the folder in the lower-left corner of the screen when it finishes downloading.
3) In the Explorer window that opens, select 'Extract all', and choose a location to extract the folder too. The location must already exist. Click 'Extract'.
4) Go to the extracted SurfRCaT folder, and double click to see its contents.
5) Scroll down until you find the file called SurfRCaT or SurfRCaT.exe (it is of type "application").
6) Double click on this file to launch SurfRCaT. Follow the onscreen instructions. 

Note: In some cases, the program can encounter an issue after the GCPs are identified in the lidar data. In this case, please download [this]() folder, extract it, and copy it into the "LaunchPPTKwin" folder within the SurfRCaT folder.

### 2. SurfRCaT from source

If you want a bit more control over the code, are not running Windows, or don't want to deal with a clunky executable, you can create SurfRCaT via the source code provided in this repo. While you will likely need to do some (pip) installations to make it work, the GUI tool will work the same as in the app once created. 

Steps for building SurfRCaT from source:
1) Clone or download the SurfRCaT repository into a folder of your choosing.
2) If you don'e already have it, download the appropriate Anaconda distribution for your machine from [here](https://www.anaconda.com/distribution/). Use the Python 3.7 64-bit version. Anaconda is an all-in-one package and environment manager, and makes downloading and dealing with Python packages relatively painless.
3) Open an Anconda prompt by searcing for 'Anaconda' in the Windows search bar and selecting the prompt. On a Mac, open a terminal window.
4) Create a new environment called SurfRCaT_env containing Python 3.6 and the pdal package by running the following two commands in the Anaconda prompt (with an 'Enter' press between the commands):
```bash
conda create -n SurfRCaT_env -c conda-forge python=3.6 python-pdal
conda activate SurfRCaT_env
```
6) Pip install PyQt5, the Python binding for the QT GUI package, as well as fbs, the package for running the GUI, by executing:
```bash
pip install fbs PyQt5==5.9.2
```
7) Pip install the following packages (in order): numpy, pandas, matplotlib, opencv, pickle, pptk, requests, ftplib, pyshp, utm, json. Each package can be pip installed by running the following command in the terminal window:
```bash
pip install <package>
```
e.g.
```bash
pip install numpy
```
8) Download [this](https://drive.google.com/open?id=1Pm4rXlXWJM-hBGHD12g2SBL67E5K2new) compressed folder, and copy the folder into the directory containing the contents of this repository.
9) cd to the directory containing the contents of this rpository by exeecuting:
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

