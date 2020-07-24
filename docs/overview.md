---
layout: page
title: Scientific Overview
---

## Overview of processes and assumptions ##
The study of geophysical processes from images requires transformation of image information into real-world space. This transformation, known
as **rectification**, requires knowledge of a number of camera parameters such as camera location and view angles, camera focal length, and lens 
distortion characteristics, as well as the co-location of ground control points (GCPs) in the image and real-world coordinates.
Estimation of camera parameters from observations of GCPs is known as **camera calibration** (or space resection, in classical photogrammetry),
and is completed through a non-linear least squares adjustment of initial approximations to minimize transformation error. For more details the user 
is referred to the references given below.

SurfRCaT completes the calibration and rectification processes in 5 stages. An overview of each stage, along with important assumptions made at each, 
are presented below:
1) Imagery acquisition and user inputs

   	Here the user is asked to supply a video from the camera to be calibrated. SurfRCaT assumes that the user has obtained video(s)
	before using the tool. This typically requires permission from the camera owners/operators to download web-streaming video, as many
	surfcams are privately owned. TUTORIAL 1 provides more information.

	The user is also asked at this stage to provide initial estimates for 4 camera parameters: camera location (lat/lon), elevation,
	and azimuth viewing angle. In the absence of a site visit, we recommend using Google Earth to obtain these estimates (TUTORIAL 1
	provides an example). SurfRCaT assumes initial approximations for all other camera parameters as follows:

	+ SurfRCaT assumes lens distorion to be 0, i.e. does not account for it.
	+ SurfRCaT assumes camera focal length by assuming a 60 degree camera horizontal field of view
	+ SurfRCaT assumes the principal point coodinates to be the center of the image.
	+ SurfRCaT assumes the tilt of the camera to be 80 degrees
	+ SurfRCaT assumes the roll of the camera to be negligable. 

		> **Note**
		>
		> If your camera deviates largely from any of these assumptions (e.g. fisheye lens, small tilt), SurfRCaT may
		> not work well out of the box. Camera parameter assumptions are easy to change if you download the source code,
		> however the lens distortion assumption is not.

	SurfRCat extracts frames from the user-input video at a user-specified rate, and allows the user to choose a frame to use in the remote-GCP
	extraction (step 3). 

2) Lidar acquisition

	SurfRCaT searches FTP repositories of the National Oceanic and Atmospheric Administration (NOAA) to find archived airborne lidar datasets that
	cover the user-input camera location. These repositories contain thousands of datasets. The user is able to choose a dataset and SurfRCaT 
	automatically downloads a portion of that dataset proximal to the camera.

3) Remote-GCP extraction

	SurfRCaT facilitates the remote extraction of ground control points (GCPs) by prompting the user to identify (by clicking) corresponding
	points in the lidar data and camera image.

4) Calibration
	
	SurfRCaT uses the camera parameter inputs/assumptions (step 1) and the remote-GCPs (step 3) to complete the space resection process
	following the iterative methods presented in [1]. However, we augment those equations in [1] with the three intrinsic camera parameters that 
	are included here (focal length and principal point coordinates). 

5) Rectification

	The adjusted camera parameters are then used to rectify images from the camera to real-world coordinates. This occurs by finding the location in
	the image of every point within a user-specified grid, and then inverse mapping the color of the image at those points to their real-world 
	locations. The grid is assumed to be input in a coordinate system relative to the user-input camera location, with the y-axis (x-axis) in meters
	north (east) of this location.

	The rectification is also completed planimetrically at a user-input elevation. Technically speaking, then, the rectified product will be most
	accurate only for real-world points at this elevation. For the purposes of analyzing coastal geophysical processes, images are typically
	rectified to the observed tidal elevation, as we are typically most interested in features at or near the water line. An example and further
	guidance on this is given in both TUTORIALS.

### References ###

[1] Wolf, P. R., Dewitt, B., & Wilkinson, B. (2014). Elements of Photogrammetry with Applications in GIS. McGraw and Hill education.

[2] Holland, K. T., Holman, R. A., Lippmann, T. C., Stanley, J., & Plant, N. (1997). 
Practical use of video imagery in nearshore oceanographic field studies. IEEE Journal of oceanic engineering, 22(1), 81-92.







