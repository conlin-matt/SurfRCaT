---
layout: default
title: Download
nav_order: 4
---

SurfRCaT can be obtained in one of two ways: by downloading a pre-compiled application or by building it from the source code. Below, 
instructions for downloading and using the tool in each of these ways are given. SurfRCaT only runs on Windows machines.

## SurfRCaT via precompiled app ##
You can download and use the precompiled SurfRCaT application following the steps below: 

1. [Download](https://www.dropbox.com/s/ppzkg3uyxy25zg7/SurfRCaT.exe?dl=1) the tool.

2. When the tool has finished downloading, click on it (Chrome) or select Run (Edge) to launch the installer.

3. Follow the prompts to install SurfRCaT. 

4. Launch SurfRCaT the same way you launch any other application. You'll have to run it as an administrator.


## SurfRCaT from source ##
If you want a bit more control over the code, you can create SurfRCaT via the source code provided in this repo. 

Steps for building SurfRCaT from source:

1. Clone or download the SurfRCaT repository (see link at top right) into a folder of your choosing.

2. If you don't already have it, download the appropriate Anaconda distribution for your machine from 
[here](https://www.anaconda.com/distribution/). Use the Python 3.7 64-bit version. Anaconda is an all-in-one package and environment manager, 
and makes downloading and dealing with Python packages relatively painless.

3. Open an Anaconda prompt by searching for 'Anaconda' in the Windows search bar and selecting the prompt.

4. Create a new environment called SurfRCaT_env containing Python 3.6 and most of the package dependencies by running the following two commands 
in the Anaconda prompt (with an 'Enter' press between the commands):

   ```bash
   conda config --set channel_priority strict
   conda create -n SurfRCaT_env -c conda-forge python=3.6 python-pdal pyqt numpy pandas matplotlib opencv requests pyshp utm lxml
   conda activate SurfRCaT_env
   ```

5. Pip install fbs, the package for running the GUI, pptk, the Point Processing Toolkit and reverse_geocoder, by executing:

   ```bash
   pip install fbs pptk reverse_geocoder
   ```

6. cd to the directory containing the contents of this repository by executing:

   ```bash
   cd <your directory>\SurfRCaT-master
   ```

7. Invoke the tool by running:

   ```bash
   fbs run 
   ```
