# SurfRCaT

## What is it?

The surf-camera remote calibration tool (SurfRCaT) allows for the rectification of imagery from any coastal camera that views structures identifiable in lidar data.

## How do I use it?
1) Obtain imagery from your desired camera and seperate into images.  
Note: The Southeastern Coastal Ocean Observing Regional Association has deployed a network of 7 surfcams and made their imagery openly accessible ([see here](https://secoora.org/webcat/)). If you want to use one of these cameras, SurfRCaT will get the imagery for you! 
2) Obtain initial estimates of camera location, elevation, and azimuth (I like to use Google Earth).
3) Click on the link in the above description and download the zip file. 
4) Extract the zip file.
5) Enter "cmd" in the Windows search bar and open the Command Prompt app.
5) Click and drag the file SurfRCaT.exe from the extracted zip file into the command prompt and press enter.
6) Follow the onscreen instructions. 

## FAQ
1) How do I use the lidar point cloud viewer window to identify points?    
Answer: The point cloud viewer window is a functionality of the Point Processing Toolkit (pptk), an open-source python package. See the pptk documentation [here](https://heremaps.github.io/pptk/viewer.html) for instructions. We recommend rotating/translating/zooming your view until the point cloud looks similar to the image to help you identify corresponding features. **Important note: You must zoom the view in/out before translating/rotating it to maintain your view position.**
2) SurfRCaT seems like it froze. What do I do?  
Answer: SurfRCaT launches and runs some processes without any visual signature of doing so, making it look like the app has frozen when it really hasn't. So, give it a few minutes. If it still seems frozen, just close and re-launch. Note: The incorporation of a spinning wheel (or similar) while background processes run would be a welcome pull request!
