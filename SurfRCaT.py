# -*- coding: utf-8 -*-
"""
This code contains the main functions utilizied by the Surfcamera Remote
Calibration Tool. These functions are called by the front-end user interface.

Created by Matt Conlin, University of Florida
12/2019

"""

#============================================================================#
# Get WebCAT video #
#============================================================================#
def getImagery_GetVideo(camToInput,year=2018,month=11,day=3,hour=1000):
    
    """
    Function to download a video clip from a specified WebCAT camera to local directory. The desired year, month, day, and time can be given, 
    however for those not given the function will use default values. If you don't like the video from the default date, an examination of WebCAT
    clips on the website can help determine the desired date/time to use. 
    
    Inputs:
        camToInput: (string) name of WebCAT camera you want imagery for
        year: (int) year of date you want video for
        month: (int) month of date you want video for
        day: (int) day of date you want video for
        hour: (int) hour of date you want video for
        
    Outputs:
        vidFile: path to downloaded video file 
    
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
       
    # Get the video # 
    url = 'http://webcat-video.axds.co/{}/raw/{}/{}_{}/{}_{}_{}/{}.{}-{}-{}_{}.mp4'.format(camToInput,year,year,month,year,month,day,camToInput,year,month,day,hour)   
    
    # Read and load the video file from that URL using requests library
    filename = url.split('/')[-1] # Get the filename as everything after the last backslash #
    r = requests.get(url,stream = True) # Create the Response Object, which contains all of the information about the file and file location %
    with open(filename,'wb') as f: # This loop does the downloading 
        for chunk in r.iter_content(chunk_size = 1024*1024):
            if chunk:
                f.write(chunk)
    
    ## The specified video is now saved to the directory ##
    
    # Get the video file name #
    vidFile = camToInput+'.'+str(year)+'-'+month+'-'+day+'_'+str(hour)+'.mp4'
       
    return vidFile


#=============================================================================#
# Check if the camera is a PTZ camera #
#=============================================================================#
def getImagery_CheckPTZ(vidPth,numErosionIter):
    
    """
    Function to check whether or not the desired camera is a pan-tilt-zoom (PTZ) camera. If it is,
    it will cycle through multiple view-points. This function extracts the longest continuous line
    from a series of video snaps and compares the angle of the line, utilizing the assumption that
    unique view-points will contain uniquly angled lines. Canny edge detection followed by a Hough
    Transform are used to find the longest line in each image. Function returns a data frame containing 
    indicies of snaps at each view. Companion function SeperateViewsAndGetFrames seperates the frames.
    The method definitely isn't perfect, but it typically does a good enough job to distinguish
    between unique views if the horizon is visible.
    
    Inputs:
        vidPth: (string) path to the video file that was obtained and saved by getImagery_GetVideo function
        numErosionIter: (int) prior to Canny edge detection, the input image is "eroded" (blurred) to reduce
                        the influence of smaller-scale edges. This number determines how many times this erosion is
                        performed. 2 typically gives good results.
    
    Outputs:
        viewDF: Data frame containing indicies of snaps at each view-point
        frameVec: 1d array (vector) containing all the frame numbers.
        
    """
    
    import numpy as np
    import math
    import cv2 
    import pandas as pd

    # Get the video capture #
    vid = cv2.VideoCapture(vidPth)
    
    # Find the number of frames in the video #
    vidLen = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calc horizon angle of each frame #
    psis = np.array([])
    frameNum = np.array([])
    for count in range(0,vidLen-500,int(vidLen/1000)):
        vid.set(1,count) #Set the property that we will pull the frame numbered by count #  
        test,image = vid.read()
        
        # Erode the image (morphological erosion) #
        kernel = np.ones((5,5),np.uint8)
        imeroded = cv2.erode(image,kernel,iterations = numErosionIter)

        # Find edges using Canny Edge Detector #
        edges = cv2.Canny(imeroded,50,100)
    
        # Find longest straight edge with Hough Transform #
        lines = cv2.HoughLines(edges,1,np.pi/180,200)
        if lines is not None:
            for rho,theta in lines[0]: # The first element is the longest edge #
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
            
            # Calc horizon angle (psi) #
            psi = math.atan2(y1-y2,x2-x1)
        
            # Save horizon angle and the number of the frame #
            psis = np.append(psis,psi)
            frameNum = np.append(frameNum,count)
        
    
    # Round angles to remove small fluctuations, and take abs #
    psis = np.round(abs(psis),3)

    # Find the frames where calculated angle changes #
    dif = np.diff(psis)
    changes = np.array(np.where(dif!=0))

    # Calculate the length of each angle segment between when the angle changes.
    if np.size(changes)>0:
        segLens = np.array([])
        vals = np.array([])
        for i in range(0,len(changes[0,:])+1):
            if i == len(changes[0,:]):
                segLen = len(psis)-(changes[0,i-1]+1)
                val = psis[len(psis)-1]    
            elif changes[0,i] == changes[0,0]:
                segLen = changes[0,i]
                val = psis[0]
            else:
                segLen = changes[0,i]-changes[0,i-1]
                val = psis[changes[0,i-1]+1]
                
            segLens = np.append(segLens,segLen)
            vals = np.append(vals,val)
            
        # Keep only chunks that are continuous over a threshold #    
        IDs_good = np.array(np.where(segLens>=10)) # Using 10 seems to work, but this could be changed #
        valsKeep = vals[IDs_good]
    
        # Find the unique views #
        viewAngles = np.unique(valsKeep)

        # Find and extract the frames contained within each view #
        frameVec = np.array(range(0,vidLen-500,int(vidLen/1000)))
        angles = []
        frames = []
        for i in viewAngles:
            iFrames = frameVec[np.array(np.where(psis == i))]
            angles.append(i)
            frames.append([iFrames])
        
        viewDict = {'View Angles':angles,'Frames':frames}
        viewDF = pd.DataFrame(viewDict)
        
        return viewDF,frameVec
    
    else:
   
        # Find the unique views #
        viewAngles = np.unique(psis)
    
        # Find and extract the frames contained within each view #
        frameVec = np.array(range(0,vidLen-500,int(vidLen/1000)))
        angles = []
        frames = []
        for i in viewAngles:
            iFrames = np.array(np.where(psis == i))
            angles.append(i)
            frames.append([iFrames])
            
        viewDict = {'View Angles':angles,'Frames':frames}
        viewDF = pd.DataFrame(viewDict)
        
        return viewDF,frameVec


def getImagery_SeperateViewsAndGetFrames(vidPth,viewDF):
    
    '''
    Function to put the frames from each view into a dataframe 
    
    Inputs:
        vidPth: (string)  path to the video file that was obtained and saved by getImagery_GetVideo function
        viewDF: The dataframe of views returned by the checkPTZ function 
    
    Outputs:
        frameDF: dataframe of snaps in each view
    
    '''
    
    import pandas as pd
    import cv2
    
    numViews = len(viewDF)
    vid = cv2.VideoCapture(vidPth)
    
    frameDF = pd.DataFrame(columns=['View','Image'])
    for i in range(0,numViews):
        frameTake = viewDF['Frames'][i][0][0][1]
        
        vid.set(1,frameTake) # Set the property that we will pull the desired frame #  
        test,image = vid.read()
        
        frameDF = frameDF.append({'View':i,'Image':image},ignore_index=True)
        
    return frameDF




#=============================================================================#
# Search for and identify lidar datasets that cover camera location #
#=============================================================================#
##def getLidar_GetIDs():
##    
##    '''
##    First function in the Lidar download process: get the IDs of all datasets on the NOAA ftp server.
##    
##    Inputs:
##        None
##    
##    Outputs:
##        IDs: A list containing all of the dataset IDs for use in later functions 
##        
##    '''
##    
##    import ftplib
##    import re
##    
##    # Pull the numeric IDs from all datasets that exist #
##    ftp = ftplib.FTP('ftp.coast.noaa.gov',timeout=1000000)
##    ftp.login('anonymous','anonymous')
##    ftp.cwd('/pub/DigitalCoast/lidar2_z/geoid12b/data/')
##    IDs = ftp.nlst()
##    # Get rid of spurious IDs which have letters
##    IDsGood = list()
##    for tryThisString in IDs:
##        testResult = re.search('[a-zA-Z]',tryThisString) # Use regular expressions to see if any letters exist in the string #
##        if testResult:
##            pass
##        else:
##            IDsGood.append(tryThisString)
##    IDs = IDsGood
##    return IDs


def getLidar_FindPossibleIDs(cameraLoc_lat,cameraLoc_lon):

    '''
    First function in the lidar download process. Finds the dataset IDs of all lidar
    datasets that could be close to the camera based on its location (and derived state
    and coast). Function searches through a NOAA-provided table fo datasets and extracts
    only the IDs of datasets that may be close to the camera. 
    
    Inputs:
        cameraLoc_lat: Latitude location of camera
        cameraLoc_lon: Longitude location of camera
    
    Outputs:
        IDs: A list containing the dataset IDs of possibly proximal datasets.
        
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

        # Get the data tabel from NOAAs website #
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



        
def getLidar_TryID(ftp,ID,cameraLoc_lat,cameraLoc_lon):
    
    '''
    Function to go through each identified lidar dataset and determine if it covers the location of the camera. If
    it does, the lidar dataset is saved. Function takes advantage of a csv file given to each dataset on the NOAA
    repositories which gives the min and max extents of the dataset.
    
    Inputs:
        ID: A lidar dataset ID
        cameraLoc_lat: Latitude location of camera
        cameraLoc_lon: Longitude location of camera
        
    Outputs:
        check: A yes or no as to if this dataset covers the camera location 
    '''
    
    import ftplib
    from io import StringIO
    from pandas import read_csv

    # Get into the correct NOAA FTP site- there are 5 of them. I'm sure this isn't the clenest way to do this #
    # "If at first you don't succeed..."
    try:
        ftp.cwd('/pub/DigitalCoast/lidar1_z/geoid12b/data/'+str(ID))
    except:
        try:
            ftp.cwd('/pub/DigitalCoast/lidar2_z/geoid12b/data/'+str(ID))
        except:
            try:
                ftp.cwd('/pub/DigitalCoast/lidar3_z/geoid12b/data/'+str(ID))
            except:
                try:
                    ftp.cwd('/pub/DigitalCoast/lidar1_z/geoid12a/data/'+str(ID))
                except:
                    ftp.cwd('/pub/DigitalCoast/lidar3_z/geoid18/data/'+str(ID))
                    
        
    # Find the minmax csv file which shows the min and max extents of each tile within the current dataset #
    files = ftp.nlst()
    fileWant = str([s for s in files if "minmax" in s])
    if fileWant:
        if len(fileWant)>2:
            # Get the file name and save it. We need to get rid of the ' or " in the name. Sometimes this means we need to get rid of the first 2 characters, sometimes the first 3 #
            if len(fileWant.split()) == 2:
                fileWant = '['+fileWant.split()[1]
            fileWant = fileWant[2:len(fileWant)-2]

##            r = StringIO()
##            ftp.retrlines('RETR '+fileWant,r.write)
##            dat = r.getvalue()


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
            
            

##            tiles = list()
##            with open('minmax.csv') as infile:
##                next(infile)
##                for line in infile:
##                    if float(line.split()[1][0:7]) <= cameraLoc_lon <= float(line.split()[2][0:7]) and float(line.split()[3][0:7])<= cameraLoc_lat <= float(line.split()[4][0:7]):
##                        tiles.append(line)
    
            return check
        

def getLidar_GetDatasetNames(appropID):
    
    '''
    Function to link the ID of each lidar dataset found to cover the camera with the name and other metadata of the dataset.
    
    Inputs:
        appropID: The ID of a dataset found to cover the camera by the getLidar_TryID function
        
    Outputs:
        matchingTable: A dictionary giving each ID linked to metadata (name, date, etc.)
        
    '''
    
    import pandas as pd
    import requests
    
    # Get the data tabel from NOAAs website #
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
def getLidar_GetShapefile(IDToDownload):
    
    '''
    Function to get the shapefile of a tile of the chosen lidar dataset. We will use the shapefile
    to determine if the tile is near the camera, to avoid downloading a bunch of data not near the camera.
    
    Inputs:
        IDToDownload: ID of chosen lidar dataset, returned by the checkbox from user input.
        
    Outputs:
        sf: The shapefile of the tiles
        
    '''
    
    import ftplib
    import shapefile


    ftp = ftplib.FTP('ftp.coast.noaa.gov',timeout=1000000)
    ftp.login('anonymous','anonymous')
    ftp.cwd('/pub/DigitalCoast/lidar2_z/geoid12b/data/'+str(IDToDownload))
    files = ftp.nlst()


    # Now that we have the dataset, we need to search the dataset for tiles which are near the camera. Otherwise,
    # we will be loading a whole lot of useless data into memory, which takes forever. #

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



def getLidar_SearchTiles(sf,shapeNum,cameraLoc_lat,cameraLoc_lon):

    '''
    Function to determine the distance of each tile to the camera
    
    Inputs: 
        sf: The shapefile of the tiles from the getLidar_GetShapefile function
        shapeNum: The tile number
        cameraLoc_lat: Latitude of camera
        cameraLoc_lon: Longitude of camera
    
    Outputs:
        rec['name']: The names of the tiles that are close to the camera
        
    '''
    
    import utm
    import math
    import numpy
    
    # Establish the location of the camera in UTM coordinates #
    cameraLoc_UTMx = utm.from_latlon(cameraLoc_lat,cameraLoc_lon)[0]
    cameraLoc_UTMy = utm.from_latlon(cameraLoc_lat,cameraLoc_lon)[1]
    
    # See if the tile is near the camera #
    bx = sf.shape(shapeNum).bbox # Get the bounding box #
    # Get the bounding box verticies in utm. bl = bottom-left, etc. #
    bx_bl = utm.from_latlon(bx[1],bx[0]) 
    bx_br = utm.from_latlon(bx[1],bx[2]) 
    bx_tr = utm.from_latlon(bx[3],bx[2]) 
    bx_tl = utm.from_latlon(bx[3],bx[0]) 
    # Min distance between camera loc and horizontal lines connecting tile verticies #
    line_minXbb = numpy.array([numpy.linspace(bx_bl[0],bx_br[0],num=1000),numpy.linspace(bx_bl[1],bx_br[1],num=1000)])
    line_maxXbb = numpy.array([numpy.linspace(bx_tl[0],bx_tr[0],num=1000),numpy.linspace(bx_tl[1],bx_tr[1],num=1000)])
    
    # Distance from camera to midpoint of tile #
    meanX = numpy.mean(numpy.array([line_minXbb[0,:],line_maxXbb[0,:]]))
    meanY = numpy.mean(numpy.array([line_minXbb[1,:],line_maxXbb[1,:]]))
    dist = math.sqrt((meanX-cameraLoc_UTMx)**2 + (meanY-cameraLoc_UTMy)**2)
    
    # Distance from camera to edges of tile #
    dist1 = list()
    dist2 = list()
    for ixMin,iyMin,ixMax,iyMax in zip(line_minXbb[0,:],line_minXbb[1,:],line_maxXbb[0,:],line_maxXbb[1,:]):
        dist1.append(math.sqrt((ixMin-cameraLoc_UTMx)**2 + (iyMin-cameraLoc_UTMy)**2))
        dist2.append(math.sqrt((ixMax-cameraLoc_UTMx)**2 + (iyMax-cameraLoc_UTMy)**2))
    
    # If either distance is <350 m, keep the tile. This ensures close tiles are kept and the tile containing the camera is kept. #
    try:
        rec = sf.record(shapeNum)
        if min(dist1)<600 or min(dist2)<600:
            return rec['Name']
    except:
        pass



def getLidar_Download(thisFile,IDToDownload,cameraLoc_lat,cameraLoc_lon):
    
    '''
    Function to download the close tiles of the identified lidar dataset.
    
    Inputs:
        thisFile: the file to download
        IDToDownload: The ID of the dataset being downloaded
        cameraLoc_lat: Latitude of camera
        cameraLoc_lon: Longitude of camera
        
    Outputs:
        lidarXYZsmall: XYZ point cloud, as an nx3 array, of the lidar data
        
    '''
            
    import ftplib
    import numpy
    import math
    import json    
    import pdal
          
    ftp = ftplib.FTP('ftp.coast.noaa.gov',timeout=1000000)
    ftp.login('anonymous','anonymous')
    ftp.cwd('/pub/DigitalCoast/lidar2_z/geoid12b/data/'+str(IDToDownload))
           
    # Save the laz file locally - would prefer not to do this, but can't seem to get the pipeline to download directly from the ftp??? #
    gfile = open('lazfile.laz','wb') # Create the local file #
    ftp.retrbinary('RETR '+thisFile,gfile.write) # Copy the contents of the file on FTP into the local file #
    gfile.close() # Close the remote file #
        
    # Construct the json PDAL pipeline to read the file and take only points within +-.5 degree x and y of the camera. Read the data in as an array #
    fullFileName = 'lazfile.laz'
    pipeline=(json.dumps([{'type':'readers.las','filename':fullFileName},{'type':'filters.range','limits':'X['+str(cameraLoc_lon-.5)+':'+str(cameraLoc_lon+.5)+'],Y['+str(cameraLoc_lat-.5)+':'+str(cameraLoc_lat+.5)+']'}],sort_keys=False,indent=4))
        
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

    # Only take points within 500 m of the camera #
    R = 6373000 # ~radius of Earth in m #
    dist = list()
    for px,py in zip(lidarX,lidarY):
        dlon = math.radians(abs(px)) - math.radians(abs(cameraLoc_lon))
        dlat = math.radians(abs(py)) - math.radians(abs(cameraLoc_lat))
        a = math.sin(dlat/2)**2 + math.cos(math.radians(abs(py))) * math.cos(math.radians(abs(cameraLoc_lat))) * math.sin(dlon/2)**2
        c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
        dist.append(R*c)
   
    lidarXsmall = list()
    lidarYsmall = list()
    lidarZsmall = list()    
    for xi,yi,zi,di in zip(lidarX,lidarY,lidarZ,dist):
        if di<300:
            lidarXsmall.append(xi)
            lidarYsmall.append(yi)
            lidarZsmall.append(zi)
    lidarXYZsmall = numpy.vstack((lidarXsmall,lidarYsmall,lidarZsmall))
    lidarXYZsmall = numpy.transpose(lidarXYZsmall)
    
    return lidarXYZsmall



def getLidar_CreatePC(lidarDat,cameraLoc_lat,cameraLoc_lon): 
    
    '''
    Fucntion to convert lidat point cloud (in lat/lon coords) to one in UTM coords
    relative to the location of the camera (camera location set as origin)
    
    Inputs:
        lidarDat: The XYZ lidar point cloud returned by getLidar_Download function
        cameraLoc_lat: Latitude of camera
        cameraLoc_lon: Longitude of camera
    
    Outputs:
        pc: The new point cloud, for use in future functions
        
    '''

    import utm
    import numpy 
    import pandas as pd
    
    pc = pd.DataFrame({'x':lidarDat[:,0],'y':lidarDat[:,1],'z':lidarDat[:,2]})

    # Convert eveything to UTM and translate to camera at (0,0) #
    utmCoordsX = list()
    utmCoordsY = list()
    for ix,iy in zip(pc['x'],pc['y']):
        utmCoords1 = utm.from_latlon(iy,ix)
        utmCoordsX.append( utmCoords1[0] )
        utmCoordsY.append( utmCoords1[1] )
    utmCoords = numpy.array([utmCoordsX,utmCoordsY])
        
    utmCam = utm.from_latlon(cameraLoc_lat,cameraLoc_lon)
        
    # Translate to camera position #
    utmCoords[0,:] = utmCoords[0,:]-utmCam[0]
    utmCoords[1,:] = utmCoords[1,:]-utmCam[1]
   
    # Put these new coordinates into the point cloud %
    pc['x'] = numpy.transpose(utmCoords[0,:])
    pc['y'] = numpy.transpose(utmCoords[1,:])
    
    return pc



#=============================================================================#
# Perform Calibration #
#=============================================================================#
def calibrate_getInitialApprox_IOPs(img):
    '''
    Get initial approximatation for camera IOPs (focal length (f) and principal points (x0,y0)) using the geometry of the image.
    - Estimate focal length by assuming a horizontal field of view of 60 degrees (typical of webcams), and using simple geometry with this and the width of the image.
    - Estimate principal points as the center of the image.
    '''
    
    import math
    w = len(img[1,:,:])
    a = math.radians(60)
    f = (w/2)*(1/math.tan(a/2))
    
    x0 = len(img[1,:,1])/2
    y0 = len(img[:,1,1])/2
    
    return f,x0,y0



def calibrate_getInitialApprox_ats2opk(a,t,s):
    '''
    Get initial approximations for the three needed camera look-angles by using easily estimated azimuth, tilt, and swing. 
    Form the ats rotation matrix and decompose it to omega,phi,kappa angles.
    '''
    import math
    
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


    
def calibrate_performCalibration(initApprox,freeVec,gcps_im,gcps_lidar):
        '''
        Perform the augmented space resection using the initial approximations for all parameters
        input to this function.
        
        Inputs:
            initApprox: a vector containing the initial approximations for all nine parameters, in the order:
                        omega,phi,kappa,XL,YL,ZL,f,x0,y0
            freeVec: A vector that defines the terms that are free to change and those that fixed during the adjustment. Each element corresponds
                     to the same positioned element in initiApprox. A value of 1 indiciates the parameter is fixed, a value of 0 indicates it is free to change. 
            gcps_im: The array of image coordinates of ground control points
            gcps_lidar: The array of world-coordinates of ground control points
        
        Outputs:
            valsVec: a vector containing the final values for each parameter after adjustment, in the same order as in initApprox
            So: The standard error of unit weight for each iteration of the adjustment. 
        
        '''
        import math
        import numpy as np
        
        unknowns = np.where(freeVec==0)[0] # Indicies of unknown values #
        
        allvals = np.empty([0,len(unknowns)]) # Matrix to store the values (rows) for each parameter (columns) as the least squares solution iterates #
        Delta = np.ones(len(unknowns))
        So = np.empty([0,1]) 
        valsVec = initApprox
        
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
            
            
            # Step 0: calculate the elements of the M matrix #
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
                

            # Step 2: Solve for corrections to each parameter using the weighted normal equation #
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
    Calculate the reprojected positions of the GCPs based on the calculated calibration values.
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






