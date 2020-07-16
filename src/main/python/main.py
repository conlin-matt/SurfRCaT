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


# Establish and format the installation directory. Some background things will be saved to the installation directory #
pth1 = os.path.dirname(os.path.realpath(__file__))
pth1 = os.path.join(str(pth1),'')
print(pth1)


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
                      +'generally known location for which you have video footage. If you have an issue, please post it on the GitHub issues page (https://github.com/conlin-matt/SurfRCaT/issues).')      
        txt2.setWordWrap(True)

        txt3 = QLabel('What would you like to do?')
        calibBut = QRadioButton('Calibrate a surfcam')
        rectifBut = QRadioButton('Rectify images (from already-calibrated camera)')

        rightGroupBox = QGroupBox()
        rightGroupBox1 = QGroupBox()
        rightGroupBox2 = QGroupBox()
        grd = QGridLayout()
        grd1 = QGridLayout()
        grd2 = QGridLayout()

        grd1.addWidget(txt,0,1,1,2)
        grd1.addWidget(txt2,1,0,1,4)
        rightGroupBox1.setLayout(grd1)
        grd2.addWidget(txt3,0,0,1,4)
        grd2.addWidget(calibBut,1,1,1,3)
        grd2.addWidget(rectifBut,2,1,1,3)
        rightGroupBox2.setLayout(grd2)
        grd.addWidget(rightGroupBox1,0,0,1,4)
        grd.addWidget(rightGroupBox2,1,0,1,4)
        rightGroupBox.setLayout(grd)

        # Connect widgets with signals #
        calibBut.clicked.connect(self.on_calibSelect)
        rectifBut.clicked.connect(self.on_rectifSelect)
        ################################

        # Full widget layout setup #
        fullLayout = QHBoxLayout()
        fullLayout.addWidget(leftGroupBox)
        fullLayout.addWidget(rightGroupBox)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        self.show()
        ###############################

    def on_calibSelect(self):
        
        self.close()
        self.w = StartCalibWindow()
        self.w.show()

    def on_rectifSelect(self):
        
        self.close()
        self.w = rectify_InputsWindow()
        self.w.show()



class StartCalibWindow(QWidget):
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
        txt = QLabel('Please establish a working directory for outputs to be saved to and/or loaded from (if they already exist):')
        txt.setWordWrap(True)
        fdBut = QPushButton('Browse')
        wdLab = QLabel('Working directory:')
        self.wdLine = QLineEdit()
        self.wdLine.setReadOnly(True)
        contBut = QPushButton('Continue >')
        backBut = QPushButton('< Back')

        rightGroupBox = QGroupBox()
        rightGroupBox1 = QGroupBox()        
        grd = QGridLayout()
        grd1 = QGridLayout()

        grd1.addWidget(txt,0,0,1,6)
        grd1.addWidget(wdLab,1,0,1,2)
        grd1.addWidget(self.wdLine,1,2,1,3)
        grd1.addWidget(fdBut,1,5,1,1)
        rightGroupBox1.setLayout(grd1)
        grd.addWidget(rightGroupBox1,0,0,1,6)
        grd.addWidget(backBut,1,0,1,2)
        grd.addWidget(contBut,1,4,1,2)
        rightGroupBox.setLayout(grd)

        ############################
        
        # Connect widgets with signals #
        fdBut.clicked.connect(self.getWD)
        backBut.clicked.connect(self.goBack)
        contBut.clicked.connect(self.startCalib)
        ################################
        
        # Full widget layout setup #
        fullLayout = QHBoxLayout()
        fullLayout.addWidget(leftGroupBox)
        fullLayout.addWidget(rightGroupBox)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        self.show()
        ###############################
        
        
    def getWD(self):
        global pth
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            direc = dlg.selectedFiles()
            self.direc = direc[0]
            pth = self.direc+'/'
            
            self.wdLine.setText(self.direc)
            
         
    def startCalib(self):
       '''
       Moves to the first window of the tool when Start is selected
       '''
       self.close()
       self.tool = ChooseCameraWindow()
       self.tool.show()
       
    def goBack(self):
        
        self.close()
        self.w = WelcomeWindow()
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
        self.ww = getImagery_GetWebCATImagery()  
        self.ww.show()
        
    def Other_select(self):
        '''
        If other-type selected, this function will open a new window (OtherCameraLocationInputWindow) to allow input of camera details
        '''
        self.close()
        self.www = getImagery_GetOtherImagery()
        self.www.show()       
##============================================================================##       


##============================================================================## 
# Get Imagery Module: Get the image to be used for the calibration #
##============================================================================##
class getImagery_GetWebCATImagery(QWidget):
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
       intro = QLabel('The Webcamera Application Testbed (WebCAT) is a network of 7 surfcams spanning the southeastern U.S. coastline. '+
                      'Live and historic feeds from the cameras are stored on servers and accessible in 10-minute video-clips. '+
                      'Live feeds from each camera can be viewed at https://secoora.org/webcat/, and a summary of available historic video from each camera '+
                      'can be found at http://webcat-video.axds.co/status/. If you wish to calibrate a WebCAT camera, please input the camera and '+
                      'desired imagery date below, and a video will be downloaded automatically. Note: only 4 of the 7 cameras can be calibrated '+
                      'via SurfRCaT; those are the only cameras available to select below.') 
       intro.setWordWrap(True)
       txt = QLabel('Select WebCAT camera:')
       opt = QComboBox()
       opt.addItem('--')
       opt.addItem('Folly Beach Pier (north)')
       opt.addItem('Folly Beach Pier (south)')
       opt.addItem('St. Augustine Pier')
       opt.addItem('Miami 40th Street')
       opt.setCurrentIndex(0)
       backBut = QPushButton('< Back')
       contBut = QPushButton('Continue >')
       lblDir1 = QLabel('Input desired imagery date below (in yyyy,mm,dd,HHHH format):')
       lblDir1.setWordWrap(True)
       self.bxYear = QLineEdit()
       self.bxMonth = QLineEdit()
       self.bxDay = QLineEdit()
       self.bxHour = QLineEdit()
       lblYear = QLabel('Year:')
       lblMonth = QLabel('Month:')
       lblDay = QLabel('Day:')
       lblHour = QLabel('Hour:')
       orLab = QLabel('Or')
     
       rightGroupBox = QGroupBox()
       rightGroupBox1 = QGroupBox()
       rightGroupBox2 = QGroupBox()
       self.grd = QGridLayout()
       grd1 = QGridLayout()
       grd2 = QGridLayout()
                      
       grd1.addWidget(txt,0,0,1,2)
       grd1.addWidget(opt,1,0,1,2)
       rightGroupBox1.setLayout(grd1)

       grd2.addWidget(lblDir1,0,0,1,4)
       grd2.addWidget(lblYear,1,0,1,2)
       grd2.addWidget(self.bxYear,1,2,1,2)              
       grd2.addWidget(lblMonth,2,0,1,2)
       grd2.addWidget(self.bxMonth,2,2,1,2) 
       grd2.addWidget(lblDay,3,0,1,2)
       grd2.addWidget(self.bxDay,3,2,1,2)
       grd2.addWidget(lblHour,4,0,1,2)
       grd2.addWidget(self.bxHour,4,2,1,2)
       grd2.addWidget(orLab,5,0,1,1)
       rightGroupBox2.setLayout(grd2)

       self.grd.addWidget(intro,0,0,4,4)
       self.grd.addWidget(rightGroupBox1,4,0,2,4)
       self.grd.addWidget(rightGroupBox2,6,0,4,4)
       self.grd.addWidget(backBut,10,0,1,2)
       self.grd.addWidget(contBut,10,2,1,2)
       rightGroupBox.setLayout(self.grd)

              
       # Connect widgets with signals #
       opt.activated.connect(self.getSelectedCam)
       backBut.clicked.connect(self.GoBack)
       contBut.clicked.connect(self.saveSelected)
       ################################

       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       self.show()
       ############################
        
        
    def getSelectedCam(self,item):

       WebCATdict = {'Placeholder':[0,0],
                    'follypiernorthcam':[32.654731,-79.939322],
                    'follypiersouthcam':[32.654645,-79.939597],
                    'staugustinecam':[29.856559,-81.265545],
                    'miami40thcam':[ 25.812227, -80.122400]}
      
       # Get location of selected camera #
       cams = ['Placeholder','follypiernorthcam','follypiersouthcam','staugustinecam','miami40thcam']
       self.cameraLocation = WebCATdict[cams[item]]
       self.cameraName = cams[item]

       # Add the pre-defined azimuth and elev for each WebCAT camera #
       if self.cameraName == 'follypiernorthcam':
           self.az = 150
           self.ZL = 15
       elif self.cameraName == 'follypiersouthcam':
           self.az = 150
           self.ZL = 15
       elif self.cameraName == 'staugustinecam':
           self.az = 80
           self.ZL = 10
       elif self.cameraName == 'miami40thcam':
           self.az = 60
           self.ZL = 40



           
    def saveSelected(self):
        
       global pth

       if os.path.exists(pth+'calibration_'+self.cameraName+'.'+self.bxYear.text()+'-'+self.bxMonth.text()+'-'+self.bxDay.text()+'_'+self.bxHour.text()) == 0:
           
           os.mkdir(pth+'calibration_'+self.cameraName+'.'+self.bxYear.text()+'-'+self.bxMonth.text()+'-'+self.bxDay.text()+'_'+self.bxHour.text())
           os.mkdir(pth+'calibration_'+self.cameraName+'.'+self.bxYear.text()+'-'+self.bxMonth.text()+'-'+self.bxDay.text()+'_'+self.bxHour.text()+'/_binaries')
           
           pth = pth+'calibration_'+self.cameraName+'.'+self.bxYear.text()+'-'+self.bxMonth.text()+'-'+self.bxDay.text()+'_'+self.bxHour.text()+'/'
           print(pth)
           
           # Save everything #
           with open(pth+'_binaries/CameraLocation.pkl','wb') as f:
               pickle.dump(self.cameraLocation,f)
           with open(pth+'_binaries/CameraName.pkl','wb') as f:
               pickle.dump(self.cameraName,f)
           with open(pth+'_binaries/az.pkl','wb') as f:
               pickle.dump(self.az,f)
           with open(pth+'_binaries/ZL.pkl','wb') as f:
               pickle.dump(self.ZL,f)

           camType = 1
           with open(pth+'_binaries/camType.pkl','wb') as f:
               pickle.dump(camType,f)

           self.downloadVid()
               
       else:        
           msg = QMessageBox(self)
           msg.setIcon(msg.Warning)
           msg.setText('A subdirectory for this video already exists in your working directory, making it appear that '+
                       'you are re-trying a calibration. If this is not true, please remove this subdirectory from your working directory or rename it. If it is, '+
                       ' do you want to use the same calibration image as before (select No if you do not have images yet)?')
           msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
           msg.buttonClicked.connect(self.onMsgBoxClick)
           msg.show()
           
           
    def onMsgBoxClick(self,i):

        global pth
        
        if i.text() == '&Yes':
 
            pth = pth+'calibration_'+self.cameraName+'.'+self.bxYear.text()+'-'+self.bxMonth.text()+'-'+self.bxDay.text()+'_'+self.bxHour.text()+'/'

            self.worker = getLidar_WebCATThread()
            self.worker.start()
            self.worker.finishSignal.connect(self.skipToLidar)

        elif i.text() == '&No':

            pth = pth+'calibration_'+self.cameraName+'.'+self.bxYear.text()+'-'+self.bxMonth.text()+'-'+self.bxDay.text()+'_'+self.bxHour.text()+'/'

            if os.path.exists(pth+'frames'):
                self.close()
                self.w = getImagery_ChooseFrameWindow()
                self.w.show()
            else:
                files = os.listdir(pth)
                vid = [i for i in files if self.cameraName in i]
                pthToVid = pth+vid[0]
                
                self.close()
                self.w = getImagery_VideoDecimatorWindow(pthToVid)
                self.w.show()


    
    def downloadVid(self):   

       self.yr = int(self.bxYear.text())
       self.mo = int(self.bxMonth.text())
       self.day = int(self.bxDay.text())
       self.hour = int(self.bxHour.text())

       # Instantiate worker threads #
       self.worker = DownloadVidThread(self.yr,self.mo,self.day,self.hour)
         
       lab1 = QLabel('Downloading Video...')
       self.grd.addWidget(lab1,11,0,1,1)

       self.loadlab = QLabel()
       self.loadmovie = QMovie(pth1+'loading.gif')
       self.loadlab.setMovie(self.loadmovie)
       
       self.worker.start()
       self.grd.addWidget(self.loadlab,11,1,1,1)
       self.loadmovie.start()
       self.worker.finishSignal.connect(self.on_closeSignal)
       

    def on_closeSignal(self):
         
       '''
       When download video thread is done, function shows a done label and moves on
       '''
       files = os.listdir(pth)
       vid = [i for i in files if self.bxYear.text() in i and self.bxMonth.text() in i and self.bxDay.text() in i and self.bxHour.text() in i]
       self.pthToVid = pth+vid[0]
       
       self.loadlab.setParent(None)
       self.loadmovie.stop()
       labDone = QLabel('Done.')
       self.grd.addWidget(labDone,11,1,1,1)


       self.worker2 = getLidar_WebCATThread()
         
       lab1 = QLabel('Cleaning up...')
       self.grd.addWidget(lab1,12,0,1,1)

       self.loadlab = QLabel()
       self.loadmovie = QMovie(pth1+'loading.gif')
       self.loadlab.setMovie(self.loadmovie)
       
       self.worker2.start()
       self.grd.addWidget(self.loadlab,12,1,1,1)
       self.loadmovie.start()
       self.worker2.finishSignal.connect(self.on_closeSignal2)

    def on_closeSignal2(self):
        
       self.loadlab.setParent(None)
       self.loadmovie.stop()
       labDone = QLabel('Done.')
       self.grd.addWidget(labDone,12,1,1,1)

       os.mkdir(pth+'frames')
       saveDir = pth+'frames'

       self.close()
       self.w = getImagery_VideoDecimatorWindow(self.pthToVid,saveDir)
       self.w.show()
       

    def skipToLidar(self):

       if os.path.exists(pth+'lidarPC.pkl'):
           msg = QMessageBox(self)
           msg.setIcon(QMessageBox.Information)
           txt = ('Exisiting lidar point cloud for this camera found. Do you want to use it? \n' +
                  'WARNING: The lidar point cloud has coordinates relative to the input camera location. If you have changed the input '+
                  'location of this camera since the point cloud was created, you need to create a new one.')
           msg.setText(txt)
           msg.setWindowTitle('Error')
           msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
           msg.buttonClicked.connect(self.onMsgBoxClick)
           msg.show()
       else:
           f = open(pth+'lidarTable.pkl','rb')
           lidarTable = pickle.load(f)

           self.close()
           self.lw = getLidar_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
           self.lw.resize(900,350)
           self.lw.show()
         
    def onMsgBoxClick(self,i):
       
       if i.text() == '&Yes':
            
           self.close()
           self.w = PickGCPsWindow()
           self.w.show()
       else:
           f = open(pth+'lidarTable.pkl','rb')
           lidarTable = pickle.load(f)

           self.close()
           self.lw = getLidar_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
           self.lw.resize(900,350)
           self.lw.show()
           

    def GoBack(self):
       '''
       Function goes back to previous window when Back button is clicked
       '''
       self.close()
       self.backToOne = ChooseCameraWindow()



class getImagery_GetOtherImagery(QWidget):
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
       lblDir = QLabel('Input the approximate location (WGS 84 lat/lon) of the camera below:')
       lblLat = QLabel('Camera Latitude (decimal degrees):')
       lblLon = QLabel('Camera Longitude (decimal degrees):')
       lblElev = QLabel('Elevation (NAVD88 m):')
       lblAz = QLabel('Azimuth (degrees):')
       self.bxLat = QLineEdit()
       self.bxLon = QLineEdit()
       self.bxElev = QLineEdit()
       self.bxAz = QLineEdit()
       self.azHelpBut = QPushButton('?')
       lblPth = QLabel('Use the button below to select the video from your camera (.mp4 format):')
       lblPth.setWordWrap(True)
       browseBut = QPushButton('Browse')
       self.bxPth = QLineEdit()
       backBut = QPushButton('< Back')
       contBut = QPushButton('Continue >')

       rightGroupBox = QGroupBox()
       rightGroupBox1 = QGroupBox()
       rightGroupBox2 = QGroupBox()
       rightGroupBox3 = QGroupBox()
       grd = QGridLayout()
       grd1 = QGridLayout()
       grd2 = QGridLayout()
       grd3 = QGridLayout()
       grd1.addWidget(lblDir1,0,0,1,3)
       grd1.addWidget(self.bxName,0,3,1,3)
       rightGroupBox1.setLayout(grd1)
       grd2.addWidget(lblDir,0,0,1,6)
       grd2.addWidget(lblLat,1,1,1,3)
       grd2.addWidget(self.bxLat,1,4,1,2)
       grd2.addWidget(lblLon,2,1,1,3)
       grd2.addWidget(self.bxLon,2,4,1,2)
       grd2.addWidget(lblElev,3,1,1,3)
       grd2.addWidget(self.bxElev,3,4,1,2)
       grd2.addWidget(self.azHelpBut,4,0,1,1)
       grd2.addWidget(lblAz,4,1,1,3)
       grd2.addWidget(self.bxAz,4,4,1,2)
       rightGroupBox2.setLayout(grd2)
       grd3.addWidget(lblPth,0,0,1,6)
       grd3.addWidget(browseBut,1,0,1,2)
       grd3.addWidget(self.bxPth,1,2,1,4)
       rightGroupBox3.setLayout(grd3)
       grd.addWidget(rightGroupBox1,0,0,2,6)
       grd.addWidget(rightGroupBox2,2,0,4,6)
       grd.addWidget(rightGroupBox3,6,0,2,6)
       grd.addWidget(backBut,8,0,1,2)
       grd.addWidget(contBut,8,4,1,2)
       grd.setAlignment(Qt.AlignCenter)
       rightGroupBox.setLayout(grd)
       ##############################
       
       # Assign signals to widgets #
       browseBut.clicked.connect(self.onBrowseClick)
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

    def onBrowseClick(self):
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.ExistingFile)
       if dlg.exec_():
           file = dlg.selectedFiles()
           self.file = file[0]
            
           self.bxPth.setText(self.file)
        
       
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
       
       global pth
       
       cameraName = self.bxName.text()
       if cameraName == '':
           msg = QMessageBox(self)
           msg.setIcon(msg.Question)
           msg.setText('Please input a name for the camera.')
           msg.setStandardButtons(msg.Ok)
           msg.show()
           
       try:
           cameraLocation = [float(self.bxLat.text()),float(self.bxLon.text())]
           az = float(self.bxAz.text())     
           ZL = float(self.bxElev.text())
       except ValueError:
           msg = QMessageBox(self)
           msg.setIcon(msg.Question)
           msg.setText('Please input numeric values for camera parameters.')
           msg.setStandardButtons(msg.Ok)
           msg.show()
           

       fileName = self.file.split('/')[len(self.file.split('/'))-1]
       self.fileName_NoExt = os.path.splitext(fileName)[0]

       if os.path.exists(pth+'calibration_'+self.fileName_NoExt) == 0:
            os.mkdir(pth+'calibration_'+self.fileName_NoExt)
            os.mkdir(pth+'calibration_'+self.fileName_NoExt+'/_binaries')
            pth = pth+'calibration_'+self.fileName_NoExt+'/'


            # Save the camera name and location #
            with open(pth+'_binaries/CameraLocation.pkl','wb') as f:
                pickle.dump(cameraLocation,f)
            with open(pth+'_binaries/CameraName.pkl','wb') as f:
                pickle.dump(cameraName,f)
            with open(pth+'_binaries/az.pkl','wb') as f:
                pickle.dump(az,f)
            with open(pth+'_binaries/ZL.pkl','wb') as f:
                pickle.dump(ZL,f)
            with open(pth+'_binaries/VidOrImage.pkl','wb') as f:
                pickle.dump(self.file,f)

            camType = 0
            with open(pth+'_binaries/camType.pkl','wb') as f:
                pickle.dump(camType,f)
               
            os.mkdir(pth+'frames')
            saveDir = pth+'frames'

            self.close()
            self.d = getImagery_VideoDecimatorWindow(self.file,saveDir)
            self.d.show()

            
       else:
            msg = QMessageBox(self)
            msg.setIcon(msg.Warning)
            msg.setText('A subdirectory for this video already exists in your working directory, making it appear that '+
                       'you are re-trying a calibration. If this is not true, please remove this subdirectory from your working directory or rename it. If it is, '+
                       ' do you want to use the same calibration image as before?')
            msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            msg.buttonClicked.connect(self.onMsgBoxClick)
            msg.show()
           
           
    def onMsgBoxClick(self,i):

        global pth
        
        if i.text() == '&Yes':
 
            pth = pth+'calibration_'+self.fileName_NoExt+'/'

            self.close()
            self.ls = getLidar_FindUseableDatasetsWindow()
            self.ls.show()

        elif i.text() == '&No':

            pth = pth+'calibration_'+self.fileName_NoExt+'/'
            
            self.close()
            self.w = getImagery_ChooseFrameWindow()
            self.w.show()
            
                     
         

class getImagery_VideoDecimatorWindow(QWidget):
    
    def __init__(self,pthToVid,saveDir,fromRectifWindow=None):

       self.vid = pthToVid
       self.saveDir = saveDir
       if fromRectifWindow:
           self.fromRectifWindow = 1
       else:
           self.fromRectifWindow = None
       
       super().__init__()    
        
       if not QApplication.instance():
           app = QApplication(sys.argv)
       else:
           app = QApplication.instance()             
       self.initUI()
        
    def initUI(self):

       cap = cv2.VideoCapture(self.vid)
       numFrames = int(cap.get(7))
       self.fps = cap.get(5)
       self.vidLen = int(numFrames/self.fps)
       
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
       labName = QLabel('Video name:')
       txtName = QLabel(self.vid.split('/')[len(self.vid.split('/'))-1])
       labLen = QLabel('Video duration:')
       txtLen = QLabel(str(self.vidLen)+' sec')
       labFrames = QLabel('Video frames:')
       txtFrames = QLabel(str(numFrames))
       labDir = QLabel('Input your desired decimation rate or number of frames (evenly spaced) below and click Go to begin the video decimation. The frames will be saved to a new subdirectory '+
              'in your working directory.')
       labDir.setWordWrap(True)
       labDec = QLabel('Decimation rate:')
       unitDec = QLabel('frames/second')
       self.bxDec = QLineEdit()
       orLab = QLabel('Or')
       labTotalFrames = QLabel('Number of frames:')
       self.bxTotalFrames = QLineEdit()
       numFramesExt = 0
       self.labNumFrames = QLabel(str(numFramesExt)+' frames will be saved')
       updateBut = QPushButton('Update')
       goBut = QPushButton('Go')
       backBut = QPushButton('Back')
                        

       rightGroupBox = QGroupBox()
       rightGroupBox1 = QGroupBox()
       rightGroupBox2 = QGroupBox()
       self.grd = QGridLayout()
       grd1 = QGridLayout()
       self.grd2 = QGridLayout()
       grd1.addWidget(labName,0,0,1,2)
       grd1.addWidget(txtName,0,2,1,4)
       grd1.addWidget(labLen,1,0,1,2)
       grd1.addWidget(txtLen,1,2,1,4)
       grd1.addWidget(labFrames,2,0,1,2)
       grd1.addWidget(txtFrames,2,2,1,4)
       rightGroupBox1.setLayout(grd1)
       self.grd2.addWidget(labDir,0,0,2,6)
       self.grd2.addWidget(labDec,2,0,1,1)
       self.grd2.addWidget(self.bxDec,2,1,1,1)
       self.grd2.addWidget(unitDec,2,2,1,1)
       self.grd2.addWidget(updateBut,3,0,1,1)
       self.grd2.addWidget(self.labNumFrames,3,1,1,2)
       self.grd2.addWidget(orLab,4,0,1,1)
       self.grd2.addWidget(labTotalFrames,5,0,1,1)
       self.grd2.addWidget(self.bxTotalFrames,5,1,1,1)
       rightGroupBox2.setLayout(self.grd2)
       self.grd.addWidget(rightGroupBox1,0,0,3,6)
       self.grd.addWidget(rightGroupBox2,3,0,4,6)
       self.grd.addWidget(backBut,8,0,1,2)
       self.grd.addWidget(goBut,8,4,1,2)
       rightGroupBox.setLayout(self.grd)


       # Assign signals to widgets #
       updateBut.clicked.connect(self.onUpdateClick)
       goBut.clicked.connect(self.onGoClick)
       #############################

       
       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       self.show()
       ############################       


    def onUpdateClick(self):
        rate = self.bxDec.text()

        try:
           rate = int(rate)
           
           self.labNumFrames.setParent(None)
           
           num = self.vidLen*rate

           self.labNumFrames = QLabel(str(int(num))+' frames will be saved')
           
           self.grd2.addWidget(self.labNumFrames,3,1,1,2)
            
        except ValueError:
           msg = QMessageBox(self)
           msg.setIcon(QMessageBox.Critical)
           txt = ('Please input an integer value.')
           msg.setText(txt)
           msg.setWindowTitle('Error')
           msg.setStandardButtons(QMessageBox.Ok)
           msg.show()

    def onGoClick(self):
        rate = self.bxDec.text()
        num = self.bxTotalFrames.text()
        

        if rate != '' and num != '': # If inputs to both fields are given, throw an error message #          
           msg = QMessageBox(self)
           msg.setIcon(QMessageBox.Critical)
           txt = ('Please either input a decimation rate or number of frames, not both.')
           msg.setText(txt)
           msg.setWindowTitle('Error')
           msg.setStandardButtons(QMessageBox.Ok)
           msg.show()
        elif rate != '' and num == '': # If a number of frames is given but not rate, decimate based on the input number of frames #
            self.worker = DecimateVidThread(self.vid,int(rate),0,self.vidLen,self.fps,self.saveDir)

            lab1 = QLabel('Extracting frames...')
            self.grd.addWidget(lab1,9,0,1,2)

            self.loadlab = QLabel()
            self.loadmovie = QMovie(pth1+'loading.gif')
            self.loadlab.setMovie(self.loadmovie)
         
            self.worker.start()
            self.grd.addWidget(self.loadlab,9,2,1,1)
            self.loadmovie.start()
  
            self.worker.finishSignal.connect(self.onFinishSignal)
        elif rate == '' and num != '': # If a rate is given but not a number of frames decimate based on the input rate #
            self.worker = DecimateVidThread(self.vid,0,int(num),self.vidLen,self.fps,self.saveDir)

            lab1 = QLabel('Extracting frames...')
            self.grd.addWidget(lab1,9,0,1,2)

            self.loadlab = QLabel()
            self.loadmovie = QMovie(pth1+'loading.gif')
            self.loadlab.setMovie(self.loadmovie)
         
            self.worker.start()
            self.grd.addWidget(self.loadlab,9,2,1,1)
            self.loadmovie.start()
  
            self.worker.finishSignal.connect(self.onFinishSignal)
        else:
           msg = QMessageBox(self)
           msg.setIcon(QMessageBox.Critical)
           txt = ('An error occured.')
           msg.setText(txt)
           msg.setWindowTitle('Error')
           msg.setStandardButtons(QMessageBox.Ok)
           msg.show()

    def onFinishSignal(self):

        self.loadlab.setParent(None)
        self.loadmovie.stop()
        labDone = QLabel('Done.')
        self.grd.addWidget(labDone,9,2,1,1)

        if self.fromRectifWindow is not None:
            self.close()
        else:
            self.close()
            self.w = getImagery_ChooseFrameWindow()
            self.w.show()


       
class getImagery_ChooseFrameWindow(QWidget):
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

       txt = QLabel('Choose a frame to use for the calibration by scrolling through extracted frames with the arrow buttons. Press Continue when '+
                    'your desired frame is displayed.')
       txt.setWordWrap(True)
       self.forward = QPushButton('->')
       self.back = QPushButton('<-')
       self.back.setEnabled(False)
       contBut = QPushButton('Continue >')
       backBut = QPushButton('< Back')

       
       self.grd = QGridLayout()
       self.grd.addWidget(txt,0,0,1,6)
       self.grd.addWidget(self.forward,5,3,1,1)
       self.grd.addWidget(self.back,5,0,1,1)
       self.grd.addWidget(backBut,6,1,1,1)
       self.grd.addWidget(contBut,6,2,1,1)

       # Display the first frame #
       self.frames = os.listdir(pth+'frames/') 

       self.frame = 0
        
       img = mpimg.imread(pth+'frames/'+self.frames[self.frame])
       self.canvas = FigureCanvas(Figure())
       self.ax = self.canvas.figure.subplots()
       self.ax.imshow(img)
       self.canvas.draw()
          
       self.grd.addWidget(self.canvas,1,0,4,4)
              
       self.rightGroupBox.setLayout(self.grd)
       ########################################
       
       # Connect widgets with signals #
       self.forward.clicked.connect(self.onForwardClick)
       self.back.clicked.connect(self.onBackClick)
       contBut.clicked.connect(self.onContClick)
       backBut.clicked.connect(self.onBackButClick)
       ################################

       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(self.rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       self.show()
       ############################

    def onForwardClick(self):
       self.back.setEnabled(True)

       if self.frame<len(self.frames)-1:
           self.frame = self.frame+1

           img = mpimg.imread(pth+'frames/'+self.frames[self.frame])
           self.canvas = FigureCanvas(Figure())
           self.ax = self.canvas.figure.subplots()
           self.ax.imshow(img)
           self.canvas.draw()
          
           self.grd.addWidget(self.canvas,1,0,4,4)
           
       else:
           self.forward.setEnabled(False)


    def onBackClick(self):
       self.forward.setEnabled(True)

       if self.frame>0:
           self.frame = self.frame-1

           img = mpimg.imread(pth+'frames/'+self.frames[self.frame])
           self.canvas = FigureCanvas(Figure())
           self.ax = self.canvas.figure.subplots()
           self.ax.imshow(img)
           self.canvas.draw()
              
           self.grd.addWidget(self.canvas,1,0,4,4)
       else:
           self.back.setEnabled(False)


    def onContClick(self):
        
        frameNumSel = self.frame
        img = cv2.imread(pth+'frames/'+self.frames[frameNumSel])
        cv2.imwrite(pth+'calibrationImage.png',img)

        f = open(pth+'_binaries/camType.pkl','rb')
        camType = pickle.load(f)
        if camType == 0: # Not WebCAT #
            self.close()
            self.w = getLidar_FindUseableDatasetsWindow()
            self.w.show()
        else: # WebCAT #
            
            if os.path.exists(pth+'_binaries/lidarPC.pkl'):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                txt = ('Exisiting lidar point cloud for this camera found. Do you want to use it? \n' +
                  'WARNING: The lidar point cloud has coordinates relative to the input camera location. If you have changed the input '+
                  'location of this camera since the point cloud was created, you need to create a new one.')
                msg.setText(txt)
                msg.setWindowTitle('Error')
                msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
                msg.buttonClicked.connect(self.onMsgBoxClick)
                msg.show()
            else:
                f = open(pth+'_binaries/lidarTable.pkl','rb')
                lidarTable = pickle.load(f)

                self.close()
                self.lw = getLidar_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
                self.lw.resize(900,350)
                self.lw.show()
         
    def onMsgBoxClick(self,i):
       
       if i.text() == '&Yes':
            
           self.close()
           self.w = PickGCPsWindow()
           self.w.show()
       else:
           f = open(pth+'_binaries/lidarTable.pkl','rb')
           lidarTable = pickle.load(f)

           self.close()
           self.lw = getLidar_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
           self.lw.resize(900,350)
           self.lw.show()


    def onBackButClick(self):

        global pth
        pth = pth.rsplit('/',2)[0]+'/'
        
        self.close()
        self.ww = ChooseCameraWindow()  
        self.ww.show()


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
        
       rightGroupBox = QGroupBox()
       self.grd = QGridLayout()
       self.grd.addWidget(self.lab1,0,0,1,4)
       
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

       if os.path.exists(pth+'_binaries/lidarPC.pkl'):
           msg = QMessageBox(self)
           msg.setIcon(QMessageBox.Information)
           txt = ('Exisiting lidar point cloud for this camera found. Do you want to use it? \n' +
                  'WARNING: The lidar point cloud has coordinates relative to the input camera location. If you have changed the input '+
                  'location of this camera since the point cloud was created, you need to create a new one.')
           msg.setText(txt)
           msg.setWindowTitle('Error')
           msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
           msg.buttonClicked.connect(self.onMsgBoxClick)
           msg.show()

       else:  
           # Instantiate worker threads #
           f = open(pth+'_binaries/CameraLocation.pkl','rb')
           cameraLocation = pickle.load(f)

           self.worker1 = getLidar_FindCloseDatasetIDsThread(cameraLocation[0],cameraLocation[1])
           self.worker1.finishSignal.connect(self.on_closeSignal1)
           self.worker = getLidar_FindCoveringDatasetsThread(cameraLocation[0],cameraLocation[1])
           self.worker.threadSignal.connect(self.on_threadSignal)
           self.worker.finishSignal.connect(self.on_closeSignal)
           self.worker.badSignal.connect(self.on_badSignal)

           self.loadlab = QLabel()
           self.loadmovie = QMovie(pth1+'loading.gif')
           self.loadlab.setMovie(self.loadmovie)
           
           self.worker1.start()
           self.grd.addWidget(self.loadlab,0,4,1,4)
           self.loadmovie.start()
       
       ##############################
       
     def onMsgBoxClick(self,i):
       
        if i.text() == '&Yes':
            
            self.close()
            self.w = PickGCPsWindow()
            self.w.show()
            
        else:
            # Instantiate worker threads #
            f = open(pth+'_binaries/CameraLocation.pkl','rb')
            cameraLocation = pickle.load(f)

            self.worker1 = getLidar_FindCloseDatasetIDsThread(cameraLocation[0],cameraLocation[1])
            self.worker1.finishSignal.connect(self.on_closeSignal1)
            self.worker = getLidar_FindCoveringDatasetsThread(cameraLocation[0],cameraLocation[1])
            self.worker.threadSignal.connect(self.on_threadSignal)
            self.worker.finishSignal.connect(self.on_closeSignal)
            self.worker.badSignal.connect(self.on_badSignal)

            self.loadlab = QLabel()
            self.loadmovie = QMovie(pth1+'loading.gif')
            self.loadlab.setMovie(self.loadmovie)
           
            self.worker1.start()
            self.grd.addWidget(self.loadlab,0,4,1,4)
            self.loadmovie.start()


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
         
         f = open(pth+'_binaries/lidarTable.pkl','rb')
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
        f = open(pth+'_binaries/CameraLocation.pkl','rb')
        cameraLocation = pickle.load(f)
        
        self.worker = getLidar_PrepChosenSetThread(cameraLocation[0],cameraLocation[1])
        self.worker.threadSignal.connect(self.on_threadSignal)
        
        self.worker2 = getLidar_DownloadChosenSetThread(cameraLocation[0],cameraLocation[1])
        self.worker2.threadSignal.connect(self.on_threadSignal2)
        
        self.worker3 = getLidar_FormatChosenSetThread(cameraLocation[0],cameraLocation[1])
        ##############################
        


    def onMsgBoxClick(self,i):
        if i.text() == '&Yes':
            
            self.close()
            self.nextWindow = PickGCPsWindow()
            
        elif i.text() == '&No':
            pass
             
        
    def dataChoice(self,item):
        '''
        Save user's choice of dataset.
        '''
        
        print(str(item.text())) 
        
        num = int(item.text())
        with open(pth+'_binaries/chosenLidarID.pkl','wb') as f:
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
        
        f = open(pth+'_binaries/lidarDat.pkl','rb')
        ld = pickle.load(f)
        if len(ld>0):
        
            lab3 = QLabel('Creating data point cloud...')
        
            self.layout.addWidget(lab3,8,0,1,2)

            self.loadlab = QLabel()
            self.loadmovie = QMovie(pth1+'loading.gif')
            self.loadlab.setMovie(self.loadmovie)
        
            self.worker3.start()
            self.layout.addWidget(self.loadlab,8,2,1,2)
            self.loadmovie.start()
            self.worker3.finishSignal.connect(self.on_closeSignal3)
        else: 
            msg = QMessageBox(self)
            msg.setIcon(msg.Warning)
            msg.setText('No lidar observations from this dataset were found near the camera. Please press OK to choose a different dataset. ')
            msg.setStandardButtons(msg.Ok)
            msg.show()
            msg.buttonClicked.connect(self.chooseOtherSet)
            
    def chooseOtherSet(self):
        '''
        Allow the user to re-choose a dataset.
        '''
        
        self.close()
        
        f = open(pth+'_binaries/lidarTable.pkl','rb')
        lidarTable = pickle.load(f)
         
        self.lw = getLidar_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
        self.lw.show()
         
        
    def on_closeSignal3(self):
        '''
        Finish when point cloud is created.
        '''
        time.sleep(10) # Let the computer rest for 10 seconds here. This helps to avaoid what seems to be memory swap issues that cause the pptk window in the next step to open very slowly. #
        
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
        img = mpimg.imread(pth+'calibrationImage.png')
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
        self.worker.badSignal.connect(self.on_badSignal)
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

       self.loadlab = QLabel()
       self.loadmovie = QMovie(pth1+'loading.gif')
       self.loadlab.setMovie(self.loadmovie)
       
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
       self.grd.addWidget(self.loadlab,7,3,1,1)
       self.loadmovie.start()



                          
   def on_CloseSignal(self):
       '''
       Start the image picking process.
       '''

       self.dirLab.setParent(None)
       self.loadlab.setParent(None)

       self.dirLab2 = QLabel('Real-world coordinates of points saved! Now, click on the points (in the same order) in the image. Press Done when finished.')
       self.dirLab2.setWordWrap(True)
       self.doneBut = QPushButton('Done')

       self.grd.addWidget(self.dirLab2,0,0,1,4)
       self.grd.addWidget(self.doneBut,7,3,1,1)

       self.doneBut.clicked.connect(self.on_DoneClick)

       # Launch the image GCP picking process #
       self.worker2.start()
 
   def on_badSignal(self):
       
       msg = QMessageBox(self)
       msg.setIcon(msg.Critical)
       msg.setText('An error occured. Please identify your GCPs again.')
       msg.setStandardButtons(msg.Ok)
       msg.buttonClicked.connect(self.onOkClick)
       msg.show()    


   def onOkClick(self):
       self.close()
       self.w = PickGCPsWindow()
       self.w.show()
       
   def onHelpClick(self):
       '''
       Show help if needed.
       '''
       
       msg = QMessageBox(self)
       msg.setIcon(msg.Question)
       msg.setText('The lidar point cloud will open in a seperate window. The viewer can be navigated by (1) rotating the view (left click+drag), (2) '+
                   'panning (hold Shift and left click+drag), and (3) zooming (scroll wheel). Manipulate the view until you can identify the same features '+
                   'as in the image. Then, select your GCPs by: \n (1) Hold Control and left click on a point \n (2) Release Control and wait at least 3 seconds \n '+
                   '(3) Right click anywhere in the viewer \n (4) Repeat 1-3 for each GCP. \n Remember the order of the points you select.')
       msg.setStandardButtons(msg.Ok)
       msg.show()
       
               
   def on_DoneClick(self):
       '''
       Save the GCPs and display them to the user.
       '''
       
       self.dirLab2.setParent(None)
       self.doneBut.setParent(None)
       self.helpBut.setParent(None)       
    
       with open(pth+'_binaries/GCPs_im.pkl','rb') as f:
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
        img = mpimg.imread(pth+'calibrationImage.png')
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
        img = mpimg.imread(pth+'calibrationImage.png')
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.imshow(img)
        self.canvas.draw()
        
        # Plot the GCPs and reprojected positions #
        f1 = open(pth+'_binaries/GCPs_im.pkl','rb') 
        f2 = open(pth+'_binaries/GCPs_lidar.pkl','rb') 
        f3 = open(pth+'_binaries/calibVals.pkl','rb') 
       
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
        introLab = QLabel('Welcome to the rectification module! Here you can produce rectified image(s) from your camera using previously-obtained '+
                          'calibration results.')
        introLab.setWordWrap(True)
        introLab1 = QLabel('If you want to rectify frames extracted from a surfcam video, input the video file and directory to save the frames to here. '+
                           'If you already have frames, you can skip this step.')
        introLab1.setWordWrap(True)
        vidLab = QLabel('Video file:')
        self.vidBx = QLineEdit()
        browseBut0 = QPushButton('Browse')
        saveLab = QLabel('Drectory to save frames:')
        self.saveBx = QLineEdit()
        browseBut00 = QPushButton('Browse')
        extractStillsBut = QPushButton('Extract Frames')
        dirLab1 = QLabel('Calibration results file:')
        dirLab2 = QLabel('Input image directory:')
        dirLab3 = QLabel('Save directory:')
        self.calibFileBx = QLineEdit()
        self.calibFileBx.setReadOnly(True)
        self.inputDirecBx = QLineEdit()
        self.inputDirecBx.setReadOnly(True)
        self.saveDirecBx = QLineEdit()
        self.saveDirecBx.setReadOnly(True)
        browseBut1 = QPushButton('Browse')
        browseBut2 = QPushButton('Browse')
        browseBut3 = QPushButton('Browse')
        introLab2 = QLabel('Real-world grid (x,y relative to camera location):')
        introLab2.setWordWrap(True)
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
        backBut = QPushButton('< Back')
        
        self.rightGroupBox = QGroupBox()
        self.rightGroupBox1 = QGroupBox('Step 1')
        self.rightGroupBox2 = QGroupBox('Step 2')
        self.grd = QGridLayout()
        self.grd1 = QGridLayout()
        self.grd2 = QGridLayout()

        self.grd1.addWidget(introLab1,0,0,1,6)
        self.grd1.addWidget(vidLab,1,0,1,1)
        self.grd1.addWidget(self.vidBx,1,1,1,4)
        self.grd1.addWidget(browseBut0,1,5,1,1)
        self.grd1.addWidget(saveLab,2,0,1,1)
        self.grd1.addWidget(self.saveBx,2,1,1,4)
        self.grd1.addWidget(browseBut00,2,5,1,1)
        self.grd1.addWidget(extractStillsBut,3,2,1,2)
        self.rightGroupBox1.setLayout(self.grd1)
        self.grd2.addWidget(dirLab1,0,0,1,2)
        self.grd2.addWidget(self.calibFileBx,0,2,1,3)
        self.grd2.addWidget(browseBut1,0,5,1,1)
        self.grd2.addWidget(dirLab2,1,0,1,2)
        self.grd2.addWidget(self.inputDirecBx,1,2,1,3)
        self.grd2.addWidget(browseBut2,1,5,1,1)
        self.grd2.addWidget(dirLab3,2,0,1,2)
        self.grd2.addWidget(self.saveDirecBx,2,2,1,3)
        self.grd2.addWidget(browseBut3,2,5,1,1)
        self.grd2.addWidget(introLab2,3,0,2,6)
        self.grd2.addWidget(xminLab,5,0,1,2)
        self.grd2.addWidget(self.xminBx,5,2,1,4)
        self.grd2.addWidget(xmaxLab,6,0,1,2)
        self.grd2.addWidget(self.xmaxBx,6,2,1,4)
        self.grd2.addWidget(dxLab,7,0,1,2)
        self.grd2.addWidget(self.dxBx,7,2,1,4)
        self.grd2.addWidget(yminLab,8,0,1,2)
        self.grd2.addWidget(self.yminBx,8,2,1,4)
        self.grd2.addWidget(ymaxLab,9,0,1,2)
        self.grd2.addWidget(self.ymaxBx,9,2,1,4)
        self.grd2.addWidget(dyLab,10,0,1,2)
        self.grd2.addWidget(self.dyBx,10,2,1,4)
        self.grd2.addWidget(zLab,11,0,1,2)
        self.grd2.addWidget(self.zBx,11,2,1,4)
        self.rightGroupBox2.setLayout(self.grd2)
        self.grd.addWidget(introLab,0,0,3,4)
        self.grd.addWidget(self.rightGroupBox1,3,0,2,4)
        self.grd.addWidget(self.rightGroupBox2,5,0,9,4)
        self.grd.addWidget(backBut,14,0,1,1)
        self.grd.addWidget(contBut,14,3,1,1)
        self.grd.setAlignment(Qt.AlignCenter)
        self.rightGroupBox.setLayout(self.grd)

        # Connect widgets with signals #
        browseBut0.clicked.connect(self.onBrowse0Click)
        browseBut00.clicked.connect(self.onBrowse00Click)
        extractStillsBut.clicked.connect(self.onDecimateClick)
        browseBut1.clicked.connect(self.onBrowse1Click)
        browseBut2.clicked.connect(self.onBrowse2Click)
        browseBut3.clicked.connect(self.onBrowse3Click)
        self.browsePresses = 0
        backBut.clicked.connect(self.onBackClick)
        contBut.clicked.connect(self.onContClick)
        ################################

        # Full widget layout setup #
        fullLayout = QHBoxLayout()
        fullLayout.addWidget(leftGroupBox)
        fullLayout.addWidget(self.rightGroupBox)
        self.setLayout(fullLayout)
        self.setWindowTitle('SurfRCaT')
        self.show()
        ############################

   def onBrowse00Click(self):
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.Directory)
       if dlg.exec_():
           direc = dlg.selectedFiles()
           self.frameSaveDirec = direc[0]
            
           self.saveBx.setText(self.frameSaveDirec)
           

   def onBrowse0Click(self):
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.ExistingFile)
       if dlg.exec_():
           file = dlg.selectedFiles()
           self.vidFile = file[0]
            
           self.vidBx.setText(self.vidFile)

   def onDecimateClick(self):

       os.mkdir(self.frameSaveDirec+'/frames')
       saveDir = self.frameSaveDirec+'/frames'
       
       self.inputDirec = saveDir
       self.inputDirecBx.setText(self.inputDirec)
       self.browsePresses +=1
       
       self.w = getImagery_VideoDecimatorWindow(self.vidFile,saveDir,1)
       self.w.show()

   def onBrowse1Click(self):
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.ExistingFile)
       if dlg.exec_():
           file = dlg.selectedFiles()
           self.calibFile = file[0]
            
           self.calibFileBx.setText(self.calibFile)
           self.browsePresses += 1

   def onBrowse2Click(self):
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.Directory)
       if dlg.exec_():
           direc = dlg.selectedFiles()
           self.inputDirec = direc[0]
            
           self.inputDirecBx.setText(self.inputDirec)
           self.browsePresses += 1

   def onBrowse3Click(self):
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.Directory)
       if dlg.exec_():
           direc = dlg.selectedFiles()
           self.outputDirec = direc[0]
            
           self.saveDirecBx.setText(self.outputDirec)
           self.browsePresses += 1
           

   def onBackClick(self):
       self.close()
       self.w = WelcomeWindow()
       self.w.show()
       

   def onContClick(self):
        '''
        Get all user inputs on button click.
        '''

        # Acquire all the inputs #
        xmin = self.xminBx.text()
        xmax = self.xmaxBx.text()
        dx = self.dxBx.text()
        ymin = self.yminBx.text()
        ymax = self.ymaxBx.text()
        dy = self.dyBx.text()
        z = self.zBx.text()

        if self.browsePresses<3 or self.xminBx.text()=='' or self.xmaxBx.text()=='' or self.dxBx.text()==''  or self.yminBx.text()=='' or self.ymaxBx.text()=='' or self.dyBx.text()=='' or self.zBx.text()=='':
            msg = QMessageBox(self)
            msg.setIcon(msg.Critical)
            msg.setText('Please fill all fields.')
            msg.setStandardButtons(msg.Ok)
            msg.show()
        elif os.path.splitext(self.calibFile)[1] != '.txt':
            msg = QMessageBox(self)
            msg.setIcon(msg.Critical)
            msg.setText('Please input a calibration results text file (.txt).')
            msg.setStandardButtons(msg.Ok)
            msg.show()
        else:
            # Acquire all the inputs #
            xmin = float(xmin)
            xmax = float(xmax)
            dx = float(dx)
            ymin = float(ymin)
            ymax = float(ymax)
            dy = float(dy)
            z = float(z)
            grd = [xmin,xmax,dx,ymin,ymax,dy,z]

            # Start the worker #
            self.worker = performRectificationThread(self.calibFile,self.inputDirec,self.outputDirec,grd)
            self.worker.threadSignal.connect(self.on_threadSignal)

            self.lab1 = QLabel('Performing rectification...')
            self.grd.addWidget(self.lab1,14,0,1,3)

            self.loadlab = QLabel()
            self.loadmovie = QMovie(pth1+'loading.gif')
            self.loadlab.setMovie(self.loadmovie)
           
            self.worker.start()
            self.grd.addWidget(self.loadlab,14,3,1,3)
            self.loadmovie.start()
            self.worker.finishSignal.connect(self.on_closeSignal)

   def on_threadSignal(self,num):

       self.lab1.setParent(None)
       
       self.lab1 = QLabel('Rectifying image '+str(num) +' of '+str(len(os.listdir(self.inputDirec)))+'...')
       self.grd.addWidget(self.lab1,14,0,1,3)
       

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
        f1 = open(pth+'_binaries/im_rectif.pkl','rb')
        f2 = open(pth+'_binaries/extents.pkl','rb')
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

    def __init__(self,year,month,day,hour):
        super().__init__()
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        
    def run(self):
        
       print('Thread Started')
       
       f = open(pth+'_binaries/CameraName.pkl','rb')      
       camToInput = pickle.load(f)
       
       vidFile = SurfRCaT.getImagery_GetVideo(pth,camToInput,year=self.year,month=self.month,day=self.day,hour=self.hour)
       
##       # Deal with Buxton camera name change #
##       fs = os.path.getsize(pth+vidFile) # Get size of video file #  
##       if camToInput == 'buxtoncoastalcam' and fs<1000:
##           vidFile = SurfRCaT.getImagery_GetVideo('buxtonnorthcam')
##       #######################################
       
       with open(pth+'_binaries/vidFile.pkl','wb') as f:
           pickle.dump(vidFile,f)
           
       self.finishSignal.emit(1)   
        
       print('Thread Done')
 
      
class DecimateVidThread(QThread):
    ''' 
    Worker thread to check if camera is a PTZ camera.
    '''
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,vid,rate,numFrames,vidLen,fps,saveDir):
       super().__init__()

       self.vid = vid
       self.rate = rate
       self.numFrames = numFrames
       self.vidLen = vidLen
       self.fps = fps
       self.saveDir = saveDir
        
    def run(self):
        
       print('Thread Started')
       
       # If the rate is 0, then the user entered a number of frames rather than a rate #
       if self.rate == 0:
           secondsPerFrame = int(round(self.vidLen/self.numFrames))
       else: # If the rate is not zero, then the user entered a rate #
           secondsPerFrame = 1

       SurfRCaT.getImagery_GetStills(self.vid,secondsPerFrame,self.rate,self.vidLen,self.fps,self.saveDir)

        
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

        with open(pth+'_binaries/lidarIDs.pkl','wb') as f:
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
        
        f = open(pth+'_binaries/lidarIDs.pkl','rb')
        IDs = pickle.load(f)

        # If no lidar datasets were found here, need to tell the user #
        if not IDs:
            self.badSignal.emit(1)
        else: 
            ftp = ftplib.FTP('ftp.coast.noaa.gov',timeout=1000000)
            ftp.login('anonymous','anonymous')
            
            # Get a list of all lidar directories. These get updated through time so always need to check. #
            ftp.cwd('/pub/DigitalCoast')
            dirs = [i for i in ftp.nlst() if 'lidar' in i]
            alldirs = []
            for ii in dirs:
                ftp.cwd(ii)
                alldirs.append([ii+'/'+i for i in ftp.nlst() if 'geoid' in i])
                ftp.cwd('../')  

            
            appropID = list() # Initiate list of IDs which contain the camera location #
            i = 0
            for ID in IDs:
                
                i = i+1
                perDone = i/len(IDs)
                self.threadSignal.emit(perDone)  

                check = SurfRCaT.getLidar_TryID(ftp,alldirs,ID,self.cameraLoc_lat,self.cameraLoc_lon)
                ftp.cwd('../../../../')
                
                if check:
                    if len(check)>0:       
                        appropID.append(ID)
                        print(appropID)
            
            matchingTable = SurfRCaT.getLidar_GetDatasetNames(appropID)
            
            # Remove the strange Puerto Rico dataset that always shows up #
            idxNames = matchingTable[matchingTable['ID']==8560].index
            matchingTable.drop(idxNames,inplace=True)
            ###############################################################    
            

            if len(matchingTable) == 0:
                self.badSignal.emit(1)
            else:
                with open(pth+'_binaries/lidarTable.pkl','wb') as f:
                    pickle.dump(matchingTable,f)

                self.finishSignal.emit(1)
                
            print('Thread Done')


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

        f = open(pth+'_binaries/CameraName.pkl','rb')
        name = pickle.load(f)

        # Add the pre-defined applicable lidar ids for each WebCAT camera #
        if name == 'follypiernorthcam':
            IDs = [8575,5184,34,10,2,1]
        elif name == 'follypiersouthcam':
            IDs = [8575,5184,34,10,2,1]
        elif name == 'staugustinecam':
            IDs = [6330,5185,5184,8698,1070,1119,34,37,100,19,8]
        else:
            IDs = [6330,8713,5185,5184,5038,8608,520,34,37,19,8]

        matchingTable = SurfRCaT.getLidar_GetDatasetNames(IDs)

                      
        print('Thread Done')

        with open(pth+'_binaries/lidarTable.pkl','wb') as f:
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
                
        f = open(pth+'_binaries/chosenLidarID.pkl','rb')
        f1 = open(pth+'_binaries/az.pkl','rb')
        IDToDownload = pickle.load(f)
        az = pickle.load(f1)
        sf = SurfRCaT.getLidar_GetShapefile(IDToDownload)
        poly = SurfRCaT.getLidar_CalcViewArea(az,20,1000,self.cameraLoc_lat,self.cameraLoc_lon)
        
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

        

        with open(pth+'_binaries/tilesKeep.pkl','wb') as f:
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
        
        f = open(pth+'_binaries/tilesKeep.pkl','rb')
        tilesKeep = pickle.load(f)
        
        f = open(pth+'_binaries/chosenLidarID.pkl','rb')
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

        with open(pth+'_binaries/lidarDat.pkl','wb') as f:
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
        
        f = open(pth+'_binaries/lidarDat.pkl','rb')
        lidarDat = pickle.load(f)

        f2 = open(pth+'_binaries/CameraName.pkl','rb')
        camName = str(pickle.load(f2))

        f3 = open(pth+'_binaries/chosenLidarID.pkl','rb')
        ID = str(pickle.load(f3))

        pc = SurfRCaT.getLidar_CreatePC(lidarDat,self.cameraLoc_lat,self.cameraLoc_lon)

        # Save to user input directory so they can see it and install directory so SurfRCaT pptk launcher can see it #  
        with open(pth+'_binaries/lidarPC.pkl','wb') as f:
            pickle.dump(pc,f)

        with open(pth1+'lidarPC.pkl','wb') as f:
            pickle.dump(pc,f)
            
        self.finishSignal.emit(1)    
        
        print('Thread Done')   
        

class pptkWindowWorker(QThread):

    '''
    Worker thread to launch the pptk lidar viewer window
    '''
    
    finishSignal = pyqtSignal('PyQt_PyObject')
    badSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()

        
    def run(self):
        
        print('Thread Started')

        # Load the point cloud #
        f = open(pth+'_binaries/lidarPC.pkl','rb')
        pc = pickle.load(f)

        # Delete any pre-existing GCP files if they exist #
        try:
            os.remove(pth+'GCPs_lidar.txt')
            os.remove(pth+'_binaries/GCPs_lidar.pkl')
            os.remove(pth+'GCPs_im.txt')
            os.remove(pth+'_binaries/GCPs_im.pkl')
            os.remove(pth1+'Testing.txt')
        except OSError:
            pass

        # Call the viewer and let the user identify points (subprocess saves the output to file #
        command = 'cmd.exe /C '+pth1+'LaunchPPTKwin\LaunchPPTKwin.exe'             
        print(command)
        
        self.child = QProcess()
        self.child.start(command)
        self.child.waitForStarted(-1)
        self.child.waitForFinished(-1)

        # Load the output and create the GCPs from it #
        f = open(pth1+'Testing.txt','r') # This is a list of point indicies- not important for the user. #
        iGCPs1 = f.read()
        iGCPs2 = iGCPs1[1:len(iGCPs1)-2]

        try:
            iGCPs = list(map(int,iGCPs2.split(',')))
        except ValueError:
            self.badSignal.emit(1)
        else:
            GCPs_lidar = np.empty([0,3])
            for i in iGCPs:
                GCPs_lidar = np.vstack((GCPs_lidar,pc.iloc[i,:]))
            
            np.savetxt(pth+'GCPS_lidar.txt',GCPs_lidar)

            with open(pth+'_binaries/GCPs_lidar.pkl','wb') as f:
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
               
            
           with open(pth+'_binaries/GCPs_im.pkl','wb') as f:
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
        f1 = open(pth+'_binaries/GCPs_im.pkl','rb')
        f2 =  open(pth+'_binaries/GCPs_lidar.pkl','rb')     
        f_az = open(pth+'_binaries/az.pkl','rb')
        f_ZL = open(pth+'_binaries/ZL.pkl','rb')
        
        img = cv2.imread(pth+'calibrationImage.png')
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
        
        with open(pth+'_binaries/calibVals.pkl','wb') as f:
            pickle.dump(calibVals,f)
##
##        preamble1 = 'The optimized calibration parameter values are given below. Important notes:'
##        preamble2 = '   Omega, Phi, and Kappa are the three camera viewing angles. These can be converted'
##        preamble2_2 = '   to the azimuth, tilt, swing/roll conventions via...'
##        preamble3 = '   The input camera location has been set as the origin.'
##        ar1 = np.array(['Omega(rad)','Phi(rad)','Kappa(rad)','CamX(m)','CamY(m)','CamZ(m)','x0(pix)','y0(pix)','f(pix)'])
##        ar2 = np.array([calibVals[0],calibVals[1],calibVals[2],calibVals[3],calibVals[4],calibVals[5],calibVals[6],calibVals[7],calibVals[8]])
##        with open(pth+'calibVals2.txt','w') as f:
##            writer = csv.writer(f,delimiter=',')
##            writer.writerows(preamble1,preamble2,preamble2_2,preamble3,zip(ar1,ar2))
            
        np.savetxt(pth+'calibVals.txt',calibVals,fmt='%6f')            
      
        self.finishSignal.emit(1)    

        print('Thread Done')



class performRectificationThread(QThread):
    
    '''
    Worker thread to perform the rectification.
    '''
        
    finishSignal = pyqtSignal('PyQt_PyObject')
    threadSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,calibFile,inputDirec,outputDirec,grd):
        super().__init__()
        self.calibFile = calibFile
        self.inputDirec = inputDirec
        self.outputDirec = outputDirec
        self.grd = grd
        
    def run(self):

        print('Thread Started')
        
        calibVals = np.loadtxt(self.calibFile)
        images = os.listdir(self.inputDirec)

        num = 0
        for im in images:
            num = num+1
            self.threadSignal.emit(num)
            
            img = mpimg.imread(self.inputDirec+'/'+im)
            im_rectif,extents = SurfRCaT.rectify_RectifyImage(calibVals,img,self.grd) # Perform the rectification #

            self.canvas = FigureCanvas(Figure()) # Save the rectified image #
            self.ax = self.canvas.figure.subplots()
            self.ax.imshow(im_rectif,extent=extents,interpolation='bilinear')
            self.ax.set_xlabel('Local x (m)')
            self.ax.set_ylabel('Local y (m)')
            self.ax.axis('equal')
            self.canvas.print_figure(self.outputDirec+'/'+os.path.splitext(im)[0]+'_rectif.png')
           
##
##        # Save the parameters #  
##        with open(pth+'_binaries/im_rectif.pkl','wb') as f:
##            pickle.dump(im_rectif,f)
##        with open(pth+'_binaries/extents.pkl','wb') as f:
##            pickle.dump(extents,f)
            
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
