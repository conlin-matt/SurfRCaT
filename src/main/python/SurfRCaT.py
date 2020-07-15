# -*- coding: utf-8 -*-
"""
Main functions utilizied by the Surfcamera Remote
Calibration Tool. These functions are called by the front-end user interface.

Created by Matthew P. Conlin, University of Florida

"""

__copyright__ = 'Copyright (c) 2020, Matthew P. Conlin'
__license__ = 'GPL-3.0'
__version__ = '1.0'


#============================================================================#
# Get WebCAT video #
#============================================================================#
def getImagery_GetVideo(pth,camToInput,year=2019,month=11,day=1,hour=1000):
    
    """
    Function to download a video clip from a specified WebCAT camera to local directory. The desired year, month, day, and time can be given, 
    however for those not given the function will use default values. If you don't like the video from the default date, an examination of WebCAT
    clips on the website can help determine the desired date/time to use. 
    
    Inputs:
        pth: (string) File location to save file to
        camToInput: (string) name of WebCAT camera you want imagery for
        year: (int) year of date you want video for
        month: (int) month of date you want video for
        day: (int) day of date you want video for
        hour: (int) hour of date you want video for
        
    Outputs:
        vidFile: (string) path to downloaded video file 
    
    """
    
    import requests
    
    # Add zeros to day and month values if needed #
    if month<10:
        month = '0'+str(month)
    else:
        month = str(month)
    
    if day<10:
        day = '0'+str(day)
    else:
        day = str(day)
       
    # Get the video URL # 
    url = 'http://webcat-video.axds.co/{}/raw/{}/{}_{}/{}_{}_{}/{}.{}-{}-{}_{}.mp4'.format(camToInput,year,year,month,year,month,day,camToInput,year,month,day,hour)   
    
    # Read and load the video file from that URL #
    filename = url.split('/')[-1] # Get the filename as everything after the last backslash #
    r = requests.get(url,stream = True) # Create the Response Object, which contains all of the information about the file and file location %
    with open(pth+filename,'wb') as f: # This loop does the downloading 
        for chunk in r.iter_content(chunk_size = 1024*1024):
            if chunk:
                f.write(chunk)
    
    ## The specified video is now saved to the directory ##
    
    # Get the video file name #
    vidFile = camToInput+'.'+str(year)+'-'+month+'-'+day+'_'+str(hour)+'.mp4'
       
    return vidFile


#=============================================================================#
# Get camera stills #
#=============================================================================#
def getImagery_GetStills(vid,secondsPerFrame,rate,vidLen,fps,saveBasePth):

    import cv2
    import numpy as np
    import os

    # Create new directory to house the stills #
    os.mkdir(saveBasePth+'frames')
    

    cap = cv2.VideoCapture(vid)

    
    # If there was an input decimation rate (which means secondsPerFrame=1), determine the frame numbers to pull each second
    # by evenly spacing the frame rate in the known frames per second. If there was an input number of frames (which means
    # secondsPerFrame != 1), determine the middle frame for each second to be pulled based on the frames per second. #
    if secondsPerFrame == 1:
        framesEachSecond = np.round(np.linspace(0,fps,rate))
    else:
        framesEachSecond = [int(round(fps/2))]

    
    totalFrames = 0
    for i in range(0,int(round(vidLen)),secondsPerFrame):
        for ii in framesEachSecond:
            frame = totalFrames+ii
            cap.set(1,frame)
            test,im = cap.read()
            cv2.imwrite(saveBasePth+'frames/frame'+str(int(i))+'.png',im)
        totalFrames = totalFrames+(fps*secondsPerFrame)





    

    
##    framesKeep = np.round(np.linspace(0,numFrames,50)) # 50 frames from the 10 minute video = 1 frame every 12 seconds #
##
##    for i in framesKeep:
##        
##        cap.set(1,int(i))
##        test,im = cap.read()
##        
##        if test:
##            cv2.imwrite(vid.split('.')[0]+vid.split('.')[1]+'_frames/frame'+str(int(i))+'.png',im)


#=============================================================================#



#=============================================================================#
# Search for and identify lidar datasets that cover camera location #
#=============================================================================#
def getLidar_FindPossibleIDs(cameraLoc_lat,cameraLoc_lon):

    '''
    First function in the lidar download process. Finds the dataset IDs of all lidar
    datasets that could be close to the camera based on its location (and derived state
    and coast). Function searches through a NOAA-provided table fo datasets and extracts
    only the IDs of datasets that may be close to the camera. 
    
    Inputs:
        cameraLoc_lat: (float) Latitude location of camera
        cameraLoc_lon: (float) Longitude location of camera
    
    Outputs:
        IDs: (List) A list containing the dataset IDs of possibly proximal datasets.
        
    '''

    
    import pandas as pd
    import requests
    import reverse_geocoder as rg

    # Find what state the camera is in based on its location #
    placeDict = rg.search((cameraLoc_lat,cameraLoc_lon))

    # Establish dictionaries for state abbreviation and coast based on state, and get this info for the state #
    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands':'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Palau': 'PW',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
    }

    coastDict = {
        'Alabama': 'Gulf',
        'Alaska': 'West',
        'Arizona': '',
        'Arkansas': '',
        'California': 'West',
        'Colorado': '',
        'Connecticut': 'East',
        'Delaware': 'East',
        'Florida': '', # Special consideration, see below #
        'Georgia': 'East',
        'Hawaii': 'West',
        'Idaho': '',
        'Illinois': '',
        'Indiana': '',
        'Iowa': '',
        'Kansas': '',
        'Kentucky': '',
        'Louisiana': 'Gulf',
        'Maine': 'East',
        'Maryland': 'East',
        'Massachusetts': 'East',
        'Michigan': '',
        'Minnesota': '',
        'Mississippi': 'Gulf',
        'Missouri': '',
        'Montana': '',
        'Nebraska': '',
        'Nevada': '',
        'New Hampshire': 'East',
        'New Jersey': 'East',
        'New Mexico': '',
        'New York': 'East',
        'North Carolina': 'East',
        'North Dakota': '',
        'Ohio': '',
        'Oklahoma': '',
        'Oregon': 'West',
        'Pennsylvania': '',
        'Puerto Rico': 'East',
        'Rhode Island': 'East',
        'South Carolina': 'East',
        'South Dakota': '',
        'Tennessee': '',
        'Texas': 'Gulf',
        'Utah': '',
        'Vermont': '',
        'Virginia': 'East',
        'Washington': 'West',
        'West Virginia': '',
        'Wisconsin': '',
        'Wyoming': '',
    }
    
    state = placeDict[0]['admin1']
    try: # If not a US state, this will throw an error #
        state_abbrev = us_state_abbrev[state]
        # Get coast, and deal with determining coast for Florida #
        if state == 'Florida':
            if cameraLoc_lat>26:
                if cameraLoc_lon<-81.5:
                    coast = 'Gulf'
                else:
                    coast = 'East'
            else:
                if cameraLoc_lon<80.5:
                    coast = 'Gulf'
                else:
                    coast = 'East'
        else: 
            coast = coastDict[state]

        # Get the data table from NOAAs website #
        url = 'https://coast.noaa.gov/htdata/lidar1_z/'
        html = requests.get(url).content
        df_list = pd.read_html(html)
        dataTable = df_list[-1]
        
        # Make a list of all IDs and geography names #
        IDlist = dataTable.loc[:,'ID #']
        nameList = dataTable.loc[:,'Geography']

        # Find all the IDs that contain the state, state abbrev, or coast name in their name and keep them #
        IDs = list()
        for n,i in zip(nameList,IDlist):
            if state in n or state_abbrev in n or coast in n:
                IDs.append(i)
    except:
        IDs = list()

    return IDs



        
def getLidar_TryID(ftp,alldirs,ID,cameraLoc_lat,cameraLoc_lon):
    
    '''
    Function to go through a lidar dataset and determine if it covers the location of the camera. If
    it does, the lidar dataset ID is saved. Function takes advantage of a csv file given to each dataset on the NOAA
    repositories which gives the min and max extents of the dataset.
    
    Inputs:
        ftp: (string) The ftp site address
        ID: (int) A lidar dataset ID
        cameraLoc_lat: (float) Latitude location of camera
        cameraLoc_lon: (float) Longitude location of camera
        
    Outputs:
        check: (int) A yes (1) or no (0) as to if this dataset covers the camera location 
    '''
    
    import ftplib
    from io import StringIO
    from pandas import read_csv

    # Get into the correct NOAA FTP site ##
    for i in alldirs:
        for ii in i:
            try:
                ftp.cwd(ii+'/data/'+str(ID))
            except:
                pass
            else:
                break
                    
        
    # Find the minmax csv file which shows the min and max extents of each tile within the current dataset #
    files = ftp.nlst()
    fileWant = str([s for s in files if "minmax" in s])
    if fileWant:
        if len(fileWant)>2:
            # Get the file name and save it. We need to get rid of the ' or " in the name. Sometimes this means we need to get rid of the first 2 characters, sometimes the first 3 #
            if len(fileWant.split()) == 2:
                fileWant = '['+fileWant.split()[1]
            fileWant = fileWant[2:len(fileWant)-2]


            # Save the file locally #
            gfile = open('minmax.csv','wb') # Create the local file #
            ftp.retrbinary('RETR '+fileWant,gfile.write) # Copy the contents of the file on FTP into the local file #
            gfile.close() # Close the remote file #
        
        
            # See if the location of the camera is contained within any of the tiles in this dataset. If it is, save the ID #

            dat = read_csv('minmax.csv')
            minx = dat[' min_x']
            maxx = dat[' max_x']
            miny = dat[' min_y']
            maxy = dat[' max_y']

            test = dat[(maxx>=cameraLoc_lon) & (minx<=cameraLoc_lon) & (maxy>=cameraLoc_lat) & (miny<=cameraLoc_lat)]
            check = list()
            if not test.empty:
                check.append(1)
    
            return check
        

def getLidar_GetDatasetNames(appropID):
    
    '''
    Function to link the ID of each lidar dataset found to cover the camera with the name and other metadata of the dataset.
    
    Inputs:
        appropID: (int) The ID of a dataset found to cover the camera by the getLidar_TryID function
        
    Outputs:
        matchingTable: (DataFrame) A DataFrame giving each ID linked to metadata (name, date, etc.)
        
    '''
    
    import pandas as pd
    import requests
    
    # Get the data table from NOAAs website #
    url = 'https://coast.noaa.gov/htdata/lidar1_z/'
    html = requests.get(url).content
    df_list = pd.read_html(html)
    dataTable = df_list[-1]
    
    # Make a list of all IDs and names #   
    IDlist = dataTable.loc[:,'ID #']
    nameList = dataTable.loc[:,'Dataset Name']  
    
    # Find the indicies in the data table that match the appropriate IDs # 
    appropIDNums = list(map(int,appropID))  
    matchingTableRows = [i for i, x in enumerate(IDlist) for j,y in enumerate(appropIDNums) if x==y] # Get indicies of matching IDs in the dataTable
    
    # Create a new data frame with data for the appropriate IDs #
    matchingTable = pd.DataFrame(columns=['ID','Year Collected','Name'])
    matchingTable.loc[:,'ID'] = IDlist[matchingTableRows]
    matchingTable.loc[:,'Year Collected'] = dataTable.loc[:,'Year'][matchingTableRows]
    matchingTable.loc[:,'Name'] = nameList[matchingTableRows]
    
    return matchingTable

#=============================================================================#


#=============================================================================#
# Prepare and download the chosen dataset
#=============================================================================#
def getLidar_CalcViewArea(az,window,dmax,lat,lon):

    '''
    Function to calculate a polygon of the expected geographic view area of the camera. The polygon
    is calculated as a triangle extending dmax km in the azimuth direction of the camera +- a tolerance.
    Any lidar dataset tiles that intersect with this polygon will be kept.

    Inputs:
        az: (float) The estimated azimuth of the camera
        window: (float) The tolerance to use around az to calculate the polygon (I use 40 degrees)
        dmax: (float) The maximum distance in the az direction of the camera of the polygon (I use 1 km)
        lat: (float) The latitude of the camera
        lon: (float) The longitude of the camera

    Outputs:
        poly: (object) The polygon object
        
    '''
    
    from math import sin,cos,tan,sqrt,radians
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import path
    import utm

    # Convert lat lon of camera to UTM #
    camLoc_x = utm.from_latlon(lat,lon)[0]
    camLoc_y = utm.from_latlon(lat,lon)[1]

    # Calculate x and y distance to farthest point along azimuthal line #
    # and lines at angles of az+-window #
    dx0 = dmax*cos(radians(90-az))
    dy0 = dmax*sin(radians(90-az))

    dx1 = dmax*cos(radians(90-(az-window)))
    dy1 = dmax*sin(radians(90-(az-window)))

    dx2 = dmax*cos(radians(90-(az+window)))
    dy2 = dmax*sin(radians(90-(az+window)))

    # Calculate the verticies of the endpoints, defining the polygon #
    xmax0 = camLoc_x+dx0
    ymax0 = camLoc_y+dy0

    xmax1 = camLoc_x+dx1
    ymax1 = camLoc_y+dy1

    xmax2 = camLoc_x+dx2
    ymax2 = camLoc_y+dy2

    # Create the polygon object #
    poly = path.Path([(camLoc_x,camLoc_y),(xmax1,ymax1),(xmax0,ymax0),(xmax2,ymax2),(camLoc_x,camLoc_y)])

    return poly   


def getLidar_GetShapefile(IDToDownload):
    
    '''
    Function to get the shapefile of a tile of the chosen lidar dataset. We will use the shapefile
    to determine if the tile is near the camera, to avoid downloading a bunch of data not near the camera.
    
    Inputs:
        IDToDownload: (int) ID of chosen lidar dataset, returned by the checkbox from user input.
        
    Outputs:
        sf: (object) The shapefile of the tiles
        
    '''
    
    import ftplib
    import shapefile

    # Get to the correct FTP site and get all the files #
    ftp = ftplib.FTP('ftp.coast.noaa.gov',timeout=1000000)
    ftp.login('anonymous','anonymous')

    try:
        ftp.cwd('/pub/DigitalCoast/lidar1_z/geoid12b/data/'+str(IDToDownload))
    except:
        try:
            ftp.cwd('/pub/DigitalCoast/lidar2_z/geoid12b/data/'+str(IDToDownload))
        except:
            try:
                ftp.cwd('/pub/DigitalCoast/lidar3_z/geoid12b/data/'+str(IDToDownload))
            except:
                try:
                    ftp.cwd('/pub/DigitalCoast/lidar1_z/geoid12a/data/'+str(IDToDownload))
                except:
                    ftp.cwd('/pub/DigitalCoast/lidar3_z/geoid18/data/'+str(IDToDownload))
                    
    files = ftp.nlst()

    # Load the datset shapefile and dbf file from the ftp. These describe the tiles #
    shpFile = str([s for s in files if "shp" in s])
    shpFile = shpFile[2:len(shpFile)-2]
    dbfFile = str([s for s in files if "dbf" in s])
    dbfFile = dbfFile[2:len(dbfFile)-2]

    # Write them locally so we can work with them #
    gfile = open('shapefileCreate.shp','wb') # Create the local file #
    ftp.retrbinary('RETR '+shpFile,gfile.write)

    gfile = open('shapefileCreate.dbf','wb') # Create the local file #
    ftp.retrbinary('RETR '+dbfFile,gfile.write)

    # Load them into an object using the PyShp library #
    sf = shapefile.Reader("shapefileCreate.shp")
    
    return sf



def getLidar_SearchTiles(sf,poly,shapeNum,cameraLoc_lat,cameraLoc_lon):

    '''
    Function to determine if a tile is within the calculated view area of the camera 
    
    Inputs: 
        sf: (object) The shapefile of the tiles returned by getLidar_GetShapefile function
        poly (object) The camera view polygon object returned by getLidar_CalcViewArea function
        shapeNum: (int)The tile number
        cameraLoc_lat: (float) Latitude of camera
        cameraLoc_lon: (float) Longitude of camera
    
    Outputs:
        rec['name']: (string) The name of the tile if any part of it is within the view polygon
        
    '''
    
    import utm
    import math
    import numpy
    from matplotlib import path
    
    # Establish the location of the camera in UTM coordinates #
    cameraLoc_UTMx = utm.from_latlon(cameraLoc_lat,cameraLoc_lon)[0]
    cameraLoc_UTMy = utm.from_latlon(cameraLoc_lat,cameraLoc_lon)[1]
    
    # Get the bounding box of the tile in UTM
    bx = sf.shape(shapeNum).bbox 
    bx_bl = utm.from_latlon(bx[1],bx[0]) 
    bx_br = utm.from_latlon(bx[1],bx[2]) 
    bx_tr = utm.from_latlon(bx[3],bx[2]) 
    bx_tl = utm.from_latlon(bx[3],bx[0])
    
    # If any verticies of the bounding box are within the polygon, keep the tile #

##    try:
##        rec = sf.record(shapeNum)
##        if poly.contains_points([(bx_bl[0],bx_bl[1])]) or poly.contains_points([(bx_br[0],bx_br[1])]) or poly.contains_points([(bx_tl[0],bx_tl[1])]) or poly.contains_points([(bx_tr[0],bx_tr[1])]):
##            return rec['Name']
##    except:
##        pass
    # If any of the tile edges intersect the bounding box, keep the tile #
##    try:

    rec = sf.record(shapeNum)
    if poly.intersects_path(path.Path([(bx_bl[0],bx_bl[1]),(bx_br[0],bx_br[1])])) or poly.intersects_path(path.Path([(bx_tl[0],bx_tl[1]),(bx_tr[0],bx_tr[1])])) or poly.intersects_path(path.Path([(bx_bl[0],bx_bl[1]),(bx_tl[0],bx_tl[1])])) or poly.intersects_path(path.Path([(bx_br[0],bx_br[1]),(bx_tr[0],bx_tr[1])])):
        return(rec['Name'])
        
##    except:
##        pass
##                        

def getLidar_Download(thisFile,IDToDownload,cameraLoc_lat,cameraLoc_lon):
    
    '''
    Function to download a tile of the selected lidar dataset using the PDAL module
    
    Inputs:
        thisFile: (str)the tile to download
        IDToDownload: (int) The ID of the dataset being downloaded
        cameraLoc_lat: (float) Latitude of camera
        cameraLoc_lon: (float) Longitude of camera
        
    Outputs:
        lidarXYZsmall: XYZ point cloud, as an nx3 array, of the lidar data
        
    '''
            
    import ftplib
    import numpy
    import math
    import json    
    import pdal

    # Get to the right FTP #      
    ftp = ftplib.FTP('ftp.coast.noaa.gov',timeout=1000000)
    ftp.login('anonymous','anonymous')
    
    try:
        ftp.cwd('/pub/DigitalCoast/lidar1_z/geoid12b/data/'+str(IDToDownload))
    except:
        try:
            ftp.cwd('/pub/DigitalCoast/lidar2_z/geoid12b/data/'+str(IDToDownload))
        except:
            try:
                ftp.cwd('/pub/DigitalCoast/lidar3_z/geoid12b/data/'+str(IDToDownload))
            except:
                try:
                    ftp.cwd('/pub/DigitalCoast/lidar1_z/geoid12a/data/'+str(IDToDownload))
                except:
                    ftp.cwd('/pub/DigitalCoast/lidar3_z/geoid18/data/'+str(IDToDownload))
 
           
    # Save the laz file locally #
    gfile = open('lazfile.laz','wb') # Create the local file #
    ftp.retrbinary('RETR '+thisFile,gfile.write) # Copy the contents of the file on FTP into the local file #
    gfile.close() # Close the remote file #
        
    # Construct the json PDAL pipeline to read the file and take only points within +-.5 degree x and y of the camera. Read the data in as an array #
    utm_band = str((math.floor((cameraLoc_lon+180)/6)%60)+1)
    if len(utm_band) == 1:
        utm_band = '0'+utm_band
    epsg = '326'+utm_band

    fullFileName = 'lazfile.laz'
    pipeline=(json.dumps([{'type':'readers.las','filename':fullFileName},{'type':'filters.range','limits':'X['+str(cameraLoc_lon-.5)+':'+str(cameraLoc_lon+.5)+'],Y['+str(cameraLoc_lat-.5)+':'+str(cameraLoc_lat+.5)+']'},{'type':'filters.reprojection','in_srs':'EPSG:4326','out_srs':'EPSG:'+epsg}],sort_keys=False,indent=4))
        
    # Go through the pdal steps to use the pipeline
    r = pdal.Pipeline(pipeline)  
    r.validate()  
    r.execute()
        
    # Get the arrays of data and format them so we can use them #
    datArrays = r.arrays
    datArrays = datArrays[int(0)] # All of the fields are now accessable with the appropriate index #
    
    # Extract x,y,z values #
    lidarX = datArrays['X']
    lidarY = datArrays['Y']
    lidarZ = datArrays['Z']

##    # Only take points within 500 m of the camera #
##    R = 6373000 # ~radius of Earth in m #
##    dist = list()
##    for px,py in zip(lidarX,lidarY):
##        dlon = math.radians(abs(px)) - math.radians(abs(cameraLoc_lon))
##        dlat = math.radians(abs(py)) - math.radians(abs(cameraLoc_lat))
##        a = math.sin(dlat/2)**2 + math.cos(math.radians(abs(py))) * math.cos(math.radians(abs(cameraLoc_lat))) * math.sin(dlon/2)**2
##        c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
##        dist.append(R*c)
##
##    lidarXsmall = list()
##    lidarYsmall = list()
##    lidarZsmall = list()    
##    for xi,yi,zi,di in zip(lidarX,lidarY,lidarZ,dist):
##        if di<1000:
##            lidarXsmall.append(xi)
##            lidarYsmall.append(yi)
##            lidarZsmall.append(zi)
##    lidarXYZsmall = numpy.vstack((lidarXsmall,lidarYsmall,lidarZsmall))
##    lidarXYZsmall = numpy.transpose(lidarXYZsmall)
    lidarXYZsmall = numpy.vstack((lidarX,lidarY,lidarZ))
    lidarXYZsmall = numpy.transpose(lidarXYZsmall)    
    return lidarXYZsmall



def getLidar_CreatePC(lidarDat,cameraLoc_lat,cameraLoc_lon): 
    
    '''
    Fucntion to convert lidar point cloud (in lat/lon coords) to one in UTM coords
    relative to the location of the camera (camera location set as origin)
    
    Inputs:
        lidarDat: (array) The XYZ lidar point cloud returned by getLidar_Download function
        cameraLoc_lat: (float) Latitude of camera
        cameraLoc_lon: (float) Longitude of camera
    
    Outputs:
        pc: (array) The new point cloud, for use in future functions
        
    '''

    import utm
    import numpy  as np
    import pandas as pd
    
    pc = pd.DataFrame({'x':lidarDat[:,0],'y':lidarDat[:,1],'z':lidarDat[:,2]})
    
    utmCam = utm.from_latlon(cameraLoc_lat,cameraLoc_lon)
    pc['x'] = pc['x']-utmCam[0]
    pc['y'] = pc['y']-utmCam[1]

##    # Convert eveything to UTM and translate to camera at (0,0) #
##    utmCoords = utm.from_latlon(np.array(pc['y']),np.array(pc['x']))
##    utmCoords = np.hstack([np.reshape(utmCoords[0],[np.size(utmCoords[0]),1]),np.reshape(utmCoords[1],[np.size(utmCoords[1]),1])])
##        
##    utmCam = utm.from_latlon(cameraLoc_lat,cameraLoc_lon)
##
##    # Translate to camera position #
##    utmCoords[:,0] = utmCoords[:,0]-utmCam[0]
##    utmCoords[:,1] = utmCoords[:,1]-utmCam[1]
##    
##    # Put these new coordinates into the point cloud %
##    pc['x'] = utmCoords[:,0]
##    pc['y'] = utmCoords[:,1]
    
    return pc



#=============================================================================#
# Perform Calibration #
#=============================================================================#
def calibrate_GetInitialApprox_IOPs(img):
    
    '''
    Get initial approximatation for camera IOPs (focal length (f) and principal points (x0,y0)) using the geometry of the image.Estimate
    focal length by assuming a horizontal field of view of 60 degrees (typical of webcams), and using simple geometry with this and
    the width of the image. Estimate principal points as the center of the image.

    Inputs:
        img: (array) The image to used for GCP picking

    Outputs:
        f: (float) initial approximation for focal length (in pixels)
        x0: (float) initial approximation for x principal point coordinate #
        y0: (float) initial approximation for y principal point coordinate #
        
    '''
    
    import math

    # Estimare focal length using assumed FOV of 60 degrees and the measured width of the image #
    w = len(img[1,:,:]) # Get the sensor width as the image width #
    a = math.radians(60)
    f = (w/2)*(1/math.tan(a/2))

    # Estimate principal point coords as center of the image #
    x0 = len(img[1,:,1])/2
    y0 = len(img[:,1,1])/2
    
    return f,x0,y0



def calibrate_GetInitialApprox_ats2opk(a,t,s):
    
    '''
    Get initial approximations for the three needed camera look-angles by using easily estimated azimuth, tilt, and swing. These angles
    are converted to the omega,phi,kappa convention by forming the rotation matrix via azimuth,tilt,swing and decomposing it
    to obtain the omega,phi,kappa angles.
    
    Reference: Wolf, Dewitt, and Wilkinson. Elements of Photogrammetry with Applications in GIS, 4th ed. 
    
    Inputs:
        a: (float) Estimated azimuth of the camera (in degrees)
        t: (float) Estimated tilt of the camera (in degrees). I use 80 degrees for webcams.
        s: (float) Estimated swing og the camera (in degrees). I use 180 degrees (i.e. no swing) for webcams.

    Outputs:
        omega: (float) Initial approximation for omega for the camera (in radians)
        phi: (float) Initial approximation for phi for the camera (in radians)
        kappa: (float) Initial approximation for kappa for the camera (in radians)
    
    '''
    import math

    # Convert inputs in degrees to radians #
    a = math.radians(a)
    t = math.radians(t)
    s = math.radians(s)
    
    # Create the rotation matrix with the ats convention #
    m11 = -(math.cos(a)*math.cos(s)) - (math.sin(a)*math.cos(t)*math.sin(s))
    m12 = (math.sin(a)*math.cos(s)) - (math.cos(a)*math.cos(t)*math.sin(s))
    m13 = -math.sin(t)*math.sin(s)
    m21 = (math.cos(a)*math.sin(s)) - (math.sin(a)*math.cos(t)*math.cos(s))
    m22 = (-math.sin(a)*math.sin(s)) - (math.cos(a)*math.cos(t)*math.cos(s))
    m23 = -math.sin(t)*math.cos(s)
    m31 = -math.sin(a)*math.sin(t)
    m32 = -math.cos(a)*math.sin(t)
    m33 = math.cos(t)
    
    # Get omega,phi,kappa from the matrix #
    phi = math.asin(m31)
    omega = math.atan2(-m32,m33)
    kappa = math.atan2(-m21,m11)
    
    return omega,phi,kappa


    
def calibrate_PerformCalibration(initApprox,freeVec,gcps_im,gcps_lidar):
    
        '''
        Perform the augmented space resection using the initial approximations for all parameters
        input to this function.

        Reference: Wolf, Dewitt, and Wilkinson. Elements of Photogrammetry with Applications in GIS, 4th ed. 
        
        Inputs:
            initApprox: (array) A vector containing the initial approximations for all nine parameters, in the order:
                        omega,phi,kappa,XL,YL,ZL,f,x0,y0
            freeVec: (array) A vector that defines the terms that are free to change and those that fixed during the adjustment. Each element corresponds
                     to the same positioned element in initiApprox. A value of 1 indiciates the parameter is fixed, a value of 0 indicates it is free to change. 
            gcps_im: (array) The array of image coordinates of ground control points
            gcps_lidar: (array) The array of world-coordinates of ground control points
        
        Outputs:
            valsVec: (array) A vector containing the final values for each parameter after adjustment, in the same order as in initApprox
            So: (array) The standard error of unit weight for each iteration of the adjustment. 
        
        '''
        import math
        import numpy as np
        
        unknowns = np.where(freeVec==0)[0] # Indicies of unknown values #

        # Matrix to store the values (rows) for each parameter (columns) as the least squares solution iterates and other empty arrays #
        allvals = np.empty([0,len(unknowns)]) 
        Delta = np.ones(len(unknowns))
        So = np.empty([0,1]) 
        valsVec = initApprox

        # This while loop performs the least-squares adjustment #
        iteration = 0
        while np.max(np.abs(Delta))>.00001:
            
            omega = valsVec[0]
            phi = valsVec[1]
            kappa = valsVec[2]
            XL = valsVec[3]
            YL = valsVec[4]
            ZL = valsVec[5]
            f = valsVec[6]
            x0 = valsVec[7]
            y0 = valsVec[8]

            # If we get over 1200 iterations, the solution probably isn't converging and we should stop #
            iteration = iteration+1
            if iteration>1200:
                print('Error: The soultion is likely diverging')
                break
            else:
                pass
            
            if iteration == 1:
                vals = np.array(initApprox[np.where(freeVec==0)])
                allvals = np.vstack([allvals,vals])
            else:
                pass
            
            
            # Step 0: calculate the elements of the rotation matrix #
            m11 = math.cos(phi)*math.cos(kappa)
            m12 = (math.sin(omega)*math.sin(phi)*math.cos(kappa)) + (math.cos(omega)*math.sin(kappa))
            m13 = (-math.cos(omega)*math.sin(phi)*math.cos(kappa)) + (math.sin(omega)*math.sin(kappa))
            m21 = -math.cos(phi)*math.sin(kappa)
            m22 = (-math.sin(omega)*math.sin(phi)*math.sin(kappa)) + (math.cos(omega)*math.cos(kappa))
            m23 = (math.cos(omega)*math.sin(phi)*math.sin(kappa)) + (math.sin(omega)*math.cos(kappa))
            m31 = math.sin(phi)
            m32 = -math.sin(omega)*math.cos(phi)
            m33 = math.cos(omega)*math.cos(phi)
            
            
            # Step 1: Form the B (Jacobian) and e (observation) matricies 
            B = np.empty([0,len(unknowns)])
            epsilon = np.empty([0,1])
            for i in range(0,len(gcps_lidar)):
                XA = gcps_lidar[i,0]
                YA = gcps_lidar[i,1]
                ZA = gcps_lidar[i,2]
                xa = gcps_im[i,0]
                ya = gcps_im[i,1]
                
                # Deltas #
                deltaX = XA-XL
                deltaY = YA-YL
                deltaZ = ZA-ZL
                
                # Numerators and denominator of collinearity conditions #
                q = (m31*deltaX)+(m32*deltaY)+(m33*deltaZ)
                r = (m11*deltaX)+(m12*deltaY)+(m13*deltaZ)
                s = (m21*deltaX)+(m22*deltaY)+(m23*deltaZ)
                
                # Now all the b's of the B (Jacobian) matrix #
                b11 = (f/q**2) * ( (r*((-m33*deltaY)+(m32*deltaZ))) - (q*((-m13*deltaY)+(m12*deltaZ))) )
                b12 = (f/q**2) * ( (r*( (math.cos(phi)*deltaX) + (math.sin(omega)*math.sin(phi)*deltaY) - (math.cos(omega)*math.sin(phi)*deltaZ) )) - (q*( (-math.sin(phi)*math.cos(kappa)*deltaX) + (math.sin(omega)*math.cos(phi)*math.cos(kappa)*deltaY) - (math.cos(omega)*math.cos(phi)*math.cos(kappa)*deltaZ) ))       )
                b13 = (-f/q) * ((m21*deltaX)+(m22*deltaY)+(m23*deltaZ))
                b14 = (f/q**2) * ((r*m31) - (q*m11))
                b15 = (f/q**2) * ((r*m32) - (q*m12))
                b16 = (f/q**2) * ((r*m33) - (q*m13))
                b17 = 1
                b18 = 0
                b19 = -r/q
                b1 = np.array([b11,b12,b13,-b14,-b15,-b16,b19,b17,b18])
            
                b21 = (f/q**2) * ( (s*((-m33*deltaY)+(m32*deltaZ))) - (q*((-m23*deltaY)+(m22*deltaZ))) )
                b22 = (f/q**2) * ( (s*( (math.cos(phi)*deltaX) + (math.sin(omega)*math.sin(phi)*deltaY) - (math.cos(omega)*math.sin(phi)*deltaZ) )) - (q*( (-math.sin(phi)*math.sin(kappa)*deltaX) - (math.sin(omega)*math.cos(phi)*math.sin(kappa)*deltaY) + (math.cos(omega)*math.cos(phi)*math.sin(kappa)*deltaZ) ))       )
                b23 = (f/q) * ((m11*deltaX)+(m12*deltaY)+(m13*deltaZ))
                b24 = (f/q**2) * ((s*m31) - (q*m21))
                b25 = (f/q**2) * ((s*m32) - (q*m22))
                b26 = (f/q**2) * ((s*m33) - (q*m23))
                b27 = 0
                b28 = 1
                b29 = -s/q
                b2 = np.array([b21,b22,b23,-b24,-b25,-b26,b29,b27,b28])
                
                
                B1 = np.vstack([[b1[np.where(freeVec==0)]],[b2[np.where(freeVec==0)]]])
                B = np.vstack([B,B1])
            
                # Now make epsilon #
                e1 = xa- (x0 - (f*r/q))
                e2 = ya- (y0 - (f*s/q))
                
                epsilon1 = np.vstack([[e1],[e2]])
                epsilon = np.vstack([epsilon,epsilon1])   
                

            # Step 2: Solve for corrections to each parameter using the normal equation #
            Delta = np.linalg.inv(np.transpose(B) @ B) @ (np.transpose(B) @ epsilon)
            v = (B@Delta)-epsilon
        
            # Step 3: Apply the corrections # 
            for i in range(0,len(unknowns)):
                valsVec[np.where(freeVec==0)[0][i]] =  float(valsVec[np.where(freeVec==0)[0][i]] + Delta[i])
                           
            # Step 4: Add the new values to the values matrix, and calculate the change in each parameter #    
            allvals = np.vstack([allvals,[valsVec[np.where(freeVec==0)]]])
        
            # Step 5: Calculate standard error of unit weight #
            So1 = math.sqrt((np.transpose(v) @ v)/(len(B)-len(Delta)))
            So = np.vstack([So,So1])
        
        return valsVec,So    



def calibrate_CalcReprojPos(gcps_lidar,calibVals):
    
    '''
    Calculate the reprojected positions of the GCPs on the image based on the calculated calibration values.

    Inputs:
        gcps_lidar: (array) The array of lidar GCPs
        calibVals: (array) The calibration vector returned by calibrate_PerformCalibration function

    Outputs:
        u: (array) The x image coordinates of the reprojected positions
        v: (array) The y image coordinates of the reprojected positions
    
    '''
    
    
    import math
    import numpy as np
    
    # Get the final parameters and the calculated control point residuals #  
    omega = calibVals[0]
    phi = calibVals[1]
    kappa = calibVals[2]
    XL = calibVals[3]
    YL = calibVals[4]
    ZL = calibVals[5]
    f = calibVals[6]
    x0 = calibVals[7]
    y0 = calibVals[8]
    
    # Calculate the projected position of each GCP based on final vals #
    m11 = math.cos(phi)*math.cos(kappa)
    m12 = (math.sin(omega)*math.sin(phi)*math.cos(kappa)) + (math.cos(omega)*math.sin(kappa))
    m13 = (-math.cos(omega)*math.sin(phi)*math.cos(kappa)) + (math.sin(omega)*math.sin(kappa))
    m21 = -math.cos(phi)*math.sin(kappa)
    m22 = (-math.sin(omega)*math.sin(phi)*math.sin(kappa)) + (math.cos(omega)*math.cos(kappa))
    m23 = (math.cos(omega)*math.sin(phi)*math.sin(kappa)) + (math.sin(omega)*math.cos(kappa))
    m31 = math.sin(phi)
    m32 = -math.sin(omega)*math.cos(phi)
    m33 = math.cos(omega)*math.cos(phi)
    
    u = np.empty([0,1])
    v = np.empty([0,1])
    for i in range(0,len(gcps_lidar)):
        XA = gcps_lidar[i,0]
        YA = gcps_lidar[i,1]
        ZA = gcps_lidar[i,2]
        
        deltaX = XA-XL
        deltaY = YA-YL
        deltaZ = ZA-ZL
        
        q = (m31*deltaX)+(m32*deltaY)+(m33*deltaZ)
        r = (m11*deltaX)+(m12*deltaY)+(m13*deltaZ)
        s = (m21*deltaX)+(m22*deltaY)+(m23*deltaZ)
            
        u1 = x0-(f*(r/q))
        v1 = y0-(f*(s/q))
        
        u1 = x0 - (f*(((m11*(XA-XL)) + (m12*(YA-YL)) + (m13*(ZA-ZL))) / ((m31*(XA-XL)) + (m32*(YA-YL)) + (m33*(ZA-ZL)))))
        v1 = y0 - (f*(((m21*(XA-XL)) + (m22*(YA-YL)) + (m23*(ZA-ZL))) / ((m31*(XA-XL)) + (m32*(YA-YL)) + (m33*(ZA-ZL)))))
        
        u = np.vstack([u,u1])
        v = np.vstack([v,v1])
        
    return u,v
#=============================================================================#



#=============================================================================#
# Perform Rectification #
#=============================================================================#
def rectify_RectifyImage(calibVals,img,xmin,xmax,dx,ymin,ymax,dy,z):

    '''
    Function to rectify an image using the resolved calibration parameters. User inputs a grid in real world space
    onto which the image is rectified.

    Inputs:
        calibVals: (array) The calibration vector returned by calibrate_PerformCalibration function
        img: (array) The image to be rectified
        xmin: (float) minimum x-coordinate of real-world grid
        xmax: (float) maximum x-coordinate of real-world grid
        dx: (float) spacing in x-direction of the grid
        ymin: (float) minimum y-coordinate of real-world grid
        ymax: (float) maximum y-coordinate of real-world grid
        dy: (float) spacing in y-direction of the grid
        z: (float) elevation onto which the image is projected #

    Outputs:
        im_rectif: (array) The rectified image
        extents: (array) The geographic extents of the rectified image, for plotting purposes

    '''
    
    import math
    import numpy as np
    from scipy.interpolate import interp2d,griddata
    
    # Define the calib params #
    omega = calibVals[0]
    phi = calibVals[1]
    kappa = calibVals[2]
    XL = calibVals[3]
    YL = calibVals[4]
    ZL = calibVals[5]
    f = calibVals[6]
    x0 = calibVals[7]
    y0 = calibVals[8]
    
    # Set up the rotation matrix #
    m11 = math.cos(phi)*math.cos(kappa)
    m12 = (math.sin(omega)*math.sin(phi)*math.cos(kappa)) + (math.cos(omega)*math.sin(kappa))
    m13 = (-math.cos(omega)*math.sin(phi)*math.cos(kappa)) + (math.sin(omega)*math.sin(kappa))
    m21 = -math.cos(phi)*math.sin(kappa)
    m22 = (-math.sin(omega)*math.sin(phi)*math.sin(kappa)) + (math.cos(omega)*math.cos(kappa))
    m23 = (math.cos(omega)*math.sin(phi)*math.sin(kappa)) + (math.sin(omega)*math.cos(kappa))
    m31 = math.sin(phi)
    m32 = -math.sin(omega)*math.cos(phi)
    m33 = math.cos(omega)*math.cos(phi)
    
    # Set up object-space grid #
    xg = np.arange(xmin,xmax,dx)
    yg = np.arange(ymin,ymax,dy)
    xgrd,ygrd = np.meshgrid(xg,yg)
    zgrd = np.zeros([len(xgrd[:,1]),len(xgrd[1,:])])+z
    extents = np.array([(-.5*dx)+min(xg),max(xg)+(.5*dx),min(yg)-(.5*dy),max(yg)+(.5*dy)])

    # Get image coordinates of each desired world coordinate based on calib vals #
    x = x0 - (f*(((m11*(xgrd-XL)) + (m12*(ygrd-YL)) + (m13*(zgrd-ZL))) / ((m31*(xgrd-XL)) + (m32*(ygrd-YL)) + (m33*(zgrd-ZL)))))
    y = y0 - (f*(((m21*(xgrd-XL)) + (m22*(ygrd-YL)) + (m23*(zgrd-ZL))) / ((m31*(xgrd-XL)) + (m32*(ygrd-YL)) + (m33*(zgrd-ZL)))))

    # Create grid for the photo coordinates #
    u = np.arange(len(img[0,:,1]))
    v = np.arange(len(img[:,0,1]))
    ug,vg = np.meshgrid(u,v)

    # Interpolate xy (image coordinates) of world points to photo coordinates to get color #
    uInterp = np.reshape(ug,[np.size(ug)])
    vInterp = np.reshape(vg,[np.size(vg)])
    rInterp = np.reshape(img[:,:,0],[np.size(img[:,:,0])])
    gInterp = np.reshape(img[:,:,1],[np.size(img[:,:,1])])
    bInterp = np.reshape(img[:,:,2],[np.size(img[:,:,2])])
    xInterp = np.reshape(x,[np.size(x)])
    yInterp = np.reshape(y,[np.size(y)])

    col_r = griddata((uInterp,vInterp),rInterp,(xInterp,yInterp))
    col_g = griddata((uInterp,vInterp),gInterp,(xInterp,yInterp))
    col_b = griddata((uInterp,vInterp),bInterp,(xInterp,yInterp))
    
    col_r = np.reshape(col_r,[len(x[:,0]),len(x[0,:])])
    col_g = np.reshape(col_g,[len(x[:,0]),len(x[0,:])])
    col_b = np.reshape(col_b,[len(x[:,0]),len(x[0,:])])

    # Create the rectified image #
    im_rectif = np.stack([col_r,col_g,col_b],axis=2)
    im_rectif = np.flipud(im_rectif)
    
    return im_rectif,extents




'''
#    This program is free software: you can redistribute it and/or  
#    modify it under the terms of the GNU General Public License as 
#    published by the Free Software Foundation, version 3 of the 
#    License.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see
#                                <http://www.gnu.org/licenses/>.
'''


