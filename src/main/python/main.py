# -*- coding: utf-8 -*-
"""
Create and run the user interface of the Surfcamera Remote
Calibration Tool. Most of the science behind the tool is contained within the
functions in the SurfRCaT.py file. The UI is created with PyQt.

The UI is run as a series of windows, each of which is its own class. All calls to
SurfRCaT.py are completed with stand alone threads. Each thread is also its own class,
and all are defined after the window classes. 

Created by Matthew P. Conlin, University of Florida

"""

__copyright__ = 'Copyright (c) 2020, Matthew P. Conlin'
__license__ = 'GPL-3.0'
__version__ = '1.0'


# Import packages #
import pptk
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont,QMovie
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QAbstractTableModel,QProcess
import sys 
import pickle
import SurfRCaT
import os
import cv2
import matplotlib.image as mpimg 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import time
import ftplib
import csv


# Establish and format the local installation directory. All outputs will be saved to this directory #
pth = os.path.dirname(os.path.realpath(__file__))
pth = os.path.join(str(pth),'')


class WelcomeWindow(QWidget):
    ''' 
    Welcome window with text about the tool and a Start button to launch the tool.
    '''
    
    def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()    
            
            
        # Left menu box setup #
        bf = QFont()
        bf.setBold(True)
        leftBar1 = QLabel('• Welcome!')
        leftBar2 = QLabel('• Get imagery')
        leftBar3 = QLabel('• Get lidar data')
        leftBar4 = QLabel('• Pick GCPs')
        leftBar5 = QLabel('• Calibrate')
        leftBar6 = QLabel('• Rectify')
        leftBar1.setFont(bf)

        leftGroupBox = QGroupBox('Contents:')
        vBox = QVBoxLayout()
        vBox.addWidget(leftBar1)
        vBox.addWidget(leftBar2)
        vBox.addWidget(leftBar3)
        vBox.addWidget(leftBar4)
        vBox.addWidget(leftBar5)
        vBox.addWidget(leftBar6)
        vBox.addStretch(1)
        leftGroupBox.setLayout(vBox)
        ########################    
            
        # Right contents box setup #      
        txt = QLabel('Welcome to the Surfcamera Remote Calibration Tool (SurfRCaT)!')
        txt2 = QLabel('SurfRCaT has been developed in partnership with the Southeastern Coastal Ocean Observing Regional Association (SECOORA; https://secoora.org/), '
                      +'the United States Geological Survey (USGS), and the National Oceanic and Atmospheric Administration (NOAA). This tool allows you to calibrate any coastal camera in the U.S. of '
                      +'generally known location with accessible video footage. If you have an issue, please post it on the GitHub issues page (https://github.com/conlin-matt/SurfRCaT/issues).')      
        txt2.setWordWrap(True)
        txt3 = QLabel('Press Continue to start calibrating a camera.')
        txt3.setWordWrap(True)
        txt4 = QLabel('Or, if you already have calibration parameters, and would like to jump directly to rectification, select Rectify.')
        txt4.setWordWrap(True)
        contBut = QPushButton('Continue >')
        rectifBut = QPushButton('Rectify >')
        
        rightGroupBox = QGroupBox()
        
        hBox1 = QHBoxLayout()
        hBox1.addWidget(txt3)
        hBox1.addWidget(contBut)
        hBox2 = QHBoxLayout()
        hBox2.addWidget(txt4)
        hBox2.addWidget(rectifBut)        
        vBox = QVBoxLayout()
        vBox.addWidget(txt)
        vBox.addWidget(txt2)
        vBox.addLayout(hBox1)
        vBox.addLayout(hBox2)
        rightGroupBox.setLayout(vBox)
        ############################
        
        # Connect widgets with signals #
        rectifBut.clicked.connect(self.jumpToRectify)
        contBut.clicked.connect(self.StartTool)
        ################################
        
        # Full widget layout setup #
        fullLayout = QHBoxLayout()
        fullLayout.addWidget(leftGroupBox)
        fullLayout.addWidget(rightGroupBox)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        self.show()
        ###############################
         
    def StartTool(self):
       '''
       Moves to the first window of the tool when Start is selected
       '''
       self.close()
       self.tool = ChooseCameraWindow()
       self.tool.show()
       
    def jumpToRectify(self):
        self.close()
        self.w = rectify_InputsWindow()
        self.w.show()



class ChooseCameraWindow(QWidget):
    '''
    Window allowing the user to choose whether they want to calibrate a WebCAT surfcam or some other surfcam. Next steps will depend on this choice.
    '''
    def __init__(self):
        super().__init__()
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()  
        
        # Left menu box setup #
        bf = QFont()
        bf.setBold(True)
        leftBar1 = QLabel('• Welcome!')
        leftBar2 = QLabel('• Get imagery')
        leftBar3 = QLabel('• Get lidar data')
        leftBar4 = QLabel('• Pick GCPs')
        leftBar5 = QLabel('• Calibrate')
        leftBar6 = QLabel('• Rectify')
        leftBar2.setFont(bf)

        leftGroupBox = QGroupBox('Contents:')
        vBox = QVBoxLayout()
        vBox.addWidget(leftBar1)
        vBox.addWidget(leftBar2)
        vBox.addWidget(leftBar3)
        vBox.addWidget(leftBar4)
        vBox.addWidget(leftBar5)
        vBox.addWidget(leftBar6)
        vBox.addStretch(1)
        leftGroupBox.setLayout(vBox)
        ########################    
        
        # Right contents box setup #
        t = QLabel('Choose camera type:')
        WebCatOpt = QRadioButton('Select WebCAT camera from list')
        OtherOpt = QRadioButton('Input location of other camera')    
        
        rightGroupBox = QGroupBox()
        vBox2 = QVBoxLayout()
        vBox2.addWidget(t)
        vBox2.addWidget(WebCatOpt)
        vBox2.addWidget(OtherOpt)
        vBox2.setAlignment(Qt.AlignCenter)
        rightGroupBox.setLayout(vBox2)
        ############################
         
        # Connect widgets with signals #
        WebCatOpt.clicked.connect(self.WebCAT_select)
        OtherOpt.clicked.connect(self.Other_select)
        ################################
        
        # Full widget layout setup #
        fullLayout = QHBoxLayout()
        fullLayout.addWidget(leftGroupBox)
        fullLayout.addWidget(rightGroupBox)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        self.show()
        ###############################
            
    def WebCAT_select(self):
        '''
        If WebCAT camera selected, this funciton will open new window (WebCATLocationWindow) to choose the WebCAT camera
        '''
        self.close()
        self.ww = getWebCATImagery_WebCATLocationWindow()  
        self.ww.show()
        
    def Other_select(self):
        '''
        If other-type selected, this function will open a new window (OtherCameraLocationInputWindow) to allow input of camera details
        '''
        self.close()
        self.www = getOtherImagery_OtherCameraLocationInputWindow()
        self.www.show()       
##============================================================================##       


##============================================================================## 
# Get Imagery Module: Get the image to be used for the calibration #
##============================================================================##
class getWebCATImagery_WebCATLocationWindow(QWidget):
    '''
    Window allowing the user to choose desired WebCAT camera from dropdown menu.
    '''
   
    def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()             
        self.initUI()
        
    def initUI(self):
       
       # Left menu box setup #
       bf = QFont()
       bf.setBold(True)
       leftBar1 = QLabel('• Welcome!')
       leftBar2 = QLabel('• Get imagery')
       leftBar3 = QLabel('• Get lidar data')
       leftBar4 = QLabel('• Pick GCPs')
       leftBar5 = QLabel('• Calibrate')
       leftBar6 = QLabel('• Rectify')
       leftBar2.setFont(bf)

       leftGroupBox = QGroupBox('Contents:')
       vBox = QVBoxLayout()
       vBox.addWidget(leftBar1)
       vBox.addWidget(leftBar2)
       vBox.addWidget(leftBar3)
       vBox.addWidget(leftBar4)
       vBox.addWidget(leftBar5)
       vBox.addWidget(leftBar6)
       vBox.addStretch(1)
       leftGroupBox.setLayout(vBox)
       ########################    
       
       # Right contents box setup #
       txt = QLabel('Select WebCAT camera:')
       opt = QComboBox()
       opt.addItem('--')
       opt.addItem('Buxton Coastal Hazard')
       opt.addItem('Cherry Grove Pier (south)')
       opt.addItem('Folly Beach Pier (north)')
       opt.addItem('Folly Beach Pier (south)')
       opt.addItem('St. Augustine Pier')
       opt.addItem('Twin Piers/Bradenton')
       opt.addItem('Miami 40th Street')
       opt.setCurrentIndex(0)
       backBut = QPushButton('< Back')
       contBut = QPushButton('Continue >')
       
       self.rightGroupBox = QGroupBox()
       self.grd = QGridLayout()
       self.grd.addWidget(txt,0,0,1,2)
       self.grd.addWidget(opt,1,0,1,2)
       self.grd.addWidget(backBut,2,0,1,1)
       self.grd.addWidget(contBut,2,1,1,1)
       self.grd.setAlignment(Qt.AlignCenter)
       self.rightGroupBox.setLayout(self.grd)
       ############################
       
       # Connect widgets with signals #
       opt.activated.connect(self.getSelected)
       backBut.clicked.connect(self.GoBack)
       contBut.clicked.connect(self.DownloadVidAndExtractStills)
       ################################

       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(self.rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       self.show()
       ############################
        
       # Instantiate worker threads #
       self.worker = DownloadVidThread(None,None,None)
       ##############################

    def getSelected(self,item):
       '''
       Function gets saved location of WebCAT camera when it is selected from the combobox
       '''
          
       WebCATdict = {'Placeholder':[0,0],
                    'buxtoncoastalcam':[35.267777,-75.518448],
                    'cherrypiersouthcam':[ 33.829960, -78.633320],
                    'follypiernorthcam':[32.654731,-79.939322],
                    'follypiersouthcam':[32.654645,-79.939597],
                    'staugustinecam':[29.856559,-81.265545],
                    'twinpierscam':[27.466685,-82.699540],
                    'miami40thcam':[ 25.812227, -80.122400]}
      
       # Get location of selected camera #
       cams = ['Placeholder','buxtoncoastalcam','cherrypiersouthcam','follypiernorthcam','follypiersouthcam','staugustinecam','twinpierscam','miami40thcam']
       cameraLocation = WebCATdict[cams[item]]
       cameraName = cams[item]
       # Save the WebCAT camera location and name #
       with open(pth+'CameraLocation.pkl','wb') as f:
           pickle.dump(cameraLocation,f)
       with open(pth+'CameraName.pkl','wb') as f:
           pickle.dump(cameraName,f)
       
       if cameraName == 'follypiersouthcam': # Need 1 erosion iter for Folly Pier South, 2 for other cams # 
           self.worker2 = CheckPTZThread(1)
       else:
           self.worker2 = CheckPTZThread(2)

        
       # Add the pre-defined azimuth and elev for each WebCAT camera #
       if cameraName == 'buxtoncoastalcam':
           self.az = 5
           self.ZL = 10
       elif cameraName == 'cherrypiersouthcam':
           self.az = 200
           self.ZL = 15
       elif cameraName == 'follypiernorthcam':
           self.az = 150
           self.ZL = 15
       elif cameraName == 'follypiersouthcam':
           self.az = 150
           self.ZL = 15
       elif cameraName == 'staugustinecam':
           self.az = 80
           self.ZL = 10
       elif cameraName == 'twinpierscam':
           self.az = 80
           self.ZL = 5
       elif cameraName == 'miami40thcam':
           self.az = 60
           self.ZL = 40
       
       with open(pth+'az.pkl','wb') as f:
           pickle.dump(self.az,f)
       with open(pth+'ZL.pkl','wb') as f:
           pickle.dump(self.ZL,f) 
           
    def GoBack(self):
       '''
       Function goes back to previous window when Back button is clicked
       '''
       self.close()
       self.backToOne = ChooseCameraWindow()
          
    def DownloadVidAndExtractStills(self):
       '''
       Sets a label that video is downloading when Continue is clicked, and starts a worker thread to download the video
       '''
       lab1 = QLabel('Downloading Video...')
       self.grd.addWidget(lab1,3,0,1,1)

       self.loadlab = QLabel()
       self.loadmovie = QMovie(pth+'loading.gif')
       self.loadlab.setMovie(self.loadmovie)
       
       self.worker.start()
       self.grd.addWidget(self.loadlab,3,1,1,1)
       self.loadmovie.start()
       self.worker.finishSignal.connect(self.on_closeSignal)

    def on_closeSignal(self):
       '''
       When download video thread is done, function shows a done label and starts the PTZ check worker thread
       '''
       self.loadlab.setParent(None)
       self.loadmovie.stop()
       labDone = QLabel('Done.')
       self.grd.addWidget(labDone,3,1,1,1)
       
       lab2 = QLabel('Checking different views...')
       self.grd.addWidget(lab2,4,0,1,1)
       
       self.loadlab = QLabel()
       self.loadmovie = QMovie(pth+'loading.gif')
       self.loadlab.setMovie(self.loadmovie)
       
       self.worker2.start()
       self.grd.addWidget(self.loadlab,4,1,1,1)
       self.loadmovie.start()
       self.worker2.finishSignal.connect(self.on_closeSignal2)
       
    
    def on_closeSignal2(self):
       ''' 
       After PTZ is checked, take user to view choice window.
       '''
       self.loadlab.setParent(None)
       self.loadmovie.stop()        
       labDone = QLabel('Done.')
       self.grd.addWidget(labDone,4,1,1,1)
       
       self.close()
       self.cv = getWebCATImagery_ChooseViewWindow()
       self.cv.show()      


class getWebCATImagery_ChooseViewWindow(QWidget):
    '''
    Window allowing the user to choose which view they want to calibrate from a PTZ camera.
    '''
   
    def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()  
        self.initUI()
        
    def initUI(self):
       
       # Left menu box setup #
       bf = QFont()
       bf.setBold(True)
       leftBar1 = QLabel('• Welcome!')
       leftBar2 = QLabel('• Get imagery')
       leftBar3 = QLabel('• Get lidar data')
       leftBar4 = QLabel('• Pick GCPs')
       leftBar5 = QLabel('• Calibrate')
       leftBar6 = QLabel('• Rectify')
       leftBar2.setFont(bf)

       leftGroupBox = QGroupBox('Contents:')
       vBox = QVBoxLayout()
       vBox.addWidget(leftBar1)
       vBox.addWidget(leftBar2)
       vBox.addWidget(leftBar3)
       vBox.addWidget(leftBar4)
       vBox.addWidget(leftBar5)
       vBox.addWidget(leftBar6)
       vBox.addStretch(1)
       leftGroupBox.setLayout(vBox)
       ########################    
        
       # Right contents box setup #
       self.rightGroupBox = QGroupBox()
       f1 = open(pth+'viewDF.pkl','rb')
       f2 = open(pth+'vidFile.pkl','rb')
       f3 = open(pth+'CameraName.pkl','rb')
       self.viewDF = pickle.load(f1)
       vidFile = pickle.load(f2)
       vidPth = vidFile
       cameraName = pickle.load(f3)
       
       self.frameDF = SurfRCaT.getImagery_GetFrames(pth+vidPth,self.viewDF)
       numViews = len(self.frameDF)
       
       # Set up the text label #
       txt = QLabel('Automatically detected unique camera views are shown below. Choose the view which you would like to calibrate. If the image(s) are not clear enough to allow for feature extraction, press the Need New Images button.')
       txt.setWordWrap(True)
       txt2 = QLabel('Select view to calibrate:')
       cb = QComboBox()
       cb.addItem('--')
       
       self.grd = QGridLayout()
       self.grd.addWidget(txt,0,0,1,numViews)
       self.grd.addWidget(txt2,2,0,1,numViews)
       
       # Display image from each view #
       for i in range(0,numViews):
           im = self.frameDF['Image'][i]
           cv2.imwrite(pth+'frame.png', im)
           
           img = mpimg.imread(pth+'frame.png')
           self.canvas = FigureCanvas(Figure())
           self.ax = self.canvas.figure.subplots()
           self.ax.imshow(img)
           self.canvas.draw()
          
           self.grd.addWidget(self.canvas,1,i,1,numViews-(numViews-i)+1)
           cb.addItem('View'+str(i+1))

       self.grd.addWidget(cb,3,0,1,numViews)
       orLab1 = QLabel('Or')
       badBut2 = QPushButton('Need new images')
       self.grd.addWidget(orLab1,4,0,1,numViews)
       self.grd.addWidget(badBut2,5,0,1,numViews)
       
       self.rightGroupBox.setLayout(self.grd)
       ########################################
       
       # Connect widgets with signals #
       cb.activated.connect(self.viewSelected)
       badBut2.clicked.connect(self.chooseNewDate)
       ################################

       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(self.rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       self.show()
       ############################
       
       # Instantiate worker threads #
       if cameraName == 'follypiersouthcam': # Need 1 erosion iter for Folly Pier South, 2 for other cams # 
           self.worker = CheckPTZThread(1)
       else:
           self.worker = CheckPTZThread(2)
       ##############################
       
    def viewSelected(self,item):
       '''
       Takes user to the lidar acquisition module on Yes click
       '''
       viewSel = item-1
       im = self.frameDF['Image'][viewSel]
       cv2.imwrite(pth+'frameUse.png', im)

       # Get the saved lidar dataset IDs for the camera #
       self.worker = getLidar_WebCATThread()
       self.worker.finishSignal.connect(self.on_closeSignal)
       self.worker.start()

    def on_closeSignal(self):
        '''
        Moves to next window.
        '''

        f = open(pth+'lidarTable.pkl','rb')
        lidarTable = pickle.load(f)

        self.close()
        self.lw = getLidar_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
        self.lw.resize(900,350)
        self.lw.show()
       
        
    def chooseNewDate(self):
       '''
       Pops up window for user to input date for imagery download
       '''
       self.close()
       self.newDate = getWebCATImagery_ChooseNewDateWindow()
       self.newDate.show()


class getWebCATImagery_ChooseNewDateWindow(QWidget):
    '''
    Window allowing the user to input desired date for WebCAT imagery, if defaults were not good
    '''
    
    def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()             
        self.initUI()
        
    def initUI(self):
       
       # Left menu box setup #
       bf = QFont()
       bf.setBold(True)
       leftBar1 = QLabel('• Welcome!')
       leftBar2 = QLabel('• Get imagery')
       leftBar3 = QLabel('• Get lidar data')
       leftBar4 = QLabel('• Pick GCPs')
       leftBar5 = QLabel('• Calibrate')
       leftBar6 = QLabel('• Rectify')
       leftBar2.setFont(bf)

       leftGroupBox = QGroupBox('Contents:')
       vBox = QVBoxLayout()
       vBox.addWidget(leftBar1)
       vBox.addWidget(leftBar2)
       vBox.addWidget(leftBar3)
       vBox.addWidget(leftBar4)
       vBox.addWidget(leftBar5)
       vBox.addWidget(leftBar6)
       vBox.addStretch(1)
       leftGroupBox.setLayout(vBox)
       ########################    
       
       # Right contents box setup #
       lblDir1 = QLabel('Input desired date below (in yyyy,mm,dd format). Imagery dates of each WebCAT camera can be found at http://webcat-video.axds.co/status/')
       lblDir1.setWordWrap(True)
       self.bxYear = QLineEdit()
       self.bxMonth = QLineEdit()
       self.bxDay = QLineEdit()
       lblYear = QLabel('Year:')
       lblMonth = QLabel('Month:')
       lblDay = QLabel('Day:')
       contBut = QPushButton('Continue >')
       
       rightGroupBox = QGroupBox()
       self.grd = QGridLayout()
       self.grd.addWidget(lblDir1,0,0,1,4)
       self.grd.addWidget(self.bxYear,1,2,1,2)
       self.grd.addWidget(self.bxMonth,2,2,1,2)
       self.grd.addWidget(self.bxDay,3,2,1,2)
       self.grd.addWidget(lblYear,1,0,1,2)
       self.grd.addWidget(lblMonth,2,0,1,2)
       self.grd.addWidget(lblDay,3,0,1,2)
       self.grd.addWidget(contBut,4,2,1,2)
       #grd.setAlignment(Qt.AlignCenter)
       rightGroupBox.setLayout(self.grd)
       ##############################
       
       # Assign signals to widgets #
       contBut.clicked.connect(self.getInputs)
       #############################
            
       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       self.show()
       ############################
       
       
    def getInputs(self):
       '''
       Gets all the user inputs.
       '''
       
       yr = int(self.bxYear.text())
       mo = int(self.bxMonth.text())
       day = int(self.bxDay.text())
           
       # Instantiate worker threads #
       self.worker = DownloadVidThread(yr,mo,day)
       
       f = open(pth+'CameraName.pkl','rb')
       cameraName = pickle.load(f)
       print(cameraName)
       if cameraName == 'follypiersouthcam': # Need 1 erosion iter for Folly Pier South, 2 for other cams # 
           self.worker2 = CheckPTZThread(1)
       else:
           self.worker2 = CheckPTZThread(2)
       ##############################
       
       lab1 = QLabel('Downloading Video...')
       self.grd.addWidget(lab1,5,0,1,2)

       self.loadlab = QLabel()
       self.loadmovie = QMovie(pth+'loading.gif')
       self.loadlab.setMovie(self.loadmovie)
       
       self.worker.start()
       self.grd.addWidget(self.loadlab,5,3,1,1)
       self.loadmovie.start()
       self.worker.finishSignal.connect(self.on_closeSignal)

    def on_closeSignal(self):
       '''
       When download video thread is done, function shows a done label and starts the video decimation worker thread
       '''
       self.loadlab.setParent(None)
       self.loadmovie.stop()
       labDone = QLabel('Done.')
       self.grd.addWidget(labDone,5,3,1,1)
       
       lab2 = QLabel('Checking different views...')
       self.grd.addWidget(lab2,6,0,1,2)

       self.loadlab = QLabel()
       self.loadmovie = QMovie(pth+'loading.gif')
       self.loadlab.setMovie(self.loadmovie)
       
       self.worker2.start()
       self.grd.addWidget(self.loadlab,6,3,1,1)
       self.loadmovie.start()
       self.worker2.finishSignal.connect(self.on_closeSignal2)       
    
    def on_closeSignal2(self):
       '''
       When PTZ check thread is complete, function shows a Done label and moves to the next window
       '''
       self.loadlab.setParent(None)
       self.loadmovie.stop()

       self.close()
       self.cv = getWebCATImagery_ChooseViewWindow()
       self.cv.show()



class getOtherImagery_OtherCameraLocationInputWindow(QWidget):
    '''
    Window allowing the user to input necessary info on any (non WebCAT) surfcam, such as location and name. 
    '''
    def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()             
        self.initUI()
        
    def initUI(self):
       
       # Left menu box setup #
       bf = QFont()
       bf.setBold(True)
       leftBar1 = QLabel('• Welcome!')
       leftBar2 = QLabel('• Get imagery')
       leftBar3 = QLabel('• Get lidar data')
       leftBar4 = QLabel('• Pick GCPs')
       leftBar5 = QLabel('• Calibrate')
       leftBar6 = QLabel('• Rectify')
       leftBar2.setFont(bf)

       leftGroupBox = QGroupBox('Contents:')
       vBox = QVBoxLayout()
       vBox.addWidget(leftBar1)
       vBox.addWidget(leftBar2)
       vBox.addWidget(leftBar3)
       vBox.addWidget(leftBar4)
       vBox.addWidget(leftBar5)
       vBox.addWidget(leftBar6)
       vBox.addStretch(1)
       leftGroupBox.setLayout(vBox)
       ########################    
       
       # Right contents box setup #
       lblDir1 = QLabel('Input the name of this camera:')
       self.bxName = QLineEdit()
       lblDir = QLabel('Input the approximate location (lat/lon) of the camera below:')
       lblLat = QLabel('Camera Latitude (decimal degrees):')
       lblLon = QLabel('Camera Longitude (decimal degrees):')
       lblElev = QLabel('Elevation (m):')
       lblAz = QLabel('Azimuth (degrees):')
       self.bxLat = QLineEdit()
       self.bxLon = QLineEdit()
       self.bxElev = QLineEdit()
       self.bxAz = QLineEdit()
       self.azHelpBut = QPushButton('?')
       lblPth = QLabel('Input the full path of the image you want to use (path and filename with extension):')
       self.bxPth = QLineEdit()
       backBut = QPushButton('< Back')
       contBut = QPushButton('Continue >')
       
       rightGroupBox = QGroupBox()
       grd = QGridLayout()
       grd.addWidget(lblDir1,0,0,1,3)
       grd.addWidget(self.bxName,0,3,1,3)
       grd.addWidget(lblDir,1,0,1,6)
       grd.addWidget(lblLat,2,1,1,3)
       grd.addWidget(self.bxLat,2,4,1,2)
       grd.addWidget(lblLon,3,1,1,3)
       grd.addWidget(self.bxLon,3,4,1,2)
       grd.addWidget(lblElev,4,1,1,3)
       grd.addWidget(self.bxElev,4,4,1,2)
       grd.addWidget(self.azHelpBut,5,0,1,1)
       grd.addWidget(lblAz,5,1,1,3)
       grd.addWidget(self.bxAz,5,4,1,2)
       grd.addWidget(lblPth,6,0,1,6)
       grd.addWidget(self.bxPth,7,0,1,4)
       grd.addWidget(backBut,8,0,1,2)
       grd.addWidget(contBut,8,4,1,2)
       grd.setAlignment(Qt.AlignCenter)
       rightGroupBox.setLayout(grd)
       ##############################
       
       # Assign signals to widgets #
       backBut.clicked.connect(self.GoBack)
       contBut.clicked.connect(self.getInputs)
       self.azHelpBut.clicked.connect(self.onAzHelpClick)
       #############################

       
       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       self.show()
       ############################
       
    def onAzHelpClick(self):
       '''
       Display help box for azimuth.
       '''
       
       msg = QMessageBox(self)
       msg.setIcon(msg.Question)
       msg.setText('The azimuth angle is the right-handed angle that the camera is facing with respect to due north. A camera looking directly north has an azimuth angle of 0' + u'\N{DEGREE SIGN}'+', one looking east an azimuth of 90'+u'\N{DEGREE SIGN}'+', one south an azimuth of 180'+u'\N{DEGREE SIGN}'+', and one west an azimuth of 270'+u'\N{DEGREE SIGN}'+'.')
       msg.setStandardButtons(msg.Ok)
       msg.show()

    def GoBack(self):
       '''
       Go back to camera choice window on Back click
       '''
       self.close()
       self.backToOne = ChooseCameraWindow()    
       
    def getInputs(self):
       '''
       Get user-input information on Continue click
       '''
       cameraName = self.bxName.text()
       cameraLocation = [float(self.bxLat.text()),float(self.bxLon.text())]
       az= float(self.bxAz.text())     
       ZL = float(self.bxElev.text())
       pthToImage = self.bxPth.text()

       
       # Save the camera name and location #
       with open(pth+'CameraLocation.pkl','wb') as f:
           pickle.dump(cameraLocation,f)
       with open(pth+'CameraName.pkl','wb') as f:
           pickle.dump(cameraName,f)
       with open(pth+'az.pkl','wb') as f:
           pickle.dump(az,f)
       with open(pth+'ZL.pkl','wb') as f:
           pickle.dump(ZL,f)
       
       im = cv2.imread(pthToImage) 
       cv2.imwrite(pth+'frameUse.png',im)
       
       self.close()
       self.ls = getLidar_FindUseableDatasetsWindow()
       self.ls.show()



##============================================================================##
# Get lidar module #
##============================================================================##

class getLidar_FindUseableDatasetsWindow(QWidget):
     '''
     Window showing progress of search through NOAA lidar repositories for potentially usable datasets
     '''
     
     def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()             
        self.initUI()
        
       
     def initUI(self):
              
       # Left menu box setup #
       bf = QFont()
       bf.setBold(True)
       leftBar1 = QLabel('• Welcome!')
       leftBar2 = QLabel('• Get imagery')
       leftBar3 = QLabel('• Get lidar data')
       leftBar4 = QLabel('• Pick GCPs')
       leftBar5 = QLabel('• Calibrate')
       leftBar6 = QLabel('• Rectify')
       leftBar3.setFont(bf)

       leftGroupBox = QGroupBox('Contents:')
       vBox = QVBoxLayout()
       vBox.addWidget(leftBar1)
       vBox.addWidget(leftBar2)
       vBox.addWidget(leftBar3)
       vBox.addWidget(leftBar4)
       vBox.addWidget(leftBar5)
       vBox.addWidget(leftBar6)
       vBox.addStretch(1)
       leftGroupBox.setLayout(vBox)
       ########################    
       
       # Right contents box setup #
       self.pb = QProgressBar()
       self.lab1 = QLabel('Looking for nearby datasets:')
##       info = QLabel('Finding lidar datasets that cover this region:')
##       self.val = QLabel('0%')
        
       rightGroupBox = QGroupBox()
       self.grd = QGridLayout()
       self.grd.addWidget(self.lab1,0,0,1,4)
       
       
##       self.grd.addWidget(info,0,0,1,6)
##       self.grd.addWidget(self.val,1,0,1,1)
##       self.grd.addWidget(self.pb,1,0,1,5)
       self.grd.setAlignment(Qt.AlignCenter)
       rightGroupBox.setLayout(self.grd)
       ##############################
       
      
       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       self.show()
       ############################
       
       # Instantiate worker threads #
       f = open(pth+'CameraLocation.pkl','rb')
       cameraLocation = pickle.load(f)

       self.worker1 = getLidar_FindCloseDatasetIDsThread(cameraLocation[0],cameraLocation[1])
       self.worker1.finishSignal.connect(self.on_closeSignal1)
       self.worker = getLidar_FindCoveringDatasetsThread(cameraLocation[0],cameraLocation[1])
       self.worker.threadSignal.connect(self.on_threadSignal)
       self.worker.finishSignal.connect(self.on_closeSignal)
       self.worker.badSignal.connect(self.on_badSignal)

       self.loadlab = QLabel()
       self.loadmovie = QMovie(pth+'loading.gif')
       self.loadlab.setMovie(self.loadmovie)
       
       self.worker1.start()
       self.grd.addWidget(self.loadlab,0,4,1,4)
       self.loadmovie.start()
       
       ##############################

     def on_closeSignal1(self):
         
         self.loadlab.setParent(None)
         self.loadmovie.stop()
         
         labDone = QLabel('Done.')
         self.grd.addWidget(labDone,0,4,1,4)
         self.lab2 = QLabel('Checking nearby datasets:')
         self.grd.addWidget(self.lab2,1,0,1,4)
         self.grd.addWidget(self.pb,1,4,1,4)

         self.worker.start()
         ##############################
                     

     def on_threadSignal(self,perDone):
         '''
         Update progress bar value each time getLidar_FindCoveringDatasetsThread sends a signal (which is every time it finishes looking at a particular dataset)
         '''
         self.pb.setValue(perDone*100)
        
     def on_badSignal(self):
         
         doneInfo = QLabel('No lidar datasets were found near your camera. Select the Back button to try another camera.')
         doneInfo.setWordWrap(True)
         backBut = QPushButton('< Back')
         
         backBut.clicked.connect(self.GoBack)
         
         self.grd.addWidget(doneInfo,2,0,1,8)
         self.grd.addWidget(backBut,3,0,1,3)

     def on_closeSignal(self):
         '''
         When sorting of lidar datasets is completed, show that it is done and allow the user to click Continue to choose the dataset they want to use.
         '''

         doneInfo = QLabel('Lidar datasets found! Press continue to select the dataset you want to use for remote GCP extraction:')
         doneInfo.setWordWrap(True)
         contBut = QPushButton('Continue >')
         backBut = QPushButton('< Back')
         
         contBut.clicked.connect(self.GoToChooseLidarSet)
         backBut.clicked.connect(self.GoBack)
         
         self.grd.addWidget(doneInfo,2,0,1,8)
         self.grd.addWidget(contBut,3,5,1,3)
         self.grd.addWidget(backBut,3,0,1,3)
         
     def GoToChooseLidarSet(self):
         '''
         When Continue is pushed, open the table of lidar datasets.
         '''
         self.close()
         
         f = open(pth+'lidarTable.pkl','rb')
         lidarTable = pickle.load(f)
         
         self.lw = getLidar_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
         self.lw.resize(900,350)
         self.lw.show()
         
        
     def GoBack(self):
         '''
         Go back to camera choice window on Back click.
         '''
         self.close()
         self.backToOne = ChooseCameraWindow()        



class getLidar_ChooseLidarSetWindow(QWidget):
    '''
    Window showing a table of datasets that cover the location of the camera, allowing
    the user to choose their desired dataset.
    '''
    
    def __init__(self, data, rows, columns):
        QWidget.__init__(self)
        
        # Left menu box setup #
        bf = QFont()
        bf.setBold(True)
        leftBar1 = QLabel('• Welcome!')
        leftBar2 = QLabel('• Get imagery')
        leftBar3 = QLabel('• Get lidar data')
        leftBar4 = QLabel('• Pick GCPs')
        leftBar5 = QLabel('• Calibrate')
        leftBar6 = QLabel('• Rectify')
        leftBar3.setFont(bf)

        leftGroupBox = QGroupBox('Contents:')
        vBox = QVBoxLayout()
        vBox.addWidget(leftBar1)
        vBox.addWidget(leftBar2)
        vBox.addWidget(leftBar3)
        vBox.addWidget(leftBar4)
        vBox.addWidget(leftBar5)
        vBox.addWidget(leftBar6)
        vBox.addStretch(1)
        leftGroupBox.setLayout(vBox)
        ########################    
        
        # Right content box setup #
        self.table = QTableWidget(rows, columns, self)
        tblHeaders = ['Choose Dataset','Year Collected','Dataset Name']
        for self.column in range(0,columns):
            for self.row in range(0,rows):
                item = QTableWidgetItem(str(data.iloc[self.row][self.column]))
                if self.column == 0:
                    item.setFlags(Qt.ItemIsUserCheckable |
                                     Qt.ItemIsEnabled)
                    item.setCheckState(Qt.Unchecked)
                self.table.setItem(self.row, self.column, item)
                
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0,QHeaderView.Stretch)
            header.setSectionResizeMode(1,QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2,QHeaderView.ResizeToContents)
            
        self.table.setHorizontalHeaderLabels(["Dataset ID","Year Collected","Dataset Name"])
        self.table.setSelectionBehavior(QTableView.SelectRows)
        
        self.dir = QLabel('Select the dataset you want to use by checking its box:')
        self.contBut = QPushButton('Continue >')
        self.backBut = QPushButton('< Back')
        
        rightGroupBox = QGroupBox()
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.dir,0,0,1,1)
        self.layout.addWidget(self.table,1,0,4,4)
        self.layout.addWidget(self.contBut,6,3,1,1)
        self.layout.addWidget(self.backBut,6,2,1,1)
        self.layout.setAlignment(Qt.AlignCenter)
        rightGroupBox.setLayout(self.layout)
        ##############################
        
        # Connect widgets to signals #
        self.table.itemClicked.connect(self.dataChoice)
        self.contBut.clicked.connect(self.downloadCorrectData)
        self.backBut.clicked.connect(self.GoBack)
        ##############################
        
        # Full widget layout setup #
        fullLayout = QGridLayout()
        fullLayout.addWidget(leftGroupBox,0,0,2,2)
        fullLayout.addWidget(rightGroupBox,0,2,2,6)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        self.show()
        ############################
        
        # Instantiate worker threads #
        f = open(pth+'CameraLocation.pkl','rb')
        cameraLocation = pickle.load(f)
        
        self.worker = getLidar_PrepChosenSetThread(cameraLocation[0],cameraLocation[1])
        self.worker.threadSignal.connect(self.on_threadSignal)
        
        self.worker2 = getLidar_DownloadChosenSetThread(cameraLocation[0],cameraLocation[1])
        self.worker2.threadSignal.connect(self.on_threadSignal2)
        
        self.worker3 = getLidar_FormatChosenSetThread(cameraLocation[0],cameraLocation[1])
        ##############################
        
    def dataChoice(self,item):
        '''
        Save user's choice of dataset.
        '''
        
        print(str(item.text())) 
        
        num = int(item.text())
        with open(pth+'chosenLidarID.pkl','wb') as f:
            pickle.dump(num,f)
    
    def downloadCorrectData(self):
        '''
        Begin the download of the chosen dataset.
        '''
        
        lab1 = QLabel('Sorting tiles:')
        self.pb1 = QProgressBar()
        
        self.layout.removeWidget(self.contBut)
        self.contBut.deleteLater()
        self.contBut = None
        self.layout.removeWidget(self.backBut)
        self.backBut.deleteLater()
        self.backBut = None
        
        self.layout.addWidget(lab1,6,0,1,2)
        self.layout.addWidget(self.pb1,6,2,1,2)
 
        self.worker.start()
        self.worker.finishSignal.connect(self.on_closeSignal)                

    def on_threadSignal(self,perDone):
        self.pb1.setValue(perDone*100)
        
    def on_closeSignal(self):
        '''
        Move to next task when tiles are sorted.
        '''
        
        lab2 = QLabel('Downloading lidar data near camera:')
        self.pb2 = QProgressBar()
        
        self.layout.addWidget(lab2,7,0,1,2)
        self.layout.addWidget(self.pb2,7,2,1,2)
        
        self.worker2.start()
        self.worker2.finishSignal.connect(self.on_closeSignal2)
        
    def on_threadSignal2(self,perDone):
        self.pb2.setValue(perDone*100)
        
    def on_closeSignal2(self):
        '''
        Move to next task when lidar is downloaded.
        '''
        
        f = open(pth+'lidarDat.pkl','rb')
        ld = pickle.load(f)
        if len(ld>0):
        
            lab3 = QLabel('Creating data point cloud...')
        
            self.layout.addWidget(lab3,8,0,1,2)

            self.loadlab = QLabel()
            self.loadmovie = QMovie(pth+'loading.gif')
            self.loadlab.setMovie(self.loadmovie)
        
            self.worker3.start()
            self.layout.addWidget(self.loadlab,8,2,1,2)
            self.loadmovie.start()
            self.worker3.finishSignal.connect(self.on_closeSignal3)
        else: 
            msg = QMessageBox(self)
            msg.setIcon(msg.Warning)
            msg.setText('Oops, no lidar observations from this dataset were found near the camera. This could indicate that this region was skipped during data collection. Please press OK to choose a different dataset. ')
            msg.setStandardButtons(msg.Ok)
            msg.show()
            msg.buttonClicked.connect(self.chooseOtherSet)
            
    def chooseOtherSet(self):
        '''
        Allow the user to re-choose a dataset.
        '''
        
        self.close()
        
        f = open(pth+'lidarTable.pkl','rb')
        lidarTable = pickle.load(f)
         
        self.lw = getLidar_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
        self.lw.show()
         
        
    def on_closeSignal3(self):
        '''
        Finish when point cloud is created.
        '''
        
        self.loadlab.setParent(None)
        labDone = QLabel('Done')
        self.layout.addWidget(labDone,8,2,1,2)
        
        self.label = QLabel('Lidar downloaded! Press continue to pick GCPs:')
        contBut2 = QPushButton('Continue >')
        backBut2 = QPushButton('< Back')

        self.layout.addWidget(self.label,9,0,1,2)
        self.layout.addWidget(contBut2,10,3,1,1)
        self.layout.addWidget(backBut2,10,2,1,1)
        
        contBut2.clicked.connect(self.moveToNext)
        backBut2.clicked.connect(self.GoBack)
        
    def moveToNext(self):
        '''
        Move to next window.
        '''
        
        self.close()
        self.nextWindow = PickGCPsWindow()        
        
    def GoBack(self):
        self.close()
        self.backToOne = ChooseCameraWindow()
        

##============================================================================##
# Pick GCPs module #
##============================================================================##

class PickGCPsWindow(QWidget):
   '''
   Window introducing the PickGCPs module and allowing the user to perform the GCP picking.
   '''
   
   def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()             
          
        # Define variables which will hold the picked GCPs #    
        self.GCPs_im = np.empty([0,2])
        self.GCPs_lidar = np.empty([0,3])
        ####################################################
        
        # Left menu box setup #
        bf = QFont()
        bf.setBold(True)
        leftBar1 = QLabel('• Welcome!')
        leftBar2 = QLabel('• Get imagery')
        leftBar3 = QLabel('• Get lidar data')
        leftBar4 = QLabel('• Pick GCPs')
        leftBar5 = QLabel('• Calibrate')
        leftBar6 = QLabel('• Rectify')
        leftBar4.setFont(bf)

        leftGroupBox = QGroupBox('Contents:')
        vBox = QVBoxLayout()
        vBox.addWidget(leftBar1)
        vBox.addWidget(leftBar2)
        vBox.addWidget(leftBar3)
        vBox.addWidget(leftBar4)
        vBox.addWidget(leftBar5)
        vBox.addWidget(leftBar6)
        vBox.addStretch(1)
        leftGroupBox.setLayout(vBox)
        ########################  
        
        # Right contents box setup #
        img = mpimg.imread(pth+'frameUse.png')
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.imshow(img)
        self.canvas.draw()
            
        self.introLab = QLabel('Welcome to the GCP picking module! Here, you will be guided through the process of co-locating points in the image and the lidar observations. You must identify the correspondence of at least 3 unique points for the calibration to work.')
        self.introLab.setWordWrap(True)
        self.goLab = QLabel('Ready to co-locate points?')
        self.goBut = QPushButton('Go')
        
        self.rightGroupBox = QGroupBox()
        self.grd = QGridLayout()
        self.grd.addWidget(self.goBut,7,3,1,1)
        self.grd.addWidget(self.goLab,7,0,1,1)
        self.grd.addWidget(self.introLab,0,0,1,4)
        self.grd.addWidget(self.canvas,2,0,4,4)
        self.rightGroupBox.setLayout(self.grd)
        ###############################

        # Connect widgets with signals #
        self.goBut.clicked.connect(self.getPoints1)
        ################################
        
        # Instantiate worker threads #
        self.worker = pptkWindowWorker()
        self.worker.finishSignal.connect(self.on_CloseSignal)
        self.worker2 = pickGCPs_Image(self.canvas,gcps_im)
        ##############################
        
        
        # Full widget layout setup #
        fullLayout = QGridLayout()
        fullLayout.addWidget(leftGroupBox,0,0,2,2)
        fullLayout.addWidget(self.rightGroupBox,0,3,2,4)
        self.setLayout(fullLayout)

        self.setGeometry(400,100,1000,500)
        self.setWindowTitle('SurfRCaT')
        self.show()
        ############################

       
   def getPoints1(self):
       '''
       Start the lidar picking process.
       '''

       # Launch the lidar PC #
       self.worker.start()

       # Setup the lidar picking instructions #
       self.goBut.setParent(None)
       self.goLab.setParent(None)
       self.introLab.setParent(None)

       self.dirLab = QLabel('The lidar point cloud is opening in a seperate window. Click on the points in the lidar that you want to use as GCPs (remember the order), making sure to right click after each (including the last point). When done, simply close the lidar window.')
       self.dirLab.setWordWrap(True)
       self.helpBut = QPushButton('Help')

       self.helpBut.clicked.connect(self.onHelpClick)
                   
       self.grd.addWidget(self.dirLab,0,0,1,4)
       self.grd.addWidget(self.helpBut,7,0,1,1)


                          
   def on_CloseSignal(self):
       '''
       Start the image picking process.
       '''

       self.dirLab.setParent(None)

       self.dirLab2 = QLabel('Real-world coordinates of points saved! Now, click on the points (in the same order) in the image. Press Done when finished.')
       self.dirLab2.setWordWrap(True)
       self.doneBut = QPushButton('Done')

       self.grd.addWidget(self.dirLab2,0,0,1,4)
       self.grd.addWidget(self.doneBut,7,3,1,1)

       self.doneBut.clicked.connect(self.on_DoneClick)

       # Launch the image GCP picking process #
       self.worker2.start()
 
              
   def onHelpClick(self):
       '''
       Show help if needed.
       '''
       
       msg = QMessageBox(self)
       msg.setIcon(msg.Question)
       msg.setText('The lidar point cloud has been opened in a seperate window. The viewer can be navigated by clicking and dragging (to rotate view) as well as zooming in/out. Try to rotate/zoom the view until it looks as similar to the image as you can. To select a point, first right click anywhere in the viewer. Then, hold Control (Windows) or Command (Mac) and left click on the point to select it. Then return to this program to continue. IMPORTANT: You must right click in the viewer before selecting each new point in the lidar data.')
       msg.setStandardButtons(msg.Ok)
       msg.show()
       
               
   def on_DoneClick(self):
       '''
       Save the GCPs and display them to the user.
       '''
       
       self.dirLab2.setParent(None)
       self.doneBut.setParent(None)
       self.helpBut.setParent(None)       
    
       with open(pth+'GCPs_im.pkl','rb') as f:
           gcpS_im = pickle.load(f)
       self.ax.plot(gcpS_im[:,0],gcpS_im[:,1],'ro')
       
       self.lab = QLabel('Your GCPs are shown on the image below. Are you happy with them? Press Continue to perform the calibration using these GCPs or select Retry to pick again.')
       self.lab.setWordWrap(True)
       self.contBut = QPushButton('Continue')
       self.retryBut = QPushButton('Retry')
       
       self.contBut.clicked.connect(self.GotoCalibration)
       self.retryBut.clicked.connect(self.Retry)
       
       self.grd.addWidget(self.lab,0,0,1,4)
       self.grd.addWidget(self.retryBut,7,0,1,1)
       self.grd.addWidget(self.contBut,7,1,1,1)
       

   def Retry(self):
       '''
       Go back to the start of the GCP picking module if the user wants to try again.
       '''
       
       global gcps_im
       gcps_im = []
       self.close()
       self.a = PickGCPsWindow()
       self.a.show()
       
   def GotoCalibration(self):
       '''
       Go to the calibration module
       '''
       
       self.close()
       self.calibrateWindow = calibrate_Welcome()
       self.calibrateWindow.show()



##=========================================================================##
# Calibration module #
##=========================================================================##
class calibrate_Welcome(QWidget):
   '''
   Window welcoming the user to the calibration module and letting them begin with a click
   '''
   
   def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()             
                 
        # Left menu box setup #
        bf = QFont()
        bf.setBold(True)
        leftBar1 = QLabel('• Welcome!')
        leftBar2 = QLabel('• Get imagery')
        leftBar3 = QLabel('• Get lidar data')
        leftBar4 = QLabel('• Pick GCPs')
        leftBar5 = QLabel('• Calibrate')
        leftBar6 = QLabel('• Rectify')
        leftBar5.setFont(bf)

        leftGroupBox = QGroupBox('Contents:')
        vBox = QVBoxLayout()
        vBox.addWidget(leftBar1)
        vBox.addWidget(leftBar2)
        vBox.addWidget(leftBar3)
        vBox.addWidget(leftBar4)
        vBox.addWidget(leftBar5)
        vBox.addWidget(leftBar6)
        vBox.addStretch(1)
        leftGroupBox.setLayout(vBox)
        ########################  

        # Right contents box setup #
        img = mpimg.imread(pth+'frameUse.png')
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.imshow(img)
        self.canvas.draw()
        
        self.introLab = QLabel('Welcome to the Calibration module! Press the CALIBRATE button below to perform the calibration.')
        self.introLab.setWordWrap(True)
        self.calibBut = QPushButton('CALIBRATE')

        self.rightGroupBox = QGroupBox()
        self.grd = QGridLayout()
        self.grd.addWidget(self.introLab,0,0,1,4)
        self.grd.addWidget(self.canvas,2,0,4,4)
        self.grd.addWidget(self.calibBut,6,1,1,2)
        self.rightGroupBox.setLayout(self.grd)
        ###############################
        
        # Full widget layout setup #
        fullLayout = QGridLayout()
        fullLayout.addWidget(leftGroupBox,0,0,2,2)
        fullLayout.addWidget(self.rightGroupBox,0,3,2,4)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        self.show()
        ############################ 
        
        # Connect widgets with signals #
        self.calibBut.clicked.connect(self.onCalibClick)
        self.worker = calibrate_CalibrateThread()

        # Instantiate worker thread #
        self.worker = calibrate_CalibrateThread()
        #############################################################

    
   def onCalibClick(self):
        '''
        Begin the calibration process on the button click.
        '''
       
        self.worker.start()
        self.worker.finishSignal.connect(self.on_closeSignal)  
      
   def on_closeSignal(self):
        '''
        Move to the next window.
        '''
       
        self.close()
        self.finalWindow = calibrate_ShowCalibResultsWindow()
        self.finalWindow.show()

      

class calibrate_ShowCalibResultsWindow(QWidget):
   '''
   Window showing the reprojected positions of the GCPs on the image based on the resolved calibration parameters.
   '''
   
   def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()           
        
        # Left menu box setup #
        bf = QFont()
        bf.setBold(True)
        leftBar1 = QLabel('• Welcome!')
        leftBar2 = QLabel('• Get imagery')
        leftBar3 = QLabel('• Get lidar data')
        leftBar4 = QLabel('• Pick GCPs')
        leftBar5 = QLabel('• Calibrate')
        leftBar6 = QLabel('• Rectify')
        leftBar5.setFont(bf)

        leftGroupBox = QGroupBox('Contents:')
        vBox = QVBoxLayout()
        vBox.addWidget(leftBar1)
        vBox.addWidget(leftBar2)
        vBox.addWidget(leftBar3)
        vBox.addWidget(leftBar4)
        vBox.addWidget(leftBar5)
        vBox.addWidget(leftBar6)
        vBox.addStretch(1)
        leftGroupBox.setLayout(vBox)
        ########################  
        
        # Right contents box setup #
        img = mpimg.imread(pth+'frameUse.png')
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.imshow(img)
        self.canvas.draw()
        
        # Plot the GCPs and reprojected positions #
        f1 = open(pth+'GCPs_im.pkl','rb') 
        f2 = open(pth+'GCPs_lidar.pkl','rb') 
        f3 = open(pth+'calibVals.pkl','rb') 
       
        GCPs_im = pickle.load(f1)
        GCPs_lidar = pickle.load(f2)
        calibVals = pickle.load(f3)
        
        # Plot the GCPs as IDd in the image #
        for i in range(0,len(GCPs_im)):
            Xc = GCPs_im[i,:]
            self.ax.plot(Xc[0],Xc[1],'o')
          
            
        # Plot the reprojection positions of the GCPs and the residuals (differences) between identified and reprojected #
        uProj,vProj = SurfRCaT.calibrate_CalcReprojPos(GCPs_lidar,calibVals)
        
        for i in range(0,len(GCPs_im)):
            Xc = GCPs_im[i,:]              
            self.ax.plot(uProj[i],vProj[i],'x')
            
        # Calculate the re-projection error of the GCPs #
        uv = np.hstack([uProj,vProj])
        allResid = np.subtract(GCPs_im,uv)
        np.savetxt(pth+'calibResid.txt',allResid,fmt='%6f')
        RMSresid = np.sqrt(np.mean(np.reshape(np.subtract(GCPs_im,uv),[np.size(np.subtract(GCPs_im,uv)),1])**2))
        
        self.introLab = QLabel('The reprojection of each picked GCP based on the calibration is shown below. The Xs should align with the Os if the calibration was accurate.')
        self.introLab.setWordWrap(True)
        self.residLab = QLabel('The RMS of the control point residuals for the calibration is '+str(round(RMSresid,3))+' pixels. The residuals for each point have been saved in the text file calibResid.txt. The calibration parameters have been saved to the text file calibVals.txt. If you are unhappy with the calibration, you can retry by clicking the Retry button. Otherwise, click Continue to enter the rectification module.')
        self.residLab.setWordWrap(True)
        self.retryBut = QPushButton('Retry')
        self.contBut = QPushButton('Continue')
        self.rightGroupBox = QGroupBox()
        self.grd = QGridLayout()
        self.grd.addWidget(self.introLab,0,0,1,4)
        self.grd.addWidget(self.canvas,2,0,4,4)
        self.grd.addWidget(self.residLab,6,0,2,4)
        self.grd.addWidget(self.retryBut,8,0,1,1)
        self.grd.addWidget(self.contBut,8,3,1,1)
        self.rightGroupBox.setLayout(self.grd)
        ###############################

        # Connect widgets with signals #
        self.retryBut.clicked.connect(self.onRetryClick)
        self.contBut.clicked.connect(self.onContClick)
        ################################
        
        
        # Full widget layout setup #
        fullLayout = QGridLayout()
        fullLayout.addWidget(leftGroupBox,0,0,2,2)
        fullLayout.addWidget(self.rightGroupBox,0,3,2,4)
        self.setLayout(fullLayout)

        self.setGeometry(400,100,1000,500)
        self.setWindowTitle('SurfRCaT')
        self.show()
        ############################

   def onRetryClick(self):
       '''
       Let the user retry the picking on a button click.
       '''
       
       self.close()
       self.w = PickGCPsWindow()
       self.w.show()
        
   def onContClick(self):
       '''
       Move to the next window.
       '''
       
       self.close()
       self.w = rectify_InputsWindow()
       self.w.show()
        


##=========================================================================##
# Rectification module #
##=========================================================================##
class rectify_InputsWindow(QWidget):
   '''
   Window allowing the user to input the image and object-space grid onto which to rectify the image.
   '''
   def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()             
        
        # Left menu box setup #
        bf = QFont()
        bf.setBold(True)
        leftBar1 = QLabel('• Welcome!')
        leftBar2 = QLabel('• Get imagery')
        leftBar3 = QLabel('• Get lidar data')
        leftBar4 = QLabel('• Pick GCPs')
        leftBar5 = QLabel('• Calibrate')
        leftBar6 = QLabel('• Rectify')
        leftBar6.setFont(bf)

        leftGroupBox = QGroupBox('Contents:')
        vBox = QVBoxLayout()
        vBox.addWidget(leftBar1)
        vBox.addWidget(leftBar2)
        vBox.addWidget(leftBar3)
        vBox.addWidget(leftBar4)
        vBox.addWidget(leftBar5)
        vBox.addWidget(leftBar6)
        vBox.addStretch(1)
        leftGroupBox.setLayout(vBox)
        ########################  

        # Right contents box setup #
        introLab = QLabel('Welcome to the rectification module. Here you can produce a rectified image from your camera using the previously-obtained calibration parameters. You can input any image from the camera, so long as it is an image of the same area as the image used in the calibration.')
        introLab.setWordWrap(True)
        dirLab1 = QLabel('Please provide the full path and filename of the image you wish to rectify:')
        dirLab1.setWordWrap(True)
        dirLab11 = QLabel('Or')
        self.UseCalibIm = QRadioButton('Use calibration image')
        dirLab2 = QLabel('Please provide an object-space grid to rectify the image onto (cordinates are meters from input camera location):')
        dirLab2.setWordWrap(True)
        imagePthLab = QLabel('Image path:')
        self.imagePthBx = QLineEdit()
        xminLab = QLabel('xmin:')
        self.xminBx = QLineEdit()
        xmaxLab = QLabel('xmax:')
        self.xmaxBx = QLineEdit()        
        dxLab = QLabel('dx:')
        self.dxBx = QLineEdit()
        yminLab = QLabel('ymin:')
        self.yminBx = QLineEdit()
        ymaxLab = QLabel('ymax:')
        self.ymaxBx = QLineEdit()
        dyLab = QLabel('dy:')
        self.dyBx = QLineEdit()
        zLab = QLabel('z:')
        self.zBx = QLineEdit()
        contBut = QPushButton('Continue >')

        self.rightGroupBox1 = QGroupBox()
        self.rightGroupBox2 = QGroupBox()
        self.grd = QGridLayout()
        self.grd1 = QGridLayout()
        self.grd2 = QGridLayout()
        
        self.grd.addWidget(introLab,0,0,1,6)
        
        self.grd1.addWidget(dirLab1,0,0,1,6)
        self.grd1.addWidget(imagePthLab,1,0,1,2)
        self.grd1.addWidget(self.imagePthBx,1,2,1,4)
        self.grd1.addWidget(dirLab11,2,0,1,2)
        self.grd1.addWidget(self.UseCalibIm,3,0,1,4)
        self.rightGroupBox1.setLayout(self.grd1)

        self.grd2.addWidget(dirLab2,0,0,1,6)
        self.grd2.addWidget(xminLab,1,0,1,2)
        self.grd2.addWidget(self.xminBx,1,2,1,4)
        self.grd2.addWidget(xmaxLab,2,0,1,2)
        self.grd2.addWidget(self.xmaxBx,2,2,1,4)
        self.grd2.addWidget(dxLab,3,0,1,2)
        self.grd2.addWidget(self.dxBx,3,2,1,4)
        self.grd2.addWidget(yminLab,4,0,1,2)
        self.grd2.addWidget(self.yminBx,4,2,1,4)
        self.grd2.addWidget(ymaxLab,5,0,1,2)
        self.grd2.addWidget(self.ymaxBx,5,2,1,4)
        self.grd2.addWidget(dyLab,6,0,1,2)
        self.grd2.addWidget(self.dyBx,6,2,1,4)
        self.grd2.addWidget(zLab,7,0,1,2)
        self.grd2.addWidget(self.zBx,7,2,1,4)
        self.grd2.addWidget(contBut,8,5,1,1)
        self.rightGroupBox2.setLayout(self.grd2)

        # Connect widgets with signals #
        contBut.clicked.connect(self.onContClick)
        ################################

        # Full widget layout setup #
        fullLayout = QGridLayout()
        fullLayout.addWidget(leftGroupBox,0,0,5,2)
        fullLayout.addLayout(self.grd,0,3,1,4)
        fullLayout.addWidget(self.rightGroupBox1,1,3,2,4)
        fullLayout.addWidget(self.rightGroupBox2,3,3,2,4)
        self.setLayout(fullLayout)
        self.setWindowTitle('SurfRCaT')
        self.show()
        ############################

   def onContClick(self):
        '''
        Get all user inputs on button click.
        '''

        # Acquire all the inputs #
        xmin = float(self.xminBx.text())
        xmax = float(self.xmaxBx.text())
        dx = float(self.dxBx.text())
        ymin = float(self.yminBx.text())
        ymax = float(self.ymaxBx.text())
        dy = float(self.dyBx.text())
        z = float(self.zBx.text())
        print(ymin)

        if self.UseCalibIm.isChecked():
            impth = pth+'frameUse.png'
        else:
            impth = self.imagePthBx.text()
            
        img = mpimg.imread(impth)
        print(impth)

        # Start the worker #
        self.worker = performRectificationThread(img,impth,xmin,xmax,dx,ymin,ymax,dy,z)

        lab1 = QLabel('Performing rectification...')
        self.grd2.addWidget(lab1,9,0,1,3)

        self.loadlab = QLabel()
        self.loadmovie = QMovie(pth+'loading.gif')
        self.loadlab.setMovie(self.loadmovie)
       
        self.worker.start()
        self.grd2.addWidget(self.loadlab,9,3,1,3)
        self.loadmovie.start()
        self.worker.finishSignal.connect(self.on_closeSignal) 

   def on_closeSignal(self):
        '''
        Move to next window.
        '''
        
        self.close()
        self.w = rectify_ShowResultsWindow()
        self.w.show()


class rectify_ShowResultsWindow(QWidget):
   '''
   Window showing the user the rectified image product.
   '''
   
   def __init__(self):
        super().__init__()    
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()             
                 
        # Left menu box setup #
        bf = QFont()
        bf.setBold(True)
        leftBar1 = QLabel('• Welcome!')
        leftBar2 = QLabel('• Get imagery')
        leftBar3 = QLabel('• Get lidar data')
        leftBar4 = QLabel('• Pick GCPs')
        leftBar5 = QLabel('• Calibrate')
        leftBar6 = QLabel('• Rectify')
        leftBar6.setFont(bf)

        leftGroupBox = QGroupBox('Contents:')
        vBox = QVBoxLayout()
        vBox.addWidget(leftBar1)
        vBox.addWidget(leftBar2)
        vBox.addWidget(leftBar3)
        vBox.addWidget(leftBar4)
        vBox.addWidget(leftBar5)
        vBox.addWidget(leftBar6)
        vBox.addStretch(1)
        leftGroupBox.setLayout(vBox)
        ########################  

        # Right contents box setup #
        f1 = open(pth+'im_rectif.pkl','rb')
        f2 = open(pth+'extents.pkl','rb')
        im_rectif = pickle.load(f1)
        extents = pickle.load(f2)
        
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.imshow(im_rectif,extent=extents,interpolation='bilinear')
        self.ax.set_xlabel('Local x (m)')
        self.ax.set_ylabel('Local y (m)')
        self.ax.axis('equal')
        self.canvas.draw()
        
        self.introLab = QLabel('Your rectified image is shown below, and is saved to the same directory as the input image with the name <imName>_rectif.png. If you would like to rectify another image, select Back. Otherwise, you can close the tool.')
        self.introLab.setWordWrap(True)
        self.backBut = QPushButton('< Back')
        self.closeBut = QPushButton('Close')

        self.rightGroupBox = QGroupBox()
        self.grd = QGridLayout()
        self.grd.addWidget(self.introLab,0,0,1,4)
        self.grd.addWidget(self.canvas,2,0,4,4)
        self.grd.addWidget(self.backBut,6,0,1,2)
        self.grd.addWidget(self.closeBut,6,2,1,2)
        self.rightGroupBox.setLayout(self.grd)
        ###############################
        
        # Full widget layout setup #
        fullLayout = QGridLayout()
        fullLayout.addWidget(leftGroupBox,0,0,2,2)
        fullLayout.addWidget(self.rightGroupBox,0,3,2,4)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        self.show()
        ############################

        # Connect widgets with signals #
        self.backBut.clicked.connect(self.on_BackClick)
        self.closeBut.clicked.connect(self.on_CloseClick)

   def on_BackClick(self):
       '''
       Go back to rectification inputs on button click (to do another image perhaps)
       '''
       
       self.close()
       self.w = rectify_InputsWindow()
       self.w.show()

   def on_CloseClick(self):
       '''
       Close the tool on button click.
       '''
       
       self.close()



        
        
##=========## 
## Threads ##
##=========## 
class DownloadVidThread(QThread):
    '''
    Worker thread to perform WebCAT video download from online.
    '''
    threadSignal = pyqtSignal('PyQt_PyObject')
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,year,month,day):
        super().__init__()
        self.year = year
        self.month = month
        self.day = day
        
    def run(self):
        
       print('Thread Started')
       
       f = open(pth+'CameraName.pkl','rb')      
       camToInput = pickle.load(f)
       
       if self.year and self.month and self.day:
           vidFile = SurfRCaT.getImagery_GetVideo(pth,camToInput,year=self.year,month=self.month,day=self.day)
       else:
           vidFile = SurfRCaT.getImagery_GetVideo(pth,camToInput)
       
       # Deal with Buxton camera name change #
       fs = os.path.getsize(pth+vidFile) # Get size of video file #  
       if camToInput == 'buxtoncoastalcam' and fs<1000:
           vidFile = SurfRCaT.getImagery_GetVideo('buxtonnorthcam')
       #######################################
       
       with open(pth+'vidFile.pkl','wb') as f:
           pickle.dump(vidFile,f)
           
       self.finishSignal.emit(1)   
        
       print('Thread Done')
 
      
class CheckPTZThread(QThread):
    ''' 
    Worker thread to check if camera is a PTZ camera.
    '''
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,numIters):
        super().__init__()
        self.numIters = numIters
        
    def run(self):
        
       print('Thread Started')
       
       f = open(pth+'vidFile.pkl','rb')      
       vidFile = pickle.load(f)
       
       # Check if PTZ #       
       fullVidPth = pth+vidFile           
       viewDF,frameVec = SurfRCaT.getImagery_CheckPTZ(fullVidPth,self.numIters)
       
       with open(pth+'viewDF.pkl','wb') as f:
           pickle.dump(viewDF,f)
           
       self.finishSignal.emit(1) 
        
       print('Thread Done')
       
       
class getLidar_FindCloseDatasetIDsThread(QThread):

    '''
    Worker thread to find lidar datasets that may be close to the camera.
    '''

    threadSignal = pyqtSignal('PyQt_PyObject')
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,cameraLoc_lat,cameraLoc_lon):
        super().__init__()
        self.cameraLoc_lat = cameraLoc_lat 
        self.cameraLoc_lon = cameraLoc_lon

    def run(self):
        
        print('Thread Started')
        
        IDs = SurfRCaT.getLidar_FindPossibleIDs(self.cameraLoc_lat,self.cameraLoc_lon)

        print('Thread Done')   

        with open(pth+'lidarIDs.pkl','wb') as f:
            pickle.dump(IDs,f)

        self.finishSignal.emit(1)
        

class getLidar_FindCoveringDatasetsThread(QThread):
    
    '''
    Worker thread to find lidar datasets the cover the camera location.
    '''
    
    threadSignal = pyqtSignal('PyQt_PyObject')
    finishSignal = pyqtSignal('PyQt_PyObject')
    badSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,cameraLoc_lat,cameraLoc_lon):
        super().__init__()
        self.cameraLoc_lat = cameraLoc_lat 
        self.cameraLoc_lon = cameraLoc_lon

    def run(self):
        
        print('Thread Started')
        
        f = open(pth+'lidarIDs.pkl','rb')
        IDs = pickle.load(f)

        # If no lidar datasets were found here, need to tell the user #
        if not IDs:
            self.badSignal.emit(1)
        else: 
            ftp = ftplib.FTP('ftp.coast.noaa.gov',timeout=1000000)
            ftp.login('anonymous','anonymous')
            
            appropID = list() # Initiate list of IDs which contain the camera location #
            i = 0
            for ID in IDs:
                
                i = i+1
                perDone = i/len(IDs)
                self.threadSignal.emit(perDone)  
                
                check = SurfRCaT.getLidar_TryID(ftp,ID,self.cameraLoc_lat,self.cameraLoc_lon)
                
                if check:
                    if len(check)>0:       
                        appropID.append(ID)
            
            matchingTable = SurfRCaT.getLidar_GetDatasetNames(appropID)
            
            # Remove the strange Puerto Rico dataset that always shows up #
            idxNames = matchingTable[matchingTable['ID']==8560].index
            matchingTable.drop(idxNames,inplace=True)
            ###############################################################
              
            print('Thread Done')

            if len(matchingTable) == 0:
                self.badSignal.emit(1)
            else:
                with open(pth+'lidarTable.pkl','wb') as f:
                    pickle.dump(matchingTable,f)

            self.finishSignal.emit(1)  


class getLidar_WebCATThread(QThread):
    
    '''
    Worker thread to get the names of the lidar datasets applicable to WebCAT cameras (pre-loaded).
    '''
    
    threadSignal = pyqtSignal('PyQt_PyObject')
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()

    def run(self):

        print('Thread Started')

        cams = ['staugustinecam','twinpierscam','miami40thcam']

        f = open(pth+'CameraName.pkl','rb')
        name = pickle.load(f)

        # Add the pre-defined applicable lidar ids for each WebCAT camera #
        if name == 'buxtoncoastalcam':
            IDs = [8688,6329,5184,4954,2488,1117,8609,1071,86,19,1397,6300,8,60,61,6,2,1]
        elif name == 'cherrypiersouthcam':
            IDs = [8617,6329,5184,4184,4800,34,10,8,61,6,2,1]
        elif name == 'follypiernorthcam':
            IDs = [8575,5184,34,10,2,1]
        elif name == 'follypiersouthcam':
            IDs = [8575,5184,34,10,2,1]
        elif name == 'staugustinecam':
            IDs = [6330,5185,5184,8698,1070,1119,34,37,100,19,8]
        elif name == 'twinpierscam':
            IDs = [8793,5183,8603,529,44,37,19,22]
        else:
            IDs = [6330,8713,5185,5184,5038,8608,520,34,37,19,8]

        matchingTable = SurfRCaT.getLidar_GetDatasetNames(IDs)

                      
        print('Thread Done')

        with open(pth+'lidarTable.pkl','wb') as f:
            pickle.dump(matchingTable,f)

        self.finishSignal.emit(1)



class getLidar_PrepChosenSetThread(QThread):
    
    '''
    Worker thread to find the applicable tiles in the chosen dataset.
    '''

    threadSignal = pyqtSignal('PyQt_PyObject')
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,cameraLoc_lat,cameraLoc_lon):
        super().__init__()
        self.cameraLoc_lat = cameraLoc_lat 
        self.cameraLoc_lon = cameraLoc_lon

    def run(self):
        
        print('Thread Started')
                
        f = open(pth+'chosenLidarID.pkl','rb')
        f1 = open(pth+'az.pkl','rb')
        IDToDownload = pickle.load(f)
        az = pickle.load(f1)
        sf = SurfRCaT.getLidar_GetShapefile(IDToDownload)
        poly = SurfRCaT.getLidar_CalcViewArea(az,40,1000,self.cameraLoc_lat,self.cameraLoc_lon)
        
        tilesKeep = list()
        i = 0
        self.threadSignal.emit(0)
        for shapeNum in range(0,len(sf)):

            out = SurfRCaT.getLidar_SearchTiles(sf,poly,shapeNum,self.cameraLoc_lat,self.cameraLoc_lon)
            if out:
                tilesKeep.append(out)

            i = i+1
            perDone = i/len(sf)
            self.threadSignal.emit(perDone)

        

        with open(pth+'tilesKeep.pkl','wb') as f:
            pickle.dump(tilesKeep,f)
            
        self.finishSignal.emit(1)
        
        print('Thread Done')
        
  
      
class getLidar_DownloadChosenSetThread(QThread):

    '''
    Worker thread to download the applicable tiles of the selected dataset.
    '''

    threadSignal = pyqtSignal('PyQt_PyObject')
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,cameraLoc_lat,cameraLoc_lon):
        super().__init__()
        self.cameraLoc_lat = cameraLoc_lat 
        self.cameraLoc_lon = cameraLoc_lon
        
    def run(self):
        print('Thread Started')
        
        f = open(pth+'tilesKeep.pkl','rb')
        tilesKeep = pickle.load(f)
        
        f = open(pth+'chosenLidarID.pkl','rb')
        IDToDownload = pickle.load(f)
        
        i = 0
        lidarDat = np.empty([0,3])
        self.threadSignal.emit(.01)
        for thisFile in tilesKeep:
            
            lidarXYZsmall = SurfRCaT.getLidar_Download(thisFile,IDToDownload,self.cameraLoc_lat,self.cameraLoc_lon)
            
            lidarDat = np.append(lidarDat,lidarXYZsmall,axis=0)

            i = i+1
            perDone = i/len(tilesKeep)
            self.threadSignal.emit(perDone)

        with open(pth+'lidarDat.pkl','wb') as f:
            pickle.dump(lidarDat,f)
            
        self.finishSignal.emit(1)   
        
        print('Thread Done')        
        
 
       
class getLidar_FormatChosenSetThread(QThread):
    
    '''
    Worker thread to format the downloaded data as a pandas dataframe,
    with locations relative to the camera location.
    '''
        
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,cameraLoc_lat,cameraLoc_lon):
        super().__init__()
        self.cameraLoc_lat = cameraLoc_lat
        self.cameraLoc_lon = cameraLoc_lon
        
    def run(self):

        print('Thread Started')
        
        f = open(pth+'lidarDat.pkl','rb')
        lidarDat = pickle.load(f)

        pc = SurfRCaT.getLidar_CreatePC(lidarDat,self.cameraLoc_lat,self.cameraLoc_lon)
          
        with open(pth+'lidarPC.pkl','wb') as f:
            pickle.dump(pc,f)
            
        self.finishSignal.emit(1)    
        
        print('Thread Done')   
        

class pptkWindowWorker(QThread):

    '''
    Worker thread to launch the pptk lidar viewer window
    '''
    
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()
        
    def run(self):
        
        print('Thread Started')

        # Load the point cloud #        
        f = open(pth+'lidarPC.pkl','rb')
        pc = pickle.load(f)

        # Delete any pre-existing GCP files if they exist #
        try:
            os.remove(pth+'GCPs_lidar.txt')
            os.remove(pth+'GCPs_lidar.pkl')
            os.remove(pth+'GCPs_im.txt')
            os.remove(pth+'GCPs_im.pkl')
            os.remove(pth+'Testing.txt')
        except OSError:
            pass

        # Call the viewer and let the user identify points (subprocess saves the output to file #
        command = 'cmd.exe /C '+pth+'LaunchPPTKwin\LaunchPPTKwin.exe'
        print(command)
        self.child = QProcess()
        self.child.start(command)
        self.child.waitForStarted(-1)
        self.child.waitForFinished(-1)

        # Load the output and create the GCPs from it #
        f = open(pth+'Testing.txt','r')
        iGCPs1 = f.read()
        iGCPs2 = iGCPs1[1:len(iGCPs1)-2]
        
        iGCPs = list(map(int,iGCPs2.split(',')))
        
        GCPs_lidar = np.empty([0,3])
        for i in iGCPs:
            GCPs_lidar = np.vstack((GCPs_lidar,pc.iloc[i,:]))
        
        np.savetxt(pth+'GCPS_lidar.txt',GCPs_lidar)

        with open(pth+'GCPs_lidar.pkl','wb') as f:
            pickle.dump(GCPs_lidar,f)

        self.finishSignal.emit(1)    
        
        print('Thread Done')        


gcps_im = []
class pickGCPs_Image(QThread):

    '''
    Worker thread to allow GCP identification in the image
    '''
        
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,canvas,gcps_im):
        super().__init__()
        self.canvas = canvas
        
    def run(self):

        print('Thread Started')

        def onclick(event):

           ix,iy = event.xdata,event.ydata
  
           global gcps_im
           gcps_im.append((ix,iy))
           gcps_im2 = np.array(gcps_im)
           uVals = np.empty([0,2])
           for i in range(0,len(gcps_im2[:,0])):
               if gcps_im2[i,0] not in uVals[:,0] or gcps_im2[i,1] not in uVals[:,1]:
                   uVals = np.vstack([uVals,np.hstack([gcps_im2[i,0],gcps_im2[i,1]])])
           else:
               pass
           gcps_im2 = uVals  
               
            
           with open(pth+'GCPs_im.pkl','wb') as f:
               pickle.dump(gcps_im2,f)

           np.savetxt(pth+'GCPS_im.txt',gcps_im2)

           return
 
           
        while True:
            cid = self.canvas.mpl_connect('button_press_event',lambda event: onclick(event))
            time.sleep(1)
            
        self.finishSignal.emit(1)    
        
        print('Thread Done')



class calibrate_CalibrateThread(QThread):

    '''
    Worker thread to perform the calibration
    '''
        
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()
        
    def run(self):
        
        print('Thread Started')
        
        # Load everything that we already have: GCPs, image, azimuth, and ZL #
        f1 = open(pth+'GCPs_im.pkl','rb')
        f2 =  open(pth+'GCPs_lidar.pkl','rb')     
        f_az = open(pth+'az.pkl','rb')
        f_ZL = open(pth+'ZL.pkl','rb')
        
        img = cv2.imread(pth+'frameUse.png')
        gcps_im = pickle.load(f1)
        gcps_lidar = pickle.load(f2)
        az = pickle.load(f_az)
        ZL = pickle.load(f_ZL)
        
        
        # Get initial approximations for all remaining parameters #
        XL = 0 # We etablished this by creating the lidar point cloud relative to the camera's estimated location. #
        YL = 0
        f,x0,y0 = SurfRCaT.calibrate_GetInitialApprox_IOPs(img)
        omega,phi,kappa = SurfRCaT.calibrate_GetInitialApprox_ats2opk(az,80,180)
        initApprox = np.array([omega,phi,kappa,XL,YL,ZL,f,x0,y0])

        # Perform the calibration #
        calibVals1,So1 = SurfRCaT.calibrate_PerformCalibration(initApprox,np.array([0,0,0,1,1,1,0,0,0]),gcps_im,gcps_lidar)
        updatedApprox = calibVals1
        calibVals,So = SurfRCaT.calibrate_PerformCalibration(np.array([updatedApprox[0],updatedApprox[1],updatedApprox[2],initApprox[3],initApprox[4],initApprox[5],updatedApprox[6],updatedApprox[7],updatedApprox[8]]),np.array([1,1,1,0,0,0,1,1,1]),gcps_im,gcps_lidar)
        
        with open(pth+'calibVals.pkl','wb') as f:
            pickle.dump(calibVals,f)
            
##        ar1 = np.array(['Omega(rad)','Phi(rad)','Kappa(rad)','CamX(m)','CamY(m)','CamZ(m)','x0(pix)','y0(pix)','f(pix)'])
##        ar2 = np.array([calibVals[0],calibVals[1],calibVals[2],calibVals[3],calibVals[4],calibVals[5],calibVals[6],calibVals[7],calibVals[8]])
##        with open(pth+'calibVals2.txt','w') as f:
##            writer = csv.writer(f,delimiter=',')
##            writer.writerows(zip(ar1,ar2))
            
        np.savetxt(pth+'calibVals.txt',calibVals,fmt='%6f')            
      
        self.finishSignal.emit(1)    

        print('Thread Done')



class performRectificationThread(QThread):
    
    '''
    Worker thread to perform the rectification.
    '''
        
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,img,impth,xmin,xmax,dx,ymin,ymax,dy,z):
        super().__init__()
        self.img = img
        self.impth = impth
        self.xmin = xmin
        self.xmax = xmax
        self.dx = dx
        self.ymin = ymin
        self.ymax = ymax
        self.dy = dy
        self.z = z
        
    def run(self):

        print('Thread Started')
        
        f = open(pth+'calibVals.pkl','rb')
        calibVals = pickle.load(f)
        print(calibVals)

        im_rectif,extents = SurfRCaT.rectify_RectifyImage(calibVals,self.img,self.xmin,self.xmax,self.dx,self.ymin,self.ymax,self.dy,self.z)

        # Save the parameters #  
        with open(pth+'im_rectif.pkl','wb') as f:
            pickle.dump(im_rectif,f)
        with open(pth+'extents.pkl','wb') as f:
            pickle.dump(extents,f)

        # Save the rectified image #
        imDir = os.path.dirname(self.impth)
        imName = os.path.basename(self.impth).split('.')[0]
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.imshow(im_rectif,extent=extents,interpolation='bilinear')
        self.ax.set_xlabel('Local x (m)')
        self.ax.set_ylabel('Local y (m)')
        self.ax.axis('equal')
        self.canvas.print_figure(imDir+'/'+imName+'_rectif.png')
            
        self.finishSignal.emit(1)    
        
        print('Thread Done')



# Launch the tool #       
if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    w = WelcomeWindow()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)



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
