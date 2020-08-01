---
layout: default
title: Scientific Overview
nav_order: 3
---
# What are camera calibration and image rectification? #
The use of images to study real-world phenomena requires transformation of the images to real-world coordinates. This allows us to quantify things in an image
(e.g. shoreline position or the length of a tree) in real-world space (e.g. meters). Photogrammetric principals show that this transformation can be completed through the
collinearity equations, which require knowledge of nine camera parameters: camera location (x and y, e.g. longitude and latitude), elevation, three
camera view angles (e.g. azimuth, tilt, and swing/roll), camera focal length, and the coordinates (x and y) of the principal point. Observations of 
points co-located in the image and the real-world, known as ground control points (GCPs), can be used to perform a least-squares optimization of these nine parameters, provided
initial approximations for each are given, to minimize transformation error. This process is known as **camera calibration** (or space resection, in
classical photogrammetry).For more details the user is referred to the references given below.

The optimized parameters can then be inserted into the collinearity conditions to transform any real-world coordinate (location and elevation) to a
corresponding point in the image, or vice-versa. In this way, an image can be transformed into a map in real-world coordinates; this process is 
known as **image rectification**.


# Overview of SurfRCaT processes/assumptions #
SurfRCaT completes the calibration and rectification processes in 5 stages. An overview of each stage, along with important assumptions made at each, 
are presented below:

1. Imagery acquisition and user inputs

   Here the user is asked to supply a video from the camera to be calibrated. SurfRCat extracts frames from the user-input video at a user-specified rate, 
   and allows the user to choose a frame to use in the remote-GCP extraction (step 3). SurfRCaT assumes that the user has obtained video(s)
   before using the tool. This typically requires permission from the camera owners/operators to download web-streaming video, as many
   surfcams are privately owned. Once permission is obtained, web-based video streams can be saved locally using a programming language or 
   open-source web extensions/tools.  

   The user is also asked at this stage to provide initial estimates for four of the nine camera parameters: camera location (lat/lon), elevation,
   and azimuth viewing angle. In the absence of a site visit, we recommend using Google Earth to obtain these estimates ([Tutorial 1](https://conlin-matt.github.io/SurfRCaT/tutorials.html)
   provides an example). SurfRCaT assumes initial approximations for the other five camera parameters as follows:

   + SurfRCaT assumes the tilt of the camera to be 80 degrees
   + SurfRCaT assumes the roll of the camera to be negligable.   
   + SurfRCaT assumes camera focal length by assuming a 60 degree camera horizontal field of view
   + SurfRCaT assumes the principal point coodinates to be the center of the image.
   + SurfRCaT also assumes lens distorion to be 0, i.e. does not account for it. 

   > **Note**
   >
   > If your camera deviates largely from any of these assumptions (e.g. fisheye lens, small tilt), SurfRCaT may
   > not work well out of the box. Camera parameter assumptions are easy to change if you download the source code,
   > however the lens distortion assumption is not.


2. Lidar acquisition

   SurfRCaT searches FTP repositories of the National Oceanic and Atmospheric Administration (NOAA) to find archived airborne lidar datasets that
   cover the user-input camera location. These repositories contain thousands of datasets. The user is able to choose a dataset and SurfRCaT 
   automatically downloads a portion of that dataset proximal to the camera.

3. Remote-GCP extraction

   SurfRCaT facilitates the remote extraction of GCPs by prompting the user to identify (by clicking) corresponding
   points in the lidar data and camera image.
   
   > **Note**
   >
   > In general, calibration accuracy is known to increase with increasing number of GCPs and increasing GCP distribution accross the image format. In other words, generally speaking, the more GCPs you identify and the more widely distributed they are, the better. Many other factors can confound this relationship, however, such as site orientation and GCP identification accuracy. There is no one-size-fits-all solution for this; site-specific testing may be beneficial. 

4. Calibration
	
   SurfRCaT uses the camera parameter inputs/assumptions (step 1) and the remote-GCPs (step 3) to complete the calibration (see above). The calibration 
   is completed following the iterative methods presented in [1], however we augment those equations in [1] with the three instrinsic camera parameters that 
   are included in SurfRCaT (focal length and principal point coordinates). 

   The accuracy of the calibration is assesed by comparing the reprojected positions of the GCPs in the image with the positions identified by the user. 

5. Rectification

   The adjusted camera parameters are then used to rectify images from the camera to real-world coordinates. This occurs by finding the location in
   the image of every point within a user-specified real-world grid, and then inverse mapping the color of the image at those points to their real-world 
   locations. The grid is assumed to be input in a coordinate system relative to the user-input camera location, with the y-axis (x-axis) in meters
   north (east) of this location.

   The rectification is also completed planimetrically at a user-input elevation. Technically speaking, then, the rectified product will be most
   accurate only for real-world points at this elevation. For the purposes of analyzing coastal geophysical processes, images are typically
   rectified to the observed tidal elevation, as we are typically most interested in features at or near the water line. An example and further
   guidance on this is given in both [Tutorials](https://conlin-matt.github.io/SurfRCaT/tutorials.html).

### References ###

[1] Wolf, P. R., Dewitt, B., & Wilkinson, B. (2014). Elements of Photogrammetry with Applications in GIS. McGraw and Hill education.

[2] Holland, K. T., Holman, R. A., Lippmann, T. C., Stanley, J., & Plant, N. (1997). 
Practical use of video imagery in nearshore oceanographic field studies. IEEE Journal of oceanic engineering, 22(1), 81-92.







