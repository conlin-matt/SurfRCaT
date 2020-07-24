## Tutorial 1- Quantify morphology with a pre-exisiting camera ##
In this tutorial, we will calibrate a pre-existing surfcam on the east coast of Florida and rectify some of its imagery in order to determine the dimensions
of a unique morphological feature. This tutorial is intended to get you familiar with the primary facilities and nuances of SurfRCaT in terms of calibrating 
a camera and then rectifying its imagery for geophysical applications. It is also intented to illustrate many of the considerations for using imagery from
recreational cameras for research-purposes. The video used in this example can be downloaded from [here](skldvnksdjnv).

> **NOTE**
>
> Prior permission from the camera owners/operators was obtained to save video from this camera. This is a requirement for working with 
> most pre-existing surfcams. Many are owned by private entities. Once permission is obtained, web-based video streams cna be save locally
> using a programming language or open-source web extensions/tools.							


1) Download/install and invoke the tool (see DOWNLOAD).
2) In the Welcome screen, select Calibrate a surfcam.
3) Choose a working directory for tool outputs to be saved to. I recommend creating one directory to contain the video and tool outputs. For this example,
I created a directory called "SurfRCaT_Example1", saved the video into it, and selected this as my working directory. SurfRCaT will create a subdirectory
in the working directory called "calibration_<video_name>" to store calibration results. Press Continue.
4) Input the values listed below within the "Any camera" box. Then use the "Browse" button to select the example video file in your
"SurfRCaT_Example1" directory as the video to use. Leave the "Used saved lidar point cloud?' field as "No". Then press Continue.
   + Name: StLucie_FL
   + Camera latitude: 27.16945
   + Camera longitude: -80.15834
   + Elevation: 21.5
   + Azimuth: 110

   > **Note**
   > 
   > These value estimates were obtained via Google Earth, which requires only an initial idea of camera position. Since the precise location/elevation of
   > surfcams is generally unknown, we see this as the best way to obtain these inputs. However,  Google Earth elevation values are generally unreliable-
   > in this example I counted the number of stories of the building that the camera sits atop and used this as the elevation estimate. 

5) The video decimation window will now open. This step allows you to extract frames from the video. We will use one of the frames to complete the remote
calibration. You can enter different decimation rates and click Update to see how many frames will be generated for a given rate. In this case, we only need
one image. Enter '5' in the Number of Frames field to generate 20 images, which will be saved to ../SurfRCaT_Example1/calibration_<video_name>/frames. 
We will be able to choose our favorite frame of the 20 in the next window. Press Continue.

   > **Note**
   >
   > This camera is not a pan-tilt-zoom (PTZ) camera, however many surfcams are. PTZ cameras periodically change their view between multiple 
   > presets. If working with a PTZ camera, it is a good idea to extract more frames from your video to ensure you obtain frames from the 
   > view that you are interested in. 


6) Choose your favorite frame by using the arrow buttons. Press Continue when you have found your favorite.
7) The tool will now automatically find airborne lidar datasets that cover the location of this camera. This is a two-step process; the tool will 
first search for nearby datasets and then examine those to find covering datasets. Press Continue when the processes finish.
8) The next window will display a table that shows all NOAA lidar datasets that cover the location of this camera, allowing you to select one to use
in the remote-GCP extraction. Select dataset 6330 (the second one) by checking its box, and then hit Continue. This will initiate the lidar download
process, which is completed in three steps: sorting tiles, downloading data, and formatting data. Press Continue when done. 

   > **Note**
   >
   > The lidar download process can be relatively time- and memory-intensive due to the large size of some datasets. See CONSIDERATIONS FOR USING SURFRCAT 
   > for more information. This dataset was downloaded in <3 minutes with a relatively slow internet connection, however dataset 8950 required  
   > 20 minutes to download with the same connection. 


9) You have now entered the GCP picking module, the heart of SurfRCaT. Here you will co-locate features in the camera image and lidar point cloud. First,
watch [this](xxxxyyyzzz) video showing the remote GCP-identification process.
10) Now, try it yourself. Press Go to begin the remote-GCP extraction. The lidar point cloud will open in a seperate window, though can take a couple
minutes to do so- please be patient. The Help button, when clicked, will display the steps necessary for identifying GCPs in the lidar data. First, zoom out
slightly, and then follow the steps in the Help menu to identify the four GCPs (in this order) shown in the video.

   > **Note**
   >
   > There is a bug with the viewer window that causes the view to get thrown off if you attempt to rotate it before first zooming in/out. 
	
11) Close the lidar viewer window, and identify the four corresponding points in the image (in the same order, as in the video). You can zoom and pan
the image with the navigation bar at the top. Press Done when done. If something happened during the GCP picking process and you are unhappy with the
GCPs you identified, you can re-do it using the Retry button. Otherwise, click Continue.
12) The Calibration Module window will now open. Press Calibrate and the tool will perform a least-squares camera calibration (see OVERVIEW OF
FUNDAMENTAL PRINCIPALS for more details). SurfRCaT will show the reprojected positions of each GCP in the next window. You should get results
resembling those shown below.  You can retry the Calibration by clicking the Retry button. Otherwise, press Continue.
13) A summary of the calibration process and results can be found in the file ../SurfRCaT_Example1/calibration_<video_name>/
results/calibrationSummary.csv.
14) The Rectification Module will now open. We will rectify the 5 frames that we extracted from the video. Since we have already extracted frames from this
video, we can skip Step 1. In Step 2, use the following for the inputs:
   + **Calibration results binary file**: browse to and select the calibration results binary file that is stored at ../SurfRCaT_Example1/calibration_<video_name>/_binaries/calibVals.pkl
   + **Input image directory**: browse to and select the frames subdirectory at ./SurfRCaT_Example1/calibration_<video_name>/frames 
   + **Save directory**: browse to and select the frames subdirectory at ./SurfRCaT_Example1/calibration_<video_name>/frames
   + **xmin**: 100
   + **xmax**: 350
   + **dx**: 1
   + **ymin**: -200
   + **ymax**: -50
   + **dy**: 1
   + **z**: -0.4,-0.4,-0.4,-0.4,-0.4

   > **Note** 
   >
   > Images are typically rectified to an elevation (z) equal to the observed tidal elevation (see REFERENCE). The closest NOAA water level station
   > indicates that -0.4 m (NAVD88) was the approximate observed tide level at the time of collection of these images (0850 LST). The [NOAA site]()
   > can help you determine tide level at the time of image collection at your site. See OVERVIEW OF PROCESSES AND ASSUMPTIONS for more information.
	

15) Press Continue, and SurfRCaT will rectify the five images. Products will be saved to the /SurfRCaT_Example1/calibration_<video_name>/frames directory.
The images should look similar to that shown below.

   > **Note**
   >
   > The rectified images are given a coordinate system relative to the user-input camera location. The y-axis is in meters north of the input camera 
   > location and the x-axis is in meters east of the input camera location. Analyses of images for geophysical applications often require a 	   
   > coordinate system transformation to one that is cross-shore distance (x) and long-shore distance (y). If you need to do this, simply add the 	   
   > camera location back to the coordinates and perform your transformation. 	           
	

16) Based on the rectified products, we will visually (and very roughly) estimate the dimensions of the sandbar in real-world space. By treating the 
left-most section of the bar as a triangle, and the right-most section as a rectangle, an overall area of the feature can be estimated as ~8000 m^2. 
Assuming an average elevation of the feature of 0.5 m (which is reasonable, from field observations), we can obtain a sediment volume within this feature
of ~4000 m^3, equivalent to approximately 440 standard dump trucks-worth of sediment.

   > **Note**
   >
   > The rectified products are also saved as Matlab and Python files. These  
   > can be imported into Python or Matlab for more detailed/precise analyses. See ANALYZING PRODUCTS IN PYTHON/MATLAB for more info. 
	

## Tutorial 2- prepare to analyze shoreline change from a WebCAT surfcam ##
In this tutorial, we will obtain videos from a surfcam in the WebCAT array, calibrate the camera, and then rectify an image from each video in 
to analyze shoreline change over time. This tutorial is intended to illustrate the integration of WebCAT cameras within SurfRCaT and 
how they can be exploited for geophysical applications (see INTEGRATION WITH THE WEBCAT ARRAY for more information). No external files are needed 
for this tutorial.

   > **Note**
   >
   > A camera calibration is, strictly speaking, only valid for the time the image used for the calibration was captured. Because cameras can #
   > change view angles slightly over time due to camera servicing, wind, and/or thermal expansion, to be most precise we will obtain calibrations for # 
   > both videos that we download here. SurfRCaT facilitates re-calibrations by allowing you to use already-downloaded point clouds, which means #
   > you only need to download a point cloud for a camera once. 
	

1) Download/install and invoke the tool (see DOWNLOAD).
2) We will download two videos from the Folly Beach Pier South camera. Create a directory called SurfRCaT_Example2. Within it, create two subdirectories,
one called FPS_Jan2019 and one called FPS_Apr2019.
3) In the Welcome screen, select "Download imagery from WebCAT camera." 
4) Select the Folly Beach Pier South camera as your desired camera. Then browse to and select the ../SurfRCat_Example2 as the save directory. We will 
download videos for January 1, 2019 at 1600 LST and April 22, 2019 at 1200 LST. To do so, enter the following in the remaining fields and press Download:
   + Year: 2019,2019	
   + Month: 01,04
   + Day: 01,22
   + Hour: 1600,1200

4) The videos will download to the ../SurfRCaT_Example2 directory. When they are downloaded, click and drag the January video into the ../SurfRCaT_Example2/
FPS_Jan2019 folder and the April video into the ../SurfRCaT_Example2/FPS_Apr2019 folder.
5) Press Back to start to return to the welcome window. Now we need to obtain camera calibrations for each video.
6) Select Calibrate a surfcam.
7) Browse to the ../SurfRCaT_Example2/FPS_Jan2019 directory and select it as your working directory. Press Continue.
8) Since we are using a WebCAT camera, we will fill in the "WebCAT camera" box. Select the Folly Beach Pier South camera from the dropdown list, and then
browse to and select the video follypiersouthcam.2020-01-01_1600.mp4 as the video to use. Leave the "Used saved lidar point cloud?' field as "No". Press 
Continue.
9) After a couple seconds, the video decimator window will open. This step allows you to extract frames from the video. We will use one of the frames to complete the remote
calibration. You can enter different decimation rates and click Update to see how many frames will be generated for a given rate. We only need one image
to complete the calibration. However, this is a pan-tilt-zoom (PTZ) camera, which means it rotates between multiple (3 in this case) view presets. We should
therefore extract more than 1 frame in order to ensure we get an image from the view that we are interested in. Enter '25' in the Number of Frames field
to generate 25 images, which will be saved to ../SurfRCaT_Example2/FPS_Jan2019/calibration_follypiersouthcam.2020-01-01_1600/frames. We will be able to choose our 
favorite frame of the 25 in the next window. Press Go.
10) When the next window opens, use the arrow buttons to scroll through the extracted images to one in which the pier is visible. Press Continue.
11) The next window will display a table that shows all NOAA lidar datasets that cover the location of this camera, allowing you to select one to use
in the remote-GCP extraction. Select dataset 5184 (the second one) by checking its box, and then hit Continue. This will initiate the lidar download
process, which is completed in three steps: sorting tiles, downloading data, and formatting data. Press Continue when the processes finish. 

   > **Note**
   >
   > The lidar download process can be relatively time- and memory-intensive due to the large size of some datasets. See CONSIDERATIONS FOR USING SURFRCAT 
   > for more information. This dataset was downloaded in 7 minutes with a relatively slow internet connection.
	

12) You have now entered the GCP picking module, the heart of SurfRCaT. Here you will co-locate features in the camera image and lidar point cloud. First,
watch [this](xxxxyyyzzz) video showing the remote GCP-identification process.
13) Now, try it yourself. Press Go to begin the remote-GCP extraction. The lidar point cloud will open in a seperate window, though can take a couple
minutes to do so- please be patient. The Help button, when clicked, will display the steps necessary for identifying GCPs in the lidar data. First, zoom out
slightly, and then follow the steps in the Help menu to identify the four GCPs (in this order) shown in the video.

   > **Note**
   >
   > There is a bug with the viewer window that causes the view to get thrown off if you attempt to rotate it before first zooming in/out. 


14) Close the lidar viewer window, and identify the four corresponding points in the image (in the same order, as in the video) by clicking on
them. You can zoom and pan the image with the navigation bar at the top. Press Done when done. If something happened during the GCP picking process 
and you are unhappy with the GCPs you identified, you can re-do it using the Retry button. Otherwise, click Continue.
15) The Calibration Module window will now open. Press Calibrate and the tool will perform a least-squares camera calibration (see OVERVIEW OF
FUNDAMENTAL PRINCIPALS for more details). SurfRCaT will show the reprojected positions of each GCP in the next window. You should get results
resembling those shown below. You can retry the Calibration by clicking the Retry button. Otherwise, press Continue. 
16) A summary of the calibration process and results can be found in the file ../SurfRCaT_Example2/FPS_Jan2019/calibration_follypiersouthcam.2020-01-01_1600/
results/calibrationSummary.csv. 
17) The Rectification Module will now open. 
18) Now, we need to calibrate the camera for the other video that we downloaded. Click the Back button to go back to the first window of the tool.
19) Like before, select Calibrate a surfcam, but this time browse to and select the ../SurfRCaT_Example2/FPS_Apr2019 directory as your working
directory.
20) Like before, in the "WebCAT camera" box, select the Folly Pier South camera from the dropdown list. This time, though, browse to and select the 
video follypiersouthcam.2020-04-22_1200.mp4 as the video to use and change the "Use saved lidar point cloud?' field to "Yes". Use the new browse button
to browse to and select the lidar point cloud that was downloaded for the last video, located at ../SurfRCaT_Example2/FPS_Jan2019/
calibration_follypiersouthcam.2020-01-01_1600/products/lidarPC.pkl. Press Continue.
21) Follow steps 9-16 again to calibrate the camera for this video, but this time the lidar download process (step 11) will not appear. 
22) The summary file for this calibration will be loacted at ../SurfRCaT_Example1/FPS_Apr2019/calibration_follypiersouthcam.2020-04-22_1200/results/
calibrationSummary.csv.
22) Now we will rectify a frame from each video. We will first extract a single frame from each video to rectify. In the Step 1 box, browse to and 
select the January video as the Video file. Browse to and select the ../SurfRCat_Example2/FPS_Jan2019 folder as the save directory. Click the Extract
Frames Button.
23) Enter 1 in the Number of Frames box and click Go. The frame will be extracted and saved at ../SurfRCat_Example2/FPS_Jan2019/frames and the decimator 
window will close. 
24) In the Step 2 box, use the following for the inputs:
   +**Calibration results binary file**: browse to and select the calibration results binary file that is stored at ../SurfRCat_Example2/
						FPS_Jan2019/calibration_follypiersouthcam.2019-01-01_1600/_binaries/calibVals.pkl.
   + **Input image directory**: leave as is
   + **Save directory**: browse to and select ../SurfRCat_Example2/FPS_Jan2019
   + **xmin**: 0
   + **xmax**: 200
   + **dx**: 1
   + **ymin**: -250
   + **ymax**: -50
   + **dy**: 1
   + **z**: 0.5  

   > **Note**
   >
   > Images are typically rectified to an elevation (z) equal to the observed tidal elevation (see REFERENCE). The two videos used in this tutorial 
   > were chosen because the closest NOAA water level station indicates that 0.5 m (NAVD88) was the approximate observed tide level during both.    
   > The [NOAA site]() can help you determine tide level at the time of image collection at your site. See OVERVIEW OF PROCESSES AND ASSUMPTIONS for more    
   > information.
	
25) Press continue, and the image will be rectified and saved. The press 'Rectify more images'.
26) Follow steps 22-25 for the April video to rectify a frame from that video as well. You should get results resembling those below. 
27) Based on these products, there was shoreline advance between January 1 2019 and April 22 2019. While the tidal elevation was the same for both images,
this apparant advance could be driven by morpholgoical changes and/or differences in wave setup, which has not been accounted for. Additionally, it is apparent than the view
angle of the camera changed slightly, illustrating the importance of performing separate calibrations for both videos.

   > **Note**
   >
   > The rectified images are given a coordinate system relative to the user-input camera location. The y-axis is in meters north of the input camera
   > location and the x-axis is in meters east of the input camera location. Analyses of images for geophysical applications often require a 	   
   > coordinate system transformation to one that is cross-shore distance (x) and long-shore distance (y). If you need to do this, simply add the 	   
   > camera location back to the coordinates and perform your transformation. 	           


   > **Note**
   >
   > The rectified products are also saved as Python dictionaries in the /SurfRCaT_Example1/calibration_<video_name>/products directory. These  
   > can be imported into Python or Matlab for more detailed/precise analyses. See ANALYZING PRODUCTS IN PYTHON/MATLAB for more info. 





