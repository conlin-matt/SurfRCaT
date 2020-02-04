# SurfRCaT Documentation

![alt text](https://github.com/conlin-matt/SurfRCaT/blob/master/SurfRCaT_PickGCPs.PNG)

## What is it?

The surf-camera remote calibration tool (SurfRCaT) allows for the calibration of any U.S. coastal camera that views structures identifiable in lidar data. It does this by facilitating the co-location of points in an image from the camera and co-spatial airborn lidar observations (see image above).

## How do I use it?

SurfRCaT can be obtained and used in one of two ways: via the pre-compiled application or by building it from the source code. If you want to calibrate a camera from the WebCAT surfcam array deployed by the Southeastern Coastal Ocean Observing Regional Association ([see here](https://secoora.org/webcat/)), SurfRCaT will automatically get all inputs.

### 1. SurfRCaT via precompiled app

SurfRCaT has been bundled into a standalone application. You won't need to do any coding to use it. NOTE: The app can only be run on Windows machines.

Steps for obtaining the SurfRCaT app:
1) [Download](https://www.dropbox.com/s/xhh5aji6kcg705v/SurfRCaT_V2_2.exe?dl=1) the tool.
2) When the tool has finished downloading, click on it (Chrome) or select Run (Edge) to launch the installer.
3) Follow the prompts to install SurfRCaT. Note- you should install the tool to an easy-to-find directory, because output files will be saved to the same location as the tool itself. 

### 2. SurfRCaT from source

If you want a bit more control over the code, you can create SurfRCaT via the source code provided in this repo. 

Steps for building SurfRCaT from source:
1) Clone or download the SurfRCaT repository into a folder of your choosing.
2) If you don't already have it, download the appropriate Anaconda distribution for your machine from [here](https://www.anaconda.com/distribution/). Use the Python 3.7 64-bit version. Anaconda is an all-in-one package and environment manager, and makes downloading and dealing with Python packages relatively painless.
3) Open an Anaconda prompt by searching for 'Anaconda' in the Windows search bar and selecting the prompt.
4) Create a new environment called SurfRCaT_env containing Python 3.6 and most of the package dependencies by running the following two commands in the Anaconda prompt (with an 'Enter' press between the commands):
```bash
conda create -n SurfRCaT_env -c conda-forge python=3.6 python-pdal pyqt numpy pandas matplotlib opencv requests pyshp utm lxml
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

## What if I have an issue? ##
Please report all issues to the Issues page in this repo. 

## Contributing ##
Contributions are welcome! Please create a new branch for your change, push your changes to that branch, and submit a pull request to merge it with the main branch.

## FAQ
1) How do I use the lidar point cloud viewer window to identify points?    
Answer: The point cloud viewer window is a functionality of the Point Processing Toolkit (pptk), an open-source python package. See the pptk documentation [here](https://heremaps.github.io/pptk/viewer.html) for instructions. We recommend rotating/translating/zooming your view until the point cloud looks similar to the image to help you identify corresponding features. **Important note: You must zoom the view in/out before translating/rotating it to maintain your view position.**

