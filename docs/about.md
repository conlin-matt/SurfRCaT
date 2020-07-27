---
layout: default
title: About
nav_order: 2
---

# What is SurfRCaT? #
The Surf-camera Remote Calibration Tool (SurfRCaT) is a python-based, graphical user interface-driven tool that was designed 
to exploit imagery from an extensive network of recreational surfcams operating on the U.S. coastline for studies of coastal geophysical processes.
It does this by facilitating the calibration of, and rectification of images from, any video camera on the U.S. coastline the views structures 
identifiable in airborne lidar data.


# What can SurfRCaT do? #
 + SurfRCaT can help you remotely calibrate and rectify images from many pre-existing cameras on the U.S. coastline (see CONSIDERATIONS FOR USING SURFRCAT)

 + SurfRCaT can guide you through the calibration and rectification processes in a self-contained graphical user interface. It does this by facilitating the
co-location of points in an image from the camera and airborne lidar observations that it automatically obtains.

 + SurfRCaT can export rectified image products into Matlab and Python files for further analysis. (See the EXTENSIONS page).
 
 + SurfRCaT can interface with cameras from the [Webcamera Application Testbed](https://secoora.org/webcat/) to download historical imagery and perform acccurate calibrbations
and image rectifications for 4 of these cameras.

These processes also mean that:
  
 + SurfRCaT can automatically find airborne lidar datasets that cover a particular location and can download a dataset of the user's choosing. 

 + SurfRCaT can display and allow manipulation of multi-million point lidar point clouds by utlizing the point processing toolkit. 

 + SurfRCaT can extract frames from a user-input video at a user-specified rate.

 

# Considerations for using SurfRCaT #
1) SurfRCaT can only be applied to a camera if:
   + You have video(s) from the camera 
   + The camera views structures that can be identified in airborne lidar observations (e.g. piers, buildings, lifeguard towers)

2) SurfRCaT must be run on a Windows 10 machine.
3) SurfRCaT requires a reliable internet connection during runtime. 
4) Airborne lidar datasets can be extremely large. While SurfRCaT goes to great lengths to reduce the amount of lidar data that are
downloaded and saved locally, this process can still be slow. Speed depends greatly on the lidar dataset being downloaded, though this 
process could concievably take upwards of 30 minutes or more depending on the dataset and internet connection. 
5) Using images from surfcams to study the coast requires a number of specific considerations. The TUTORIALS illustrate these. 
6) SurfRCaT does not account/correct for lens distortion (see OVERVIEW OF PROCESSES AND ASSUMPTIONS). SurfRCaT may therefore not be applicable to 
surfcams with substantial lens distortion (e.g. fisheye lenses). 



## Integration with the WebCAT array ##
The [Webcamera Application Testbed](https://secoora.org/webcat/) is a network of 7 surfcams spanning the southeastern U.S. that have continuous video streams archived on servers made
available to the public. SurfRCaT contains built-in options to download historical imagery from, calibrate, and rectify imagery from the 4 WebCAT cameras 
that meet SurfRCaT's usage requirments (see item 1 in CONSIDERATIONS FOR USING SURFRCAT). TUTORIAL 2 focuses on using a WebCAT camera to observe shoreline 
change in South Carolina. 











