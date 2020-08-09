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
__version__ = '2.0'


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
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import time
import ftplib
import csv
import scipy.io
import utm


# Establish and format the installation directory. Some background things will be saved to the installation directory #
pth1 = os.path.dirname(os.path.realpath(__file__))
pth1 = os.path.join(str(pth1),'')

class WelcomeWindow(QWidget):
    ''' 
    Welcome window with text about the tool and options to start the user on a path.
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
        leftBar2 = QLabel('• Inputs and imagery')
        leftBar3 = QLabel('• Lidar data')
        leftBar4 = QLabel('• GCPs')
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
        txt2 = QLabel('SurfRCaT has been developed in partnership with the Southeast Coastal Ocean Observing Regional Association '+
                      '(SECOORA; https://secoora.org/), the United States Geological Survey (USGS), and the National Oceanic and Atmospheric '+
                      'Administration (NOAA). Documentation for the tool, including helpful tutorials, can be found on the website '+
                      '(conlin-matt.github.io/surfrcat/). If you have an issue, please post it on the Github Issue tracker.')
        txt2.setWordWrap(True)

        txt3 = QLabel('What would you like to do?')
        calibBut = QRadioButton('Calibrate a surfcam')
        rectifBut = QRadioButton('Rectify images (from already-calibrated camera)')
        webcatBut = QRadioButton('Download imagery from WebCAT camera')

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
        grd2.addWidget(webcatBut,3,1,1,3)
        rightGroupBox2.setLayout(grd2)
        grd.addWidget(rightGroupBox1,0,0,1,4)
        grd.addWidget(rightGroupBox2,1,0,1,4)
        rightGroupBox.setLayout(grd)

        # Connect widgets with signals #
        calibBut.clicked.connect(self.on_calibSelect)
        rectifBut.clicked.connect(self.on_rectifSelect)
        webcatBut.clicked.connect(self.on_webcatSelect)
        ################################

        # Full widget layout setup #
        fullLayout = QHBoxLayout()
        fullLayout.addWidget(leftGroupBox)
        fullLayout.addWidget(rightGroupBox)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        qr = self.frameGeometry()
        lp = QDesktopWidget().availableGeometry().topLeft()
        qr.moveTopLeft(lp)
        self.move(qr.topLeft())        
        self.show()
        ###############################


    def on_calibSelect(self):
        
        self.close()
        self.w = StartCalibWindow()
        self.w.show()

    def on_rectifSelect(self):
        
        self.close()
        self.w = rectify_UserInputs()
        self.w.show()

    def on_webcatSelect(self):
        
        self.close()
        self.w = WebCATDownloadUtility()
        self.w.show()



class StartCalibWindow(QWidget):
    ''' 
    Window allowing (requiring) the user to input a working directory. Things will be saved to/loaded from
    this directory, if applicable. 
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
        leftBar2 = QLabel('• Inputs and imagery')
        leftBar3 = QLabel('• Lidar data')
        leftBar4 = QLabel('• GCPs')
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
        qr = self.frameGeometry()
        lp = QDesktopWidget().availableGeometry().topLeft()
        qr.moveTopLeft(lp)
        self.move(qr.topLeft())        
        self.show()
        ###############################
        
        
    def getWD(self):
        '''
        Get the working directory and save it
        '''
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
       Moves to the Inputs and imagery step when start is selected
       '''
       if self.wdLine.text() != '':
           self.close()
           self.tool = inputsAndImagery_UserInputs()
           self.tool.show()
       else:
           msg = QMessageBox(self)
           msg.setIcon(msg.Critical)
           msg.setText('Please input a working directory.')
           msg.setStandardButtons(msg.Ok)
           msg.show()
       
    def goBack(self):
        
        self.close()
        self.w = WelcomeWindow()
        self.w.show()    
##============================================================================##       


##============================================================================## 
# Inputs and imagery step: Get inputs and the image to be used for the calibration #
##============================================================================##
class inputsAndImagery_UserInputs(QWidget):
    '''
    Window allowing the user to input necessary info on any surfcam, such as location and name, or choose a WebCAT cam. Video file
    must also be provided.
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
       leftBar2 = QLabel('• Inputs and imagery')
       leftBar3 = QLabel('• Lidar data')
       leftBar4 = QLabel('• GCPs')
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
       lblLat = QLabel('Latitude (decimal degrees):')
       lblLon = QLabel('Longitude (decimal degrees):')
       lblElev = QLabel('Elevation (NAVD88 m):')
       lblAz = QLabel('Azimuth (degrees):')
       self.bxLat = QLineEdit()
       self.bxLon = QLineEdit()
       self.bxElev = QLineEdit()
       self.bxAz = QLineEdit()
       self.azHelpBut = QPushButton('?')
       lblPth = QLabel('Select the saved video from your camera (.mp4 format):')
       lblPth.setWordWrap(True)
       browseBut = QPushButton('Browse')
       self.bxPth = QLineEdit()
       useSavedLidarLab1 = QLabel('Use saved lidar point cloud?')
       useSavedLidarButYes1 = QRadioButton('Yes')
       useSavedLidarButNo1 = QRadioButton('No')
       useSavedLidarButNo1.setChecked(True)
       self.useSavedLidarButLine1 = QLineEdit()
       self.useSavedLidarButBrowse1 = QPushButton('Browse')
       line = QFrame(); line.setFrameShape(QFrame.HLine)
       line2 = QFrame(); line2.setFrameShape(QFrame.HLine)
       orLab = QLabel('Or')
       webcatLab = QLabel('Select camera from the WebCAT array:')
       opt = QComboBox()
       opt.addItem('--')
       opt.addItem('Folly Beach Pier (north)')
       opt.addItem('Folly Beach Pier (south)')
       opt.addItem('St. Augustine Pier')
       opt.addItem('Miami 40th Street')
       opt.setCurrentIndex(0)
       lblPth2 = QLabel('Select saved video from this WebCAT camera:')
       lblPth2.setWordWrap(True)
       browseBut2 = QPushButton('Browse')
       self.bxPth2 = QLineEdit()
       useSavedLidarLab2 = QLabel('Use saved lidar point cloud?')
       useSavedLidarButYes2 = QRadioButton('Yes')
       useSavedLidarButNo2 = QRadioButton('No')
       useSavedLidarButNo2.setChecked(True)
       self.useSavedLidarButLine2 = QLineEdit()
       self.useSavedLidarButBrowse2 = QPushButton('Browse')
       backBut = QPushButton('< Back')
       contBut1 = QPushButton('Continue >')
       contBut2 = QPushButton('Continue >')

       rightGroupBox = QGroupBox()
       rightGroupBox1 = QGroupBox('Any camera')
       rightGroupBox2 = QGroupBox('WebCAT camera')
       self.grd = QGridLayout()
       self.grd1 = QGridLayout()
       self.grd2 = QGridLayout()
       self.grd1.addWidget(lblDir1,0,0,1,3)
       self.grd1.addWidget(self.bxName,0,3,1,3)
       self.grd1.addWidget(lblDir,1,0,1,6)
       self.grd1.addWidget(lblLat,2,1,1,3)
       self.grd1.addWidget(self.bxLat,2,4,1,2)
       self.grd1.addWidget(lblLon,3,1,1,3)
       self.grd1.addWidget(self.bxLon,3,4,1,2)
       self.grd1.addWidget(lblElev,4,1,1,3)
       self.grd1.addWidget(self.bxElev,4,4,1,2)
       self.grd1.addWidget(self.azHelpBut,5,0,1,1)
       self.grd1.addWidget(lblAz,5,1,1,3)
       self.grd1.addWidget(self.bxAz,5,4,1,2)
       self.grd1.addWidget(lblPth,6,0,1,6)
       self.grd1.addWidget(browseBut,7,5,1,1)
       self.grd1.addWidget(self.bxPth,7,0,1,5)
       self.grd1.addWidget(useSavedLidarLab1,8,0,1,6)
       self.grd1.addWidget(useSavedLidarButNo1,9,0,1,1)
       self.grd1.addWidget(useSavedLidarButYes1,9,1,1,1)
       self.grd1.addWidget(contBut1,11,4,1,2)
       rightGroupBox1.setLayout(self.grd1)
       self.grd2.addWidget(webcatLab,0,0,1,6)
       self.grd2.addWidget(opt,1,0,1,4)
       self.grd2.addWidget(lblPth2,2,0,1,6)
       self.grd2.addWidget(self.bxPth2,3,0,1,5)
       self.grd2.addWidget(browseBut2,3,5,1,1)
       self.grd2.addWidget(useSavedLidarLab2,4,0,1,4)
       self.grd2.addWidget(useSavedLidarButNo2,5,0,1,1)
       self.grd2.addWidget(useSavedLidarButYes2,5,1,1,1)
       self.grd2.addWidget(contBut2,7,4,1,2)
       rightGroupBox2.setLayout(self.grd2)

       self.grd.addWidget(rightGroupBox1,0,0,4,6)
       self.grd.addWidget(line,5,0,1,8)
       self.grd.addWidget(orLab,6,0,1,1)
       self.grd.addWidget(line2,7,0,1,8)
       self.grd.addWidget(rightGroupBox2,8,0,3,6)
       self.grd.addWidget(backBut,11,0,1,2)
       self.grd.setAlignment(Qt.AlignCenter)
       rightGroupBox.setLayout(self.grd)
       ##############################
       
       # Assign signals to widgets #
       browseBut.clicked.connect(self.onBrowseClick)
       browseBut2.clicked.connect(self.onBrowseClick2)
       backBut.clicked.connect(self.GoBack)
       contBut1.clicked.connect(self.getInputs_NotWebCAT)
       contBut2.clicked.connect(self.getInputs_WebCAT)
       self.azHelpBut.clicked.connect(self.onAzHelpClick)
       opt.activated.connect(self.getInputs_WebCAT1)
       useSavedLidarButYes1.clicked.connect(self.useSavedLidarSet1)
       useSavedLidarButNo1.clicked.connect(self.useSavedLidarSet1_no)
       useSavedLidarButYes2.clicked.connect(self.useSavedLidarSet2)
       useSavedLidarButNo2.clicked.connect(self.useSavedLidarSet2_no)
       self.useSavedLidarButBrowse1.clicked.connect(self.onLidarBrowseClick1)
       self.useSavedLidarButBrowse2.clicked.connect(self.onLidarBrowseClick2)
       self.lidarFile = None
       #############################

       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       qr = self.frameGeometry()
       lp = QDesktopWidget().availableGeometry().topLeft()
       qr.moveTopLeft(lp)
       self.move(qr.topLeft())        
       self.show()
       ############################

    def onBrowseClick(self):
       '''
       Get saved non-WebCAT video, if applicable.
       '''
       dlg = QFileDialog()
       dlg.setNameFilter('mp4 files (*.mp4)')
       dlg.setFileMode(QFileDialog.ExistingFile)
       if dlg.exec_():
           file = dlg.selectedFiles()
           self.file = file[0]
            
           self.bxPth.setText(self.file)
           
    def onBrowseClick2(self):
       '''
       Get saved WebCAT video, if applicable.
       '''
       dlg = QFileDialog()
       dlg.setNameFilter('mp4 files (*.mp4)')
       dlg.setFileMode(QFileDialog.ExistingFile)
       if dlg.exec_():
           file2 = dlg.selectedFiles()
           self.file2 = file2[0]
            
           self.bxPth2.setText(self.file2)
           
        
    def useSavedLidarSet1(self):
        self.grd1.addWidget(self.useSavedLidarButLine1,10,0,1,5)
        self.grd1.addWidget(self.useSavedLidarButBrowse1,10,5,1,1)
        
    def useSavedLidarSet1_no(self):
        self.useSavedLidarButLine1.setParent(None)
        self.useSavedLidarBrowse1.setParent(None)

    def onLidarBrowseClick1(self):
       '''
       Get saved lidar file for non-WebCAT camera, if the user wants to use one.
       '''
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.ExistingFile)
       if dlg.exec_():
           file3 = dlg.selectedFiles()
           self.lidarFile = file3[0]
            
           self.useSavedLidarButLine1.setText(self.lidarFile)

    def useSavedLidarSet2(self):
        self.grd2.addWidget(self.useSavedLidarButLine2,6,0,1,5)
        self.grd2.addWidget(self.useSavedLidarButBrowse2,6,5,1,1)
        
    def useSavedLidarSet2_no(self):
        self.useSavedLidarButLine2.setParent(None)
        self.useSavedLidarBrowse2.setParent(None)

    def onLidarBrowseClick2(self):
       '''
       Get saved lidar file for WebCAT camera, if the user wants to use one.
       '''        
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.ExistingFile)
       if dlg.exec_():
           file3 = dlg.selectedFiles()
           self.lidarFile = file3[0]
            
           self.useSavedLidarButLine2.setText(self.lidarFile)  
        

    def onAzHelpClick(self):
       '''
       Display help box for azimuth.
       '''
       
       msg = QMessageBox(self)
       msg.setIcon(msg.Question)
       msg.setText('The azimuth angle is the right-handed angle that the camera is facing with respect to due north. '+
                   'A camera looking directly north has an azimuth angle of 0' + u'\N{DEGREE SIGN}'+', one looking east '+
                   'an azimuth of 90'+u'\N{DEGREE SIGN}'+', one south an azimuth of 180'+u'\N{DEGREE SIGN}'+', and one '+
                   'west an azimuth of 270'+u'\N{DEGREE SIGN}'+'.')
       msg.setStandardButtons(msg.Ok)
       msg.show()

    def GoBack(self):
       '''
       Go back to camera choice window on Back click
       '''
       self.close()
       self.backToOne = WelcomeWindow()
       
       
    def getInputs_NotWebCAT(self):
       '''
       Get user-input information for non-WebCAT camera
       '''

       global pth

       # Error catching #
       cameraName = self.bxName.text()
       fileName = self.bxPth.text()
       if cameraName == '':
           msg = QMessageBox(self)
           msg.setIcon(msg.Critical)
           msg.setText('Please input a name for the camera.')
           msg.setStandardButtons(msg.Ok)
           msg.show()
       elif fileName == '':
           msg = QMessageBox(self)
           msg.setIcon(msg.Critical)
           msg.setText('Please input a video file.')
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

       # Create save directories if they don't exist. If they do, warn the user. #
       if os.path.exists(pth+'calibration_'+self.fileName_NoExt) == 0:
            os.mkdir(pth+'calibration_'+self.fileName_NoExt)
            os.mkdir(pth+'calibration_'+self.fileName_NoExt+'/_binaries')
            os.mkdir(pth+'calibration_'+self.fileName_NoExt+'/products')
            os.mkdir(pth+'calibration_'+self.fileName_NoExt+'/results')
            pth = pth+'calibration_'+self.fileName_NoExt+'/'

            # Save the camera name and location and other params #
            with open(pth+'_binaries/CameraLocation.pkl','wb') as f:
                pickle.dump(cameraLocation,f)
            with open(pth+'_binaries/CameraName.pkl','wb') as f:
                pickle.dump(cameraName,f)
            with open(pth+'_binaries/az.pkl','wb') as f:
                pickle.dump(az,f)
            with open(pth+'_binaries/ZL.pkl','wb') as f:
                pickle.dump(ZL,f)
            with open(pth+'_binaries/vidFile.pkl','wb') as f:
                pickle.dump(self.file,f)
            camType = 0
            with open(pth+'_binaries/camType.pkl','wb') as f:
                pickle.dump(camType,f)
               
            os.mkdir(pth+'frames')
            saveDir = pth+'frames'

            try:
                os.remove(pth+'_binaries/linkToLidar.pkl')
            except:
                pass

            # Save the lidar dataset the user wants to use, if they established one #
            if self.lidarFile:
                with open(pth+'_binaries/linkToLidar.pkl','wb') as f:
                    pickle.dump(self.lidarFile,f)

                cmd = 'copy '+os.path.realpath(self.lidarFile)+' '+os.path.realpath(pth1)+'\\lidarPC.pkl'
                os.system(cmd)

                basePth = self.lidarFile.rsplit('/',1)[0].rsplit('/',1)[0]
                f = open(basePth+'/_binaries/chosenLidarID.pkl','rb')
                ID = pickle.load(f)
                with open(pth+'_binaries/chosenLidarID.pkl','wb') as f:
                    pickle.dump(ID,f)
            

            self.close()
            self.d = inputsAndImagery_ExtractFrames(self.file,saveDir)
            self.d.show()

            
       else:
            msg = QMessageBox(self)
            msg.setIcon(msg.Warning)
            msg.setText('A subdirectory for this video already exists in your working directory, making it appear that '+
                       'you are re-trying a calibration. If this is not true, please remove this subdirectory from your working directory or rename it. If it is, '+
                       'do you want to use the same calibration image as before?')
            msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            msg.buttonClicked.connect(self.onMsgBoxClick)
            msg.show()
           
           
    def onMsgBoxClick(self,i):

        global pth
        
        if i.text() == '&Yes':
            
            pth = pth+'calibration_'+self.fileName_NoExt+'/'

            try:
               os.remove(pth+'_binaries/linkToLidar.pkl')
            except:
               pass

            if self.lidarFile:
                with open(pth+'_binaries/linkToLidar.pkl','wb') as f:
                    pickle.dump(self.lidarFile,f)

                cmd = 'copy '+os.path.realpath(self.lidarFile)+' '+os.path.realpath(pth1)+'\\lidarPC.pkl'
                os.system(cmd)

                basePth = self.lidarFile.rsplit('/',1)[0].rsplit('/',1)[0]
                f = open(basePth+'/_binaries/chosenLidarID.pkl','rb')
                ID = pickle.load(f)
                with open(pth+'_binaries/chosenLidarID.pkl','wb') as f:
                    pickle.dump(ID,f)

                self.close()
                self.w = PickGCPsWindow(self.lidarFile)
                self.w.show()
                
            else:
                self.close()
                self.ls = lidarData_FindUseableDatasetsWindow()
                self.ls.show()

        elif i.text() == '&No':

            pth = pth+'calibration_'+self.fileName_NoExt+'/'

            try:
               os.remove(pth+'_binaries/linkToLidar.pkl')
            except:
               pass

            if self.lidarFile:
                with open(pth+'_binaries/linkToLidar.pkl','wb') as f:
                    pickle.dump(self.lidarFile,f)

                cmd = 'copy '+os.path.realpath(self.lidarFile)+' '+os.path.realpath(pth1)+'\\lidarPC.pkl'
                os.system(cmd)

                basePth = self.lidarFile.rsplit('/',1)[0].rsplit('/',1)[0]
                f = open(basePth+'/_binaries/chosenLidarID.pkl','rb')
                ID = pickle.load(f)
                with open(pth+'_binaries/chosenLidarID.pkl','wb') as f:
                    pickle.dump(ID,f)
            
            self.close()
            self.w = inputsAndImagery_ChooseImage()
            self.w.show()


    def getInputs_WebCAT1(self,item):
        '''
        Get user inputs for WebCAT camera.
        '''
        
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
           

    def getInputs_WebCAT(self):
        
       global pth

       vidName = self.file2.split('/')[len(self.file2.split('/'))-1]
       vidName2 = vidName.split('.')[1]
       yr = vidName2.split('-')[0]
       mo = vidName2.split('-')[1]
       day = vidName2.split('-')[2].split('_')[0]
       hr = vidName2.split('-')[2].split('_')[1]
       
       if os.path.exists(pth+'calibration_'+self.cameraName+'.'+yr+'-'+mo+'-'+day+'_'+hr) == 0:

           # Make save direcs if they don't exist. If they do, warn the user #
           os.mkdir(pth+'calibration_'+self.cameraName+'.'+yr+'-'+mo+'-'+day+'_'+hr)
           os.mkdir(pth+'calibration_'+self.cameraName+'.'+yr+'-'+mo+'-'+day+'_'+hr+'/_binaries')
           os.mkdir(pth+'calibration_'+self.cameraName+'.'+yr+'-'+mo+'-'+day+'_'+hr+'/products')
           os.mkdir(pth+'calibration_'+self.cameraName+'.'+yr+'-'+mo+'-'+day+'_'+hr+'/results')
           pth = pth+'calibration_'+self.cameraName+'.'+yr+'-'+mo+'-'+day+'_'+hr+'/'
           os.mkdir(pth+'frames');self.saveDir = pth+'frames'
           
           # Save everything #
           with open(pth+'_binaries/CameraLocation.pkl','wb') as f:
               pickle.dump(self.cameraLocation,f)
           with open(pth+'_binaries/CameraName.pkl','wb') as f:
               pickle.dump(self.cameraName,f)
           with open(pth+'_binaries/az.pkl','wb') as f:
               pickle.dump(self.az,f)
           with open(pth+'_binaries/ZL.pkl','wb') as f:
               pickle.dump(self.ZL,f)
           with open(pth+'_binaries/vidFile.pkl','wb') as f:
               pickle.dump(self.file2,f)
           camType = 1
           with open(pth+'_binaries/camType.pkl','wb') as f:
               pickle.dump(camType,f)

           try:
               os.remove(pth+'_binaries/linkToLidar.pkl')
           except:
               pass
    

           if self.lidarFile:
               with open(pth+'_binaries/linkToLidar.pkl','wb') as f:
                    pickle.dump(self.lidarFile,f)

               cmd = 'copy '+os.path.realpath(self.lidarFile)+' '+os.path.realpath(pth1)+'\\lidarPC.pkl'
               os.system(cmd)
                    
               basePth = self.lidarFile.rsplit('/',1)[0].rsplit('/',1)[0]
               f = open(basePth+'/_binaries/chosenLidarID.pkl','rb')
               ID = pickle.load(f)
               with open(pth+'_binaries/chosenLidarID.pkl','wb') as f:
                   pickle.dump(ID,f)


           self.worker = getLidar_WebCATThread()
           self.worker.finishSignal.connect(self.moveToDecimator)

           lab1 = QLabel('Getting lidar datasets...')
           self.grd.addWidget(lab1,12,0,1,1)

           self.loadlab = QLabel()
           self.loadmovie = QMovie(pth1+'loading.gif')
           self.loadlab.setMovie(self.loadmovie)
       
           self.worker.start()
           self.grd.addWidget(self.loadlab,12,1,1,1)
           self.loadmovie.start()

               
       else:
           msg = QMessageBox(self)
           msg.setIcon(msg.Warning)
           msg.setText('A subdirectory for this video already exists in your working directory, making it appear that '+
                       'you are re-calibrating and previously-calibrated camera. If this is not true, please remove this subdirectory from your working directory or rename it. If it is, '+
                       ' do you want to use the same calibration image as before (select No if you do not have images yet)?')
           msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
           msg.show()
           msg.buttonClicked.connect(self.onMsgBoxClick1)


    def moveToDecimator(self):
        
        self.loadmovie.stop()
        self.close()
        self.w = inputsAndImagery_ExtractFrames(self.file2,self.saveDir)
        self.w.show()

           
           
    def onMsgBoxClick1(self,i):

        global pth

        vidName = self.file2.split('/')[len(self.file2.split('/'))-1]
        vidName2 = vidName.split('.')[1]
        yr = vidName2.split('-')[0]
        mo = vidName2.split('-')[1]
        day = vidName2.split('-')[2].split('_')[0]
        hr = vidName2.split('-')[2].split('_')[1]
 
        pth = pth+'calibration_'+self.cameraName+'.'+yr+'-'+mo+'-'+day+'_'+hr+'/'

        try:
            os.remove(pth+'_binaries/linkToLidar.pkl')
        except:
            pass
        
        if i.text() == '&Yes':

           if self.lidarFile:
                with open(pth+'_binaries/linkToLidar.pkl','wb') as f:
                    pickle.dump(self.lidarFile,f)

                cmd = 'copy '+os.path.realpath(self.lidarFile)+' '+os.path.realpath(pth1)+'\\lidarPC.pkl'
                os.system(cmd)
                    
                basePth = self.lidarFile.rsplit('/',1)[0].rsplit('/',1)[0]
                f = open(basePth+'/_binaries/chosenLidarID.pkl','rb')
                ID = pickle.load(f)
                with open(pth+'_binaries/chosenLidarID.pkl','wb') as f:
                   pickle.dump(ID,f)

                self.close()
                self.w = PickGCPsWindow(self.lidarFile)
                self.w.show()

           else:
               
                self.worker = getLidar_WebCATThread()
                self.worker.finishSignal.connect(self.skipToLidar)

                lab1 = QLabel('Getting lidar datasets...')
                self.grd.addWidget(lab1,12,0,1,1)

                self.loadlab = QLabel()
                self.loadmovie = QMovie(pth1+'loading.gif')
                self.loadlab.setMovie(self.loadmovie)
           
                self.worker.start()
                self.grd.addWidget(self.loadlab,12,1,1,1)
                self.loadmovie.start()

        elif i.text() == '&No':

           try:
               os.remove(pth+'_binaries/linkToLidar.pkl')
           except:
               pass

           if self.lidarFile:
                with open(pth+'_binaries/linkToLidar.pkl','wb') as f:
                    pickle.dump(self.lidarFile,f)

                cmd = 'copy '+os.path.realpath(self.lidarFile)+' '+os.path.realpath(pth1)+'\\lidarPC.pkl'
                os.system(cmd)

                basePth = self.lidarFile.rsplit('/',1)[0].rsplit('/',1)[0]
                f = open(basePth+'/_binaries/chosenLidarID.pkl','rb')
                ID = pickle.load(f)
                with open(pth+'_binaries/chosenLidarID.pkl','wb') as f:
                    pickle.dump(ID,f)

           try:
               ims = os.listdir(pth+'frames')
               for i in ims:
                   os.remove(pth+'frames/'+i)
           except:
               pass
            
           self.saveDir = pth+'frames'
               
           
           self.worker = getLidar_WebCATThread()
           self.worker.finishSignal.connect(self.moveToDecimator)

           lab1 = QLabel('Getting lidar datasets...')
           self.grd.addWidget(lab1,12,0,1,1)

           self.loadlab = QLabel()
           self.loadmovie = QMovie(pth1+'loading.gif')
           self.loadlab.setMovie(self.loadmovie)
       
           self.worker.start()
           self.grd.addWidget(self.loadlab,12,1,1,1)
           self.loadmovie.start()


    def skipToLidar(self):

        f = open(pth+'_binaries/lidarTable.pkl','rb')
        lidarTable = pickle.load(f)

        self.close()
        self.lw = lidarData_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
        self.lw.resize(900,350)
        self.lw.show()

         
    def onMsgBoxClick3(self,i):
       
       if i.text() == '&Yes':
            
           self.close()
           self.w = PickGCPsWindow()
           self.w.show()
           
       else:
           f = open(pth+'_binaries/lidarTable.pkl','rb')
           lidarTable = pickle.load(f)

           self.close()
           self.lw = lidarData_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
           self.lw.resize(900,350)
           self.lw.show()
        



class inputsAndImagery_ExtractFrames(QWidget):
    '''
    Window allowing the user to extract frames from a video at a certain rate.
    '''
    
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
       leftBar2 = QLabel('• Inputs and imagery')
       leftBar3 = QLabel('• Lidar data')
       leftBar4 = QLabel('• GCPs')
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
       labDir = QLabel('Input your desired decimation rate or number of frames (evenly spaced) below and click Go to begin the video decimation.')
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
       self.goBut = QPushButton('Go')
       self.backBut = QPushButton('Back')
                        

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
       self.grd.addWidget(self.backBut,8,0,1,2)
       self.grd.addWidget(self.goBut,8,4,1,2)
       rightGroupBox.setLayout(self.grd)

       # Assign signals to widgets #
       updateBut.clicked.connect(self.onUpdateClick)
       self.goBut.clicked.connect(self.onGoClick)
       self.backBut.clicked.connect(self.onBackClick)
       #############################
 
       # Full widget layout setup #
       fullLayout = QHBoxLayout()
       fullLayout.addWidget(leftGroupBox)
       fullLayout.addWidget(rightGroupBox)
       self.setLayout(fullLayout)

       self.setWindowTitle('SurfRCaT')
       qr = self.frameGeometry()
       lp = QDesktopWidget().availableGeometry().topLeft()
       qr.moveTopLeft(lp)
       self.move(qr.topLeft())        
       self.show()
       ############################       


    def onUpdateClick(self):
        '''
        Show user how many frames will be extracted for a given descimation rate.
        '''
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
        '''
        Launch the frame extraction process.
        '''
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
            self.goBut.setEnabled(False)
            self.backBut.setEnabled(False)
            
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
            self.goBut.setEnabled(False)
            self.backBut.setEnabled(False)

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
            self.w = inputsAndImagery_ChooseImage()
            self.w.show()

    def onBackClick(self):
        self.close()
        self.w = inputsAndImagery_UserInputs()
        self.w.show()


       
class inputsAndImagery_ChooseImage(QWidget):
    '''
    Window allowing the user to scroll through extracted frames and choose the image they want to use
    for remote-GCP extraction.
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
       leftBar2 = QLabel('• Inputs and imagery')
       leftBar3 = QLabel('• Lidar data')
       leftBar4 = QLabel('• GCPs')
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
       self.frames1 = os.listdir(pth+'frames/')
       self.frames = []
       for f in self.frames1:
           if f.endswith(".png"):
               self.frames.append(f)
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
       qr = self.frameGeometry()
       lp = QDesktopWidget().availableGeometry().topLeft()
       qr.moveTopLeft(lp)
       self.move(qr.topLeft())        
       self.show()
       ############################

    def onForwardClick(self):
       '''
       Scroll forward to the next frame, if possible.
       '''
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
       '''
       Scroll backwards to the previous frame, if possible.
       '''        
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
        '''
        Save the chosen frame and move to the next step
        '''
        
        frameNumSel = self.frame
        img = cv2.imread(pth+'frames/'+self.frames[frameNumSel])
        cv2.imwrite(pth+'products/calibrationImage.png',img)

        f = open(pth+'_binaries/camType.pkl','rb')
        camType = pickle.load(f)
        if camType == 0: # Not WebCAT #
            if os.path.exists(pth+'_binaries/linkToLidar.pkl'):
                f = open(pth+'_binaries/linkToLidar.pkl','rb')
                linkToLidar = pickle.load(f)

                self.close()
                self.w = PickGCPsWindow(linkToLidar)
                self.w.show()
            else:
                self.close()
                self.w = lidarData_FindUseableDatasetsWindow()
                self.w.show()
                
        else: # WebCAT #

            if os.path.exists(pth+'_binaries/linkToLidar.pkl'):
                f = open(pth+'_binaries/linkToLidar.pkl','rb')
                linkToLidar = pickle.load(f)

                self.close()
                self.w = PickGCPsWindow(linkToLidar)
                self.w.show()
            else:
            
                if os.path.exists(pth+'products/lidarPC.pkl'):
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Information)
                    txt = ('Existing lidar point cloud for this camera found. Do you want to use it?')
                    msg.setText(txt)
                    msg.setWindowTitle('Error')
                    msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
                    msg.buttonClicked.connect(self.onMsgBoxClick)
                    msg.show()
                else:
                    f = open(pth+'_binaries/lidarTable.pkl','rb')
                    lidarTable = pickle.load(f)

                    self.close()
                    self.lw = lidarData_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
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
           self.lw = lidarData_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
           self.lw.resize(900,350)
           self.lw.show()


    def onBackButClick(self):

        global pth
        pth = pth.rsplit('/',2)[0]+'/'
        
        self.close()
        self.ww = inputsAndImagery_UserInputs()  
        self.ww.show()

##============================================================================##       


##============================================================================## 
# WebCAT download utility #
##============================================================================##
class WebCATDownloadUtility(QWidget):
    '''
    Window allowing the user to download imagery from WebCAT camera
    '''
   
    def __init__(self):
        super().__init__()
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        self.initUI()

        
    def initUI(self):
       
       # Right contents box setup #
       intro = QLabel('The Web-camera Application Testbed (WebCAT) is a network of 7 surfcams spanning the southeastern U.S. coastline. '+
                      'Historic feeds from the cameras are stored on servers and accessible in 10-minute video-clips. '+
                      'Live feeds from each camera can be viewed at https://secoora.org/webcat/, and a summary of available historic video from each camera '+
                      'can be found at http://webcat-video.axds.co/status/. Please input the camera and '+
                      'desired imagery date(s) to download below, and a video will be downloaded automatically. You can input multiple dates by separating them with '+
                      'a comma, but you must input the same number of values in each field. For example, if you wanted to download imagery from both 1000 '+
                      'and 1010 on January 1 2020, you would input 2020,2020 ; 01,01 ; 01,01 ; 1000,1010. Note: only 4 of the 7 cameras can be calibrated '+
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
       self.backBut = QPushButton('< Back')
       self.contBut = QPushButton('Download')
       lblDir = QLabel('Select directory to save video(s) to:')
       self.bxDir = QLineEdit()
       browseBut = QPushButton('Browse')
       lblDir1 = QLabel('Input desired imagery date(s) below (in yyyy,mm,dd,HHHH format; separate multiple with commas):')
       lblDir1.setWordWrap(True)
       self.bxYear = QLineEdit()
       self.bxMonth = QLineEdit()
       self.bxDay = QLineEdit()
       self.bxHour = QLineEdit()
       lblYear = QLabel('Year:')
       lblMonth = QLabel('Month:')
       lblDay = QLabel('Day:')
       lblHour = QLabel('Hour:')
     
       rightGroupBox = QGroupBox()
       rightGroupBox1 = QGroupBox()
       rightGroupBox2 = QGroupBox()
       self.grd = QGridLayout()
       grd1 = QGridLayout()
       grd2 = QGridLayout()
                      
       grd1.addWidget(txt,0,0,1,2)
       grd1.addWidget(opt,1,0,1,2)
       rightGroupBox1.setLayout(grd1)
       grd2.addWidget(lblDir,0,0,1,4)
       grd2.addWidget(self.bxDir,1,0,1,3)
       grd2.addWidget(browseBut,1,3,1,1)
       grd2.addWidget(lblDir1,2,0,1,4)
       grd2.addWidget(lblYear,3,0,1,2)
       grd2.addWidget(self.bxYear,3,2,1,2)              
       grd2.addWidget(lblMonth,4,0,1,2)
       grd2.addWidget(self.bxMonth,4,2,1,2) 
       grd2.addWidget(lblDay,5,0,1,2)
       grd2.addWidget(self.bxDay,5,2,1,2)
       grd2.addWidget(lblHour,6,0,1,2)
       grd2.addWidget(self.bxHour,6,2,1,2)
       rightGroupBox2.setLayout(grd2)

       self.grd.addWidget(intro,0,0,4,4)
       self.grd.addWidget(rightGroupBox1,4,0,2,4)
       self.grd.addWidget(rightGroupBox2,6,0,4,4)
       self.grd.addWidget(self.backBut,10,0,1,2)
       self.grd.addWidget(self.contBut,10,2,1,2)
       rightGroupBox.setLayout(self.grd)

              
       # Connect widgets with signals #
       opt.activated.connect(self.getSelectedCam)
       browseBut.clicked.connect(self.onBrowseClick)
       self.backBut.clicked.connect(self.GoBack)
       self.contBut.clicked.connect(self.downloadVid)
       ################################

       # Full widget layout setup #
       grdd = QGridLayout()
       grdd.addWidget(rightGroupBox,0,0,1,1)
       self.setLayout(grdd)

       self.setWindowTitle('SurfRCaT')
       qr = self.frameGeometry()
       lp = QDesktopWidget().availableGeometry().topLeft()
       qr.moveTopLeft(lp)
       self.move(qr.topLeft())        
       self.show()
       ############################
        
        
    def getSelectedCam(self,item):

       WebCATdict = {'Placeholder':[0,0],
                    'follypiernorthcam':[32.654731,-79.939322],
                    'follypiersouthcam':[32.654645,-79.939597],
                    'staugustinecam':[29.856559,-81.265545],
                    'miami40thcam':[ 25.812227, -80.122400]}
      
       # Get name of selected camera #
       cams = ['Placeholder','follypiernorthcam','follypiersouthcam','staugustinecam','miami40thcam']
       self.cameraLocation = WebCATdict[cams[item]]
       self.cameraName = cams[item]
           

    def onBrowseClick(self):
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.Directory)
       if dlg.exec_():
           direc = dlg.selectedFiles()
           self.direc = direc[0]
            
           self.bxDir.setText(self.direc)

    
    def downloadVid(self):
       '''
       Start video download process.
       '''

       self.contBut.setEnabled(False)
       self.backBut.setEnabled(False)
       
       try:
           del self.yr
       except:
           pass
       try:
           del self.mo
       except:
           pass
       try:
           del self.day
       except:
           pass
       try:
           del self.hour
       except:
           pass
       


       if self.bxYear.text!='' and self.bxMonth.text()!='' and self.bxDay.text()!='' and self.bxHour.text()!='':

           self.yr = self.bxYear.text(); self.yr = self.yr.split(',')
           self.mo = self.bxMonth.text(); self.mo = self.mo.split(',')
           self.day = self.bxDay.text(); self.day = self.day.split(',')
           self.hour = self.bxHour.text(); self.hour = self.hour.split(',')

           check = [i for i in self.hour if ':' in i]
           if check:
               self.contBut.setEnabled(True)
               self.backBut.setEnabled(True)
               
               msg = QMessageBox(self)
               msg.setIcon(QMessageBox.Critical)
               txt = ('Please express all times in 24 hour convention without colons (e.g. 1310 for 1:10 in the afternoon)')
               msg.setText(txt)
               msg.setWindowTitle('Error')
               msg.setStandardButtons(QMessageBox.Ok)
               msg.show()
           else:

               try:

                   # Instantiate worker threads #
                   self.worker = DownloadVidThread(self.cameraName,self.yr,self.mo,self.day,self.hour,self.direc)
                     
                   self.lab1 = QLabel('Downloading Videos...')
                   self.grd.addWidget(self.lab1,11,0,1,1)

                   self.loadlab = QLabel()
                   self.loadmovie = QMovie(pth1+'loading.gif')
                   self.loadlab.setMovie(self.loadmovie)
                   
                   self.worker.start()
                   self.grd.addWidget(self.loadlab,11,1,1,1)
                   self.loadmovie.start()
                   self.worker.threadSignal.connect(self.on_threadSignal)
                   self.worker.finishSignal.connect(self.on_closeSignal)
               except AttributeError or ValueError:
                   self.contBut.setEnabled(True)
                   self.backBut.setEnabled(True)
                   
                   msg = QMessageBox(self)
                   msg.setIcon(QMessageBox.Critical)
                   txt = ('An error occured. Please ensure you have chosen a camera and selected a valid directory.')
                   msg.setText(txt)
                   msg.setWindowTitle('Error')
                   msg.setStandardButtons(QMessageBox.Ok)
                   msg.show()
                
           
       else:
           self.contBut.setEnabled(True)
           self.backBut.setEnabled(True)
           
           msg = QMessageBox(self)
           msg.setIcon(QMessageBox.Critical)
           txt = ('Please fill all fields.')
           msg.setText(txt)
           msg.setWindowTitle('Error')
           msg.setStandardButtons(QMessageBox.Ok)
           msg.show()
                  

    def on_threadSignal(self,numVid):
        self.lab1.setParent(None)
        self.lab1 = QLabel('Downloading video '+str(numVid)+' of '+str(len(self.yr)))
        self.grd.addWidget(self.lab1,11,0,1,1)
       

    def on_closeSignal(self):
         
       '''
       When download video(s) thread is done, function shows a done label and moves on
       '''
       badVid = []
       for i in range(0,len(self.yr)):
           if len(self.mo[i]) == 1:
               self.mo[i] = '0'+self.mo[i]
           if len(self.day[i]) == 1:
               self.day[i] = '0'+self.day[i]

           try:
               if os.stat(self.direc+'/'+self.cameraName+'.'+self.yr[i]+'-'+self.mo[i]+'-'+self.day[i]+'_'+self.hour[i]+'.mp4').st_size <1000:
                   badVid.append(i+1)
           except FileNotFoundError:
                   msg = QMessageBox(self)
                   msg.setIcon(QMessageBox.Critical)
                   txt = ('An error occured. Please ensure you have entered values for all fields correctly.')
                   msg.setText(txt)
                   msg.setWindowTitle('Error')
                   msg.setStandardButtons(QMessageBox.Ok)
                   msg.show()
                   
               
       if len(badVid)>0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            txt = ('Video number(s) '+str(badVid)+' do not exist.')
            msg.setText(txt)
            msg.setWindowTitle('Error')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.show()
       else:
            pass
       
       self.loadlab.setParent(None)
       self.backBut.setParent(None)
       self.contBut.setParent(None)
       self.loadmovie.stop()
       labDone = QLabel('Done.')
       self.grd.addWidget(labDone,11,1,1,1)

       beginBut = QPushButton('Back to start')
       self.grd.addWidget(beginBut,11,3,1,1)

       beginBut.clicked.connect(self.GoBack)

    def GoBack(self):
        
        self.close()
        self.w = WelcomeWindow()
        self.w.show()
       
#==============================================================================#
       
##============================================================================##
# Lidar data step: download lidar data near the camera #
##============================================================================##

class lidarData_FindUseableDatasetsWindow(QWidget):
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
       leftBar2 = QLabel('• Inputs and imagery')
       leftBar3 = QLabel('• Lidar data')
       leftBar4 = QLabel('• GCPs')
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
       qr = self.frameGeometry()
       lp = QDesktopWidget().availableGeometry().topLeft()
       qr.moveTopLeft(lp)
       self.move(qr.topLeft())        
       self.show()
       ############################


       if os.path.exists(pth+'products/lidarPC.pkl'):
           msg = QMessageBox(self)
           msg.setIcon(QMessageBox.Information)
           txt = ('Existing lidar point cloud for this camera found. Do you want to use it?')
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

            cmd = 'copy '+os.path.realpath(pth)+'\\'+'products\lidarPC.pkl '+os.path.realpath(pth1)+'\\lidarPC.pkl'
            os.system(cmd)

            self.close()
            self.w = PickGCPsWindow(pth+'products/lidarPC.pkl')
            self.w.show()
            
        else:

            f = open(pth+'_binaries/lidarTable.pkl','rb')
            lidarTable = pickle.load(f)

            self.close()
            self.lw = lidarData_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
            self.lw.resize(900,350)
            self.lw.show()


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
         
         self.lw = lidarData_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
         self.lw.resize(900,350)
         self.lw.show()
         
        
     def GoBack(self):
         '''
         Go back to camera choice window on Back click.
         '''
         self.close()
         self.backToOne = inputsAndImagery_UserInputs()        



class lidarData_ChooseLidarSetWindow(QWidget):
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
        leftBar2 = QLabel('• Inputs and imagery')
        leftBar3 = QLabel('• Lidar data')
        leftBar4 = QLabel('• GCPs')
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
        qr = self.frameGeometry()
        lp = QDesktopWidget().availableGeometry().topLeft()
        qr.moveTopLeft(lp)
        self.move(qr.topLeft())        
        self.show()
        ############################

        if os.path.exists(pth+'_binaries/linkToLidar.pkl'):
            f = open(pth+'_binaries/linkToLidar.pkl','rb')
            pthToLidar = pickle.load(f)
            
            self.close()
            self.w = PickGCPsWindow(pthToLidar)
            self.w.show()
        else:
        
            # Instantiate worker threads #
            f = open(pth+'_binaries/CameraLocation.pkl','rb')
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

        self.loadlab = QLabel()
        self.loadmovie = QMovie(pth1+'loading.gif')
        self.loadlab.setMovie(self.loadmovie)
        
        self.layout.addWidget(lab2,7,0,1,2)
        self.layout.addWidget(self.pb2,7,2,1,1)
        
        self.worker2.start()
        self.layout.addWidget(self.loadlab,7,3,1,1)
        self.loadmovie.start()
        self.worker2.finishSignal.connect(self.on_closeSignal2)
        
    def on_threadSignal2(self,perDone):
        self.pb2.setValue(perDone*100)
        
        
    def on_closeSignal2(self):
        '''
        Move to next task when lidar is downloaded.
        '''
        
        self.loadlab.setParent(None)

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
         
        self.lw = lidarData_ChooseLidarSetWindow(lidarTable,lidarTable.shape[0],lidarTable.shape[1])
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
        self.backToOne = inputsAndImagery_ChooseImage()
#==============================================================================#        


##============================================================================##
# GCPs step. Pick GCPs using the lidar data and image #
##============================================================================##

class PickGCPsWindow(QWidget):
   '''
   Window introducing the PickGCPs module and allowing the user to perform the GCP picking.
   '''
   
   def __init__(self,pthToSavedLidar=None):
        super().__init__()

        if pthToSavedLidar:
            self.pthToLidar = pthToSavedLidar
        else:
            self.pthToLidar = pth+'products/lidarPC.pkl'

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
        leftBar2 = QLabel('• Inputs and imagery')
        leftBar3 = QLabel('• Lidar data')
        leftBar4 = QLabel('• GCPs')
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
        self.img = mpimg.imread(pth+'products/calibrationImage.png')
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.format_coord = lambda x, y: ""
        self.ax.imshow(self.img)
        self.origxlim = self.ax.get_xlim()
        self.origylim = self.ax.get_ylim()
        self.canvas.draw()
            
        self.introLab = QLabel('Welcome to the GCP step! Here, you will be guided through the process of co-locating points '+
                               'in the image and the lidar observations. You must identify the correspondence of at least 3 unique points '
                               +'for the calibration to work.')
        self.introLab.setWordWrap(True)
        self.goLab = QLabel('Ready to co-locate points?')
        self.goBut = QPushButton('Go')
        self.navBar = self.NavToolbar(self.canvas,self)
        
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
        self.worker = pptkWindowWorker(self.pthToLidar)
        self.worker.finishSignal.connect(self.on_CloseSignal)
        self.worker.badSignal.connect(self.on_badSignal)
        self.worker2 = pickGCPs_Image(self.canvas)
        self.worker2.threadSignal.connect(self.on_ClickSignal)
        self.worker2.removeSignal.connect(self.on_RemoveSignal)
        ##############################
        
        
        # Full widget layout setup #
        fullLayout = QGridLayout()
        fullLayout.addWidget(leftGroupBox,0,0,2,2)
        fullLayout.addWidget(self.rightGroupBox,0,3,2,4)
        self.setLayout(fullLayout)

        self.setGeometry(400,100,1000,500)
        
        self.setWindowTitle('SurfRCaT')
        qr = self.frameGeometry()
        lp = QDesktopWidget().availableGeometry().topLeft()
        qr.moveTopLeft(lp)
        self.move(qr.topLeft())        
        self.show()
        ############################


   class NavToolbar(NavigationToolbar):
   
        toolitems = [t for t in NavigationToolbar.toolitems if
                     t[0] in ('Home','Pan','Zoom')]
        NavigationToolbar.update

 

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


       self.dirLab = QLabel('The lidar point cloud is opening in a seperate window- THIS CAN TAKE SEVERAL MINUTES. Press the HELP button for detailed instructions '+
                            'on identifying GCPs by clicking. Select the points you want to use as GCPs in the lidar point cloud (remember the order). When done, '+
                            'simply close the lidar window and then identify the corresponding points in the image.')
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
       f = open(pth+'_binaries/GCPs_lidar.pkl','rb') 
       iGCPs2 = pickle.load(f)
       
       self.dirLab.setParent(None)
       self.loadlab.setParent(None)
       self.helpBut.setParent(None)

       self.dirLab2 = QLabel('Real-world coordinates of points saved! Now, click on the points (in the same order) in the image. '+
                             'The image can be zoomed and panned using the navigation toolbar. You can revert clicks with a right-click. '+
                             'Press Done when finished.')
       self.dirLab2.setWordWrap(True)
       self.clicksLab = QLabel('0 of '+str(int(len(iGCPs2)))+' points identified')
       self.doneBut = QPushButton('Done')

       self.grd.addWidget(self.navBar,1,0,1,4)
       self.grd.addWidget(self.dirLab2,0,0,1,4)
       self.grd.addWidget(self.clicksLab,7,3,1,1)
       self.grd.addWidget(self.doneBut,8,3,1,1)
       self.grd.addWidget(self.helpBut,8,0,1,1)

       self.doneBut.clicked.connect(self.on_DoneClick)

       # Launch the image GCP picking process #
       self.points = []
       self.worker2.start()
 
   def on_ClickSignal(self,clicks):

       self.clicksLab.setParent(None)
       
       f = open(pth+'_binaries/GCPs_lidar.pkl','rb') 
       iGCPs2 = pickle.load(f)

       self.clicksLab = QLabel(str(int(clicks))+' of '+str(int(len(iGCPs2)))+' points identified')
       self.grd.addWidget(self.clicksLab,7,3,1,1)

       f = open(pth+'_binaries/GCPs_im.pkl','rb') 
       gcps = pickle.load(f)
       self.ax.plot(gcps[len(gcps)-1][0],gcps[len(gcps)-1][1],'ro')

   def on_RemoveSignal(self,clicks):
       
       self.ax.remove()
       self.ax = self.canvas.figure.subplots()
       self.ax.format_coord = lambda x, y: ""
       self.ax.imshow(self.img)

       f = open(pth+'_binaries/GCPs_im.pkl','rb') 
       gcps = pickle.load(f)
       if len(gcps)>0:
           for i in gcps:
               self.ax.plot(i[0],i[1],'ro')

       self.navBar.update()
       self.canvas.draw_idle()
       self.navBar.update()

       self.clicksLab.setParent(None)
       
       f = open(pth+'_binaries/GCPs_lidar.pkl','rb') 
       iGCPs2 = pickle.load(f)

       self.clicksLab = QLabel(str(int(clicks))+' of '+str(int(len(iGCPs2)))+' points identified')
       self.grd.addWidget(self.clicksLab,7,3,1,1)
       

   def on_badSignal(self):
       
       msg = QMessageBox(self)
       msg.setIcon(msg.Critical)
       msg.setText('An error occured. Please identify your GCPs again.')
       msg.setStandardButtons(msg.Ok)
       msg.buttonClicked.connect(self.onOkClick)
       msg.show()    


   def onOkClick(self):
       if os.path.exists(pth+'_binaries/linkToLidar.pkl'):
           f = open(pth+'_binaries/linkToLidar.pkl','rb')
           linkToLidar = pickle.load(f)

           self.close()
           self.w = PickGCPsWindow(linkToLidar)
           self.w.show()
       else:
           self.close()
           self.w = PickGCPsWindow()
           self.w.show()
       
   def onHelpClick(self):
       '''
       Show help if needed.
       '''
       
       msg = QMessageBox(self)
       msg.setIcon(msg.Question)
       msg.setText('The lidar point cloud will open in a separate window. The viewer can be navigated by (1) rotating (left click+drag), (2) '+
                   'panning (hold Shift and left click+drag), and (3) zooming (scroll wheel). Manipulate the view until you can identify the same features '+
                   'as in the image. Then, select your GCPs by: \n (1) Hold Control and left click on a point \n (2) Release Control and wait at least 3 seconds \n '+
                   '(3) Right click anywhere in the viewer \n (4) Repeat 1-3 for each GCP. \nRemember the order of the points you select.')
       msg.setStandardButtons(msg.Ok)
       msg.show()
       
               
   def on_DoneClick(self):
       '''
       Save the GCPs and display them to the user.
       '''
       
       self.dirLab2.setParent(None)
       self.doneBut.setParent(None)
       self.helpBut.setParent(None)

       self.ax.set_xlim(self.origxlim)
       self.ax.set_ylim(self.origylim)
       
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

       if os.path.exists(pth+'_binaries/linkToLidar.pkl'):
           f = open(pth+'_binaries/linkToLidar.pkl','rb')
           pthToLidar = pickle.load(f)
           
           self.close()
           self.a = PickGCPsWindow(pthToLidar)
           self.a.show()
       else:
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
# Calibrate step: Perform the non-linear least squares camera calibration #
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
        leftBar2 = QLabel('• Inputs and imagery')
        leftBar3 = QLabel('• Lidar data')
        leftBar4 = QLabel('• GCPs')
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
        img = mpimg.imread(pth+'products/calibrationImage.png')
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.imshow(img)
        self.canvas.draw()
        
        self.introLab = QLabel('Welcome to the Calibrate step! Press the CALIBRATE button below to perform the calibration.')
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
        qr = self.frameGeometry()
        lp = QDesktopWidget().availableGeometry().topLeft()
        qr.moveTopLeft(lp)
        self.move(qr.topLeft())        
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
        leftBar2 = QLabel('• Inputs and imagery')
        leftBar3 = QLabel('• Lidar data')
        leftBar4 = QLabel('• GCPs')
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
        img = mpimg.imread(pth+'products/calibrationImage.png')
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        self.ax.imshow(img)
        self.canvas.draw()
        
        # Plot the GCPs and reprojected positions #
        f1 = open(pth+'_binaries/GCPs_im.pkl','rb') 
        f2 = open(pth+'_binaries/GCPs_lidar.pkl','rb') 
        f3 = open(pth+'_binaries/calibVals.pkl','rb') 
       
        GCPs_im = pickle.load(f1); GCPs_im = np.array(GCPs_im)
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
        with open(pth+'_binaries/calibResid.pkl','wb') as f:
            pickle.dump(allResid,f)
        RMSresid = np.sqrt(np.mean(np.reshape(np.subtract(GCPs_im,uv),[np.size(np.subtract(GCPs_im,uv)),1])**2))
        
        self.introLab = QLabel('The reprojection of each picked GCP based on the calibration is shown below. The Xs should align with the Os '+
                               'if the calibration was accurate.')
        self.introLab.setWordWrap(True)
        self.residLab = QLabel('The RMS of the control point residuals for the calibration is '+str(round(RMSresid,3))+' pixels. A summary of the '+
                               'calibration has been saved as results\calibrationSummary.csv. If you are unhappy with the calibration, you can retry GCP picking'+
                               'by clicking the Retry button. Otherwise, click Continue to enter the rectification module.')
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
        qr = self.frameGeometry()
        lp = QDesktopWidget().availableGeometry().topLeft()
        qr.moveTopLeft(lp)
        self.move(qr.topLeft())        
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

        # Save the summary file #
        f_camName = open(pth+'_binaries/CameraName.pkl','rb')
        camName = pickle.load(f_camName)
        f_camLoc = open(pth+'_binaries/CameraLocation.pkl','rb')
        camLoc = pickle.load(f_camLoc)
        camX = str(camLoc[1])
        camY = str(camLoc[0])
        f_camz = open(pth+'_binaries/ZL.pkl','rb')
        camZ = str(pickle.load(f_camz))
        f_az = open(pth+'_binaries/az.pkl','rb')
        az = str(pickle.load(f_az))
        f_fl = open(pth+'_binaries/fl.pkl','rb')
        fl = pickle.load(f_fl)
        f_vidFile = open(pth+'_binaries/vidFile.pkl','rb')
        vidFile = pickle.load(f_vidFile)
        f_lidarID = open(pth+'_binaries/chosenLidarID.pkl','rb')
        lidarID = pickle.load(f_lidarID)
        f_gcps_lidar = open(pth+'_binaries/GCPs_lidar.pkl','rb')
        gcps_lidar = pickle.load(f_gcps_lidar)
        f_gcps_im = open(pth+'_binaries/GCPs_im.pkl','rb')
        gcps_lidar = pickle.load(f_gcps_im)
        f_calibVals = open(pth+'_binaries/calibVals.pkl','rb')
        calibVals = pickle.load(f_calibVals)
        f_resid = open(pth+'_binaries/calibResid.pkl','rb')
        calibResid = pickle.load(f_resid)
        rms = np.sqrt(np.sum(np.square(calibResid))/np.size(calibResid))
        
        Inputs_header = [['User inputs (all parameters with * are assumed by the tool)','','','','']]
        Inputs_camParams = [['','Camera parameters:','','',''],
                            ['','','Name',camName],
                            ['','','X',camX+u'\N{DEGREE SIGN}','Input longitude of camera (WGS84)'],
                            ['','','Y',camY+u'\N{DEGREE SIGN}','Input latitude of camera (WGS84)'],
                            ['','','Z',camZ+' m','Input elevation of camera (NAVD88)'],
                            ['','','azimuth',str(az)+u'\N{DEGREE SIGN}','Input azimuth of camera'],
                            ['','','tilt*','80'+u'\N{DEGREE SIGN}','Assumed tilt of camera'],
                            ['','','swing*','180'+u'\N{DEGREE SIGN}','Assumed swing of camera'],
                            ['','','focal length*',str(round(fl))+' pix','Assumed focal length (calibrated principal distance) of camera'],
                            ['','','x0*','0 pix','Assumed x-coordinate of camera principal point'],
                            ['','','y0*','0 pix','Assumed y-coordinate of camera principal point']]
        Inputs_videoParams = [['','Video parameters:','','',''],
                              ['','','video file name',vidFile,'']]
        Inputs_gcpParams = [['','GCP parameters:','','',''],
                            ['','','ID of chosen lidar dataset','ID '+str(lidarID),''],
                            ['','','num GCPs',str(len(gcps_lidar))+' GCPs','']]
        Outputs_header = [['Outputs','','','']]
        Outputs_camParams = [['','Adjusted camera parameters:','',''],
                             ['','','X',str(round(calibVals[3],2))+' m','Coordinates are meters east of input camera location'],
                             ['','','Y',str(round(calibVals[4],2))+' m','Coordinates are meters north of input camera location'],
                             ['','','Z',str(round(calibVals[5],2))+' m','Adjusted elevation of camera (NAVD88)'],
                             ['','','omega',str(round(calibVals[0],2))+' rad','Look angle 1, can be converted to azimuth,tilt,swing convention'],
                             ['','','phi',str(round(calibVals[1]))+' rad','Look angle 2, can be converted to azimuth,tilt,swing convention'],
                             ['','','kappa',str(round(calibVals[2],2))+' rad','Look angle 3, can be converted to azimuth,tilt,swing convention'],
                             ['','','focal length',str(round(calibVals[6],2))+' pix','Adjusted focal length (calibrated principal distance) of camera'],
                             ['','','x0',str(round(calibVals[7],2))+' pix','Adjusted x-coordinate of camera principal point'],
                             ['','','y0',str(round(calibVals[8],2))+' pix','Adjusted y-coordinate of camera principal point']]
        Outputs_accuracy = [['','Accuracy','','',''],
                            ['','','RMS GCP reprojection residual',str(round(rms,2))+' pix','']]
        Outputs_storage = [['','Storage','','',''],
                           ['','','calibration values file',pth+'_binaries/calibVals.pkl','Copy and paste this path in the Rectification module']]

        rows1 = [Inputs_header,Inputs_camParams,Inputs_videoParams,Inputs_gcpParams,Outputs_header,Outputs_camParams,Outputs_accuracy,Outputs_storage]
        rows = [item for sublist in rows1 for item in sublist]

        try:
            with open(pth+'results/calibrationSummary.csv','w') as f:
                writer = csv.writer(f,delimiter=',',lineterminator='\n')
                for i in rows:
                    writer.writerow(i)
            f.close()
        except PermissionError:
            msg = QMessageBox(self)
            msg.setIcon(msg.Question)
            msg.setText('Please close the file calibrationSummary.csv and try again.')
            msg.setStandardButtons(msg.Ok)
            msg.show()
        else:
            self.close()
            self.w = rectify_UserInputs()
            self.w.show()
        


##=========================================================================##
# Rectify step: rectify images based on calibration parameters #
##=========================================================================##
class rectify_UserInputs(QWidget):
   '''
   Window allowing the user to input everything needed to perform the rectification.
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
        leftBar2 = QLabel('• Inputs and imagery')
        leftBar3 = QLabel('• Lidar data')
        leftBar4 = QLabel('• GCPs')
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
        saveLab = QLabel('Directory to save frames:')
        self.saveBx = QLineEdit()
        browseBut00 = QPushButton('Browse')
        extractStillsBut = QPushButton('Extract Frames')
        dirLab1 = QLabel('Calibration results binary file:')
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
        introLab2 = QLabel('Real-world grid (x,y in meters relative to camera location; one z-value per image separated with commas):')
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
        self.contBut = QPushButton('Continue >')
        self.backBut = QPushButton('< Back')
        
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
        self.grd.addWidget(self.backBut,14,0,1,1)
        self.grd.addWidget(self.contBut,14,3,1,1)
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
        self.backBut.clicked.connect(self.onBackClick)
        self.contBut.clicked.connect(self.onContClick)
        ################################

        # Full widget layout setup #
        fullLayout = QHBoxLayout()
        fullLayout.addWidget(leftGroupBox)
        fullLayout.addWidget(self.rightGroupBox)
        self.setLayout(fullLayout)

        self.setWindowTitle('SurfRCaT')
        qr = self.frameGeometry()
        lp = QDesktopWidget().availableGeometry().topLeft()
        qr.moveTopLeft(lp)
        self.move(qr.topLeft())        
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
       
       self.w = inputsAndImagery_ExtractFrames(self.vidFile,saveDir,1)
       self.w.show()

   def onBrowse1Click(self):
       dlg = QFileDialog()
       dlg.setFileMode(QFileDialog.ExistingFile)
       dlg.setNameFilter('PKL files (*.pkl)')
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
        z1 = self.zBx.text()
        z1 = z1.split(',')

        if self.browsePresses<3 or self.xminBx.text()=='' or self.xmaxBx.text()=='' or self.dxBx.text()==''  or self.yminBx.text()=='' or self.ymaxBx.text()=='' or self.dyBx.text()=='' or self.zBx.text()=='':
            msg = QMessageBox(self)
            msg.setIcon(msg.Critical)
            msg.setText('Please fill all fields.')
            msg.setStandardButtons(msg.Ok)
            msg.show()
        elif os.path.splitext(self.calibFile)[1] != '.pkl':
            msg = QMessageBox(self)
            msg.setIcon(msg.Critical)
            msg.setText('Please input a valid calibration results binary file (.pkl).')
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
            z = [float(i) for i in z1]
            grd = [xmin,xmax,dx,ymin,ymax,dy,z]
            self.numIms = len(os.listdir(self.inputDirec))

            if len(z) != self.numIms:
                msg = QMessageBox(self)
                msg.setIcon(msg.Critical)
                msg.setText('Please input the same number of z-values as images ('+str(self.numIms)+')')
                msg.setStandardButtons(msg.Ok)
                msg.show()
            else:
                # Start the worker #
                self.worker = performRectificationThread(self.calibFile,self.inputDirec,self.outputDirec,grd)
                self.worker.threadSignal.connect(self.on_threadSignal)
                self.worker.badSignal.connect(self.on_badSignal)

                self.lab1 = QLabel('Performing rectification...')
                self.grd.addWidget(self.lab1,15,0,1,3)

                self.loadlab = QLabel()
                self.loadmovie = QMovie(pth1+'loading.gif')
                self.loadlab.setMovie(self.loadmovie)
               
                self.worker.start()
                self.grd.addWidget(self.loadlab,15,3,1,3)
                self.loadmovie.start()
                self.worker.finishSignal.connect(self.on_closeSignal)

            
   def on_badSignal(self):
       self.lab1.setParent(None)
       self.loadlab.setParent(None)

       msg = QMessageBox(self)
       msg.setIcon(msg.Critical)
       msg.setText('An error occured. Please ensure that your real-world grid is correct and you are using a valid calibration binary file.')
       msg.setStandardButtons(msg.Ok)
       msg.show()

   def on_threadSignal(self,num):

       self.lab1.setParent(None)
       
       self.lab1 = QLabel('Rectifying image '+str(num) +' of '+str(self.numIms)+'...')
       self.grd.addWidget(self.lab1,15,0,1,3)
       

   def on_closeSignal(self):
        '''
        Move to next window.
        '''
        self.loadlab.setParent(None)
        self.lab1.setParent(None)
        self.contBut.setParent(None)
        self.backBut.setParent(None)
        
        self.lab1 = QLabel('Done!')
        closeBut = QPushButton('Close')
        moreBut = QPushButton('Rectify more images')
        self.grd.addWidget(self.lab1,15,0,1,1)
        self.grd.addWidget(closeBut,15,3,1,1)
        self.grd.addWidget(moreBut,15,2,1,1)

        closeBut.clicked.connect(self.closeTool)
        moreBut.clicked.connect(self.doMore)

   def closeTool(self):        
        self.close()

   def doMore(self):
       self.close()
       self.w = rectify_UserInputs()
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

    def __init__(self,cam,year,month,day,hour,direc):
        super().__init__()
        self.cam = cam
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.direc = direc
        
    def run(self):
        
       print('Thread Started')

       vidNum = 0
       for i in range(0,len(self.year)):
           vidNum = vidNum+1
           self.threadSignal.emit(vidNum)
           try:           
               yr = int(self.year[i])
               mo = int(self.month[i])
               d = int(self.day[i])
               hr = int(self.hour[i])
           except:
               self.finishSignal.emit(1)

           if mo<10:
               mo = '0'+str(mo)
           else:
               mo = str(mo)
    
           if d<10:
               d = '0'+str(d)
           else:
               d = str(d)

           if hr<1000:
               hr = '0'+str(hr)
           else:
               hr = str(hr)

           print(self.direc+'/'+self.cam+'.'+str(yr)+'-'+str(mo)+'-'+str(d)+'_'+str(hr)+'.mp4')
           if not os.path.exists(self.direc+'/'+self.cam+'.'+str(yr)+'-'+str(mo)+'-'+str(d)+'_'+str(hr)+'.mp4'): # Only download if the file doesn't already exist #
               vidFile = SurfRCaT.GetWebCATVideo(self.direc+'/',self.cam,int(yr),int(mo),int(d),int(hr))
           else:
               pass
           
       self.finishSignal.emit(1)   
        
       print('Thread Done')
 
      
class DecimateVidThread(QThread):
    ''' 
    Worker thread to decimate video to images at user-specified rate.
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

       SurfRCaT.GetStills(self.vid,secondsPerFrame,self.rate,self.vidLen,self.fps,self.saveDir)

        
       self.finishSignal.emit(1) 
        
       print('Thread Done')
       
       
class getLidar_FindCloseDatasetIDsThread(QThread):

    '''
    Worker thread to find lidar datasets that may be close to the camera based on its state and coast.
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

                check = SurfRCaT.getLidar_TryID(ftp,alldirs,ID,self.cameraLoc_lat,self.cameraLoc_lon,pth+'_binaries/')
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

        self.threadSignal.emit(0)
        
        sf = SurfRCaT.getLidar_GetShapefile(IDToDownload)
        poly = SurfRCaT.getLidar_CalcViewArea(az,20,500,self.cameraLoc_lat,self.cameraLoc_lon)
        
        tilesKeep = list()
        i = 0
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
        with open(pth+'products/lidarPC.pkl','wb') as f:
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

    def __init__(self,pthToSavedLidar):
        super().__init__()
        self.pthToSavedLidar = pthToSavedLidar

        
    def run(self):
        
        print('Thread Started')

        # Save the point cloud in coords relative to this camera #
        f = open(pth1+'lidarPC.pkl','rb')
        pc = pickle.load(f)

        f = open(pth+'_binaries/CameraLocation.pkl','rb')
        camLoc = pickle.load(f)
        camLoc_utm = utm.from_latlon(camLoc[0],camLoc[1])
        
        pc['x'] = pc['x']-camLoc_utm[0]
        pc['y'] = pc['y']-camLoc_utm[1]
        
        with open(pth1+'lidarPC.pkl','wb') as f:
            pickle.dump(pc,f)
        
        # Delete any pre-existing GCP files if they exist #
        try:
            os.remove(pth+'results/GCPs_lidar.txt')
            os.remove(pth+'_binaries/GCPs_lidar.pkl')
            os.remove(pth+'results/GCPs_im.txt')
            os.remove(pth+'_binaries/GCPs_im.pkl')
        except OSError:
            pass
        try:
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

        # Re-save the point cloud in its native coordinates #
        f = open(pth1+'lidarPC.pkl','rb')
        pc1 = pickle.load(f)
        pc1['x'] = pc1['x']+camLoc_utm[0]
        pc1['y'] = pc1['y']+camLoc_utm[1]
        with open(pth1+'lidarPC.pkl','wb') as f:
            pickle.dump(pc1,f)
        

        # Load the output and create the GCPs from it #
        try:
            f = open(pth1+'Testing.txt','r') # This is a list of point indicies- not important for the user. #
        except FileNotFoundError:
            self.badSignal.emit(1)
        else:
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
                
                np.savetxt(pth+'products/GCPs_lidar.txt',GCPs_lidar)

                with open(pth+'_binaries/GCPs_lidar.pkl','wb') as f:
                    pickle.dump(GCPs_lidar,f)

                self.finishSignal.emit(1)    
                
                print('Thread Done')        



class pickGCPs_Image(QThread):

    '''
    Worker thread to allow GCP identification in the image
    '''

    threadSignal = pyqtSignal('PyQt_PyObject')
    removeSignal = pyqtSignal('PyQt_PyObject')
    finishSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,canvas):
        super().__init__()
        self.canvas = canvas

        self.press = False
        self.move = False
        
    def run(self):

        print('Thread Started')
        self.gcps_im = []

        def onPress(event):
            self.press = True
        def onMove(event):
            if self.press:
                self.move = True
        def onRelease(event):
            if self.press and not self.move:
                onclick(event)
            self.press = False
            self.move = False


        def onclick(event):
            
           if event.button == 1:
               ix,iy = event.xdata,event.ydata
      
               self.gcps_im.append([ix,iy])
               print(self.gcps_im)

               np.savetxt(pth+'products/GCPS_im.txt',self.gcps_im) 
                                  
               with open(pth+'_binaries/GCPs_im.pkl','wb') as f:
                   pickle.dump(self.gcps_im,f)

               clicks = len(self.gcps_im)
               self.threadSignal.emit(clicks)

               return
            
           elif event.button == 3:
               
               # Get rid of the last selected point in the GCP_im files #
               if len(self.gcps_im)>1:
                   self.gcps_im = self.gcps_im[0:len(self.gcps_im)-1]                   
               else:
                   self.gcps_im = []
               print(self.gcps_im)
               
               f = open(pth+'_binaries/GCPs_im.pkl','rb')
               gcp = pickle.load(f)
               if len(gcp)>1:
                   gcp = gcp[0:len(gcp)-1]
               else:
                   gcp = []
               with open(pth+'_binaries/GCPs_im.pkl','wb') as f:
                   pickle.dump(gcp,f)

               np.savetxt(pth+'products/GCPS_im.txt',self.gcps_im)

               clicks = len(gcp)
               self.removeSignal.emit(clicks)

               self.canvas.draw_idle()

               return

               
        while True:
            cid1 = self.canvas.mpl_connect('button_press_event',onPress)
            cid2 = self.canvas.mpl_connect('button_release_event',onRelease)
            cid3 = self.canvas.mpl_connect('motion_notify_event',onMove)
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
        
        img = cv2.imread(pth+'products/calibrationImage.png')
        gcps_im = pickle.load(f1); gcps_im = np.array(gcps_im)
        gcps_lidar = pickle.load(f2)
        az = pickle.load(f_az)
        ZL = pickle.load(f_ZL)
        
        
        # Get initial approximations for all remaining parameters #
        XL = 0 # We etablished this by creating the lidar point cloud relative to the camera's estimated location. #
        YL = 0
        fl,x0,y0 = SurfRCaT.calibrate_GetInitialApprox_IOPs(img)
        omega,phi,kappa = SurfRCaT.calibrate_GetInitialApprox_ats2opk(az,80,180)
        initApprox = np.array([omega,phi,kappa,XL,YL,ZL,fl,x0,y0])

        with open(pth+'_binaries/fl.pkl','wb') as f:
            pickle.dump(fl,f)        

        # Perform the calibration #
        calibVals1,So1 = SurfRCaT.calibrate_PerformCalibration(initApprox,np.array([0,0,0,1,1,1,0,0,0]),gcps_im,gcps_lidar)
        updatedApprox = calibVals1
        calibVals,So = SurfRCaT.calibrate_PerformCalibration(np.array([updatedApprox[0],updatedApprox[1],updatedApprox[2],initApprox[3],initApprox[4],initApprox[5],updatedApprox[6],updatedApprox[7],updatedApprox[8]]),np.array([1,1,1,0,0,0,1,1,1]),gcps_im,gcps_lidar)

        with open(pth+'_binaries/calibVals.pkl','wb') as f:
            pickle.dump(calibVals,f)

        f = open(pth+'_binaries/CameraLocation.pkl','rb')
        camLoc = pickle.load(f)        
        camLoc_x = utm.from_latlon(camLoc[0],camLoc[1])[0]
        camLoc_y = utm.from_latlon(camLoc[0],camLoc[1])[1]
        camLoc_utm = [camLoc_x,camLoc_y]
        zone = str(utm.from_latlon(camLoc[0],camLoc[1])[2])+utm.from_latlon(camLoc[0],camLoc[1])[3]

        with open(pth+'_binaries/CameraLocation_utm.pkl','wb') as f:
            pickle.dump(camLoc_utm,f)
        with open(pth+'_binaries/utmZone.pkl','wb') as f:
            pickle.dump(zone,f)
      
        self.finishSignal.emit(1)    

        print('Thread Done')



class performRectificationThread(QThread):
    
    '''
    Worker thread to perform the rectification.
    '''
        
    finishSignal = pyqtSignal('PyQt_PyObject')
    threadSignal = pyqtSignal('PyQt_PyObject')
    badSignal = pyqtSignal('PyQt_PyObject')

    def __init__(self,calibFile,inputDirec,outputDirec,grd):
        super().__init__()
        self.calibFile = calibFile
        self.inputDirec = inputDirec
        self.outputDirec = outputDirec
        self.grd = grd
        
    def run(self):

        print('Thread Started')

        f = open(self.calibFile,'rb')
        calibVals = pickle.load(f)
        images = os.listdir(self.inputDirec)

        num = 0
        for im in images:
            num = num+1
            self.threadSignal.emit(num)
            
            grdUse = [self.grd[0],self.grd[1],self.grd[2],self.grd[3],self.grd[4],self.grd[5],self.grd[6][num-1]] # Get this image's z-value #
            img = mpimg.imread(self.inputDirec+'/'+im)
            try:
                im_rectif,extents = SurfRCaT.rectify_RectifyImage(calibVals,img,grdUse) # Perform the rectification #
                    
            except:
                self.badSignal.emit(1)
                break
            else:
                
                # Get the rectified image back into real-world coordinates by adding the input camera location back in #
                try:
                    pth
                except:
                    f = open(self.calibFile.rsplit('/',1)[0]+'/CameraLocation_utm.pkl','rb')
                    f2 = open(self.calibFile.rsplit('/',1)[0]+'/utmZone.pkl','rb')
                    camLoc_utm = pickle.load(f)
                    utmZone = pickle.load(f2)
                else:
                    f = open(pth+'_binaries/CameraLocation_utm.pkl','rb')
                    f2 = open(pth+'_binaries/utmZone.pkl','rb')
                    camLoc_utm = pickle.load(f)
                    utmZone = pickle.load(f2)

                extents[0] = extents[0]+camLoc_utm[0]
                extents[1] = extents[1]+camLoc_utm[0]  
                extents[2] = extents[2]+camLoc_utm[1]
                extents[3] = extents[3]+camLoc_utm[1]
                ################################################################################################
                
                self.canvas = FigureCanvas(Figure()) # Save the rectified image #
                self.ax = self.canvas.figure.subplots()
                self.ax.imshow(im_rectif,extent=extents,interpolation='bilinear')
                self.ax.set_xlabel('UTM Zone '+utmZone+' Easting (m)')
                self.ax.set_ylabel('UTM Zone '+utmZone+' Northing (m)')
                self.ax.axis('equal')
                self.canvas.print_figure(self.outputDirec+'/'+os.path.splitext(im)[0]+'_rectif.png')

                # Save the rectified image as a .mat and .pkl #
                scipy.io.savemat(self.outputDirec+'/'+os.path.splitext(im)[0]+'_rectif.mat',{'x':np.arange(self.grd[0]+camLoc_utm[0],self.grd[1]+camLoc_utm[0],self.grd[2]),
                                                                                             'y':np.arange(self.grd[3]+camLoc_utm[1],self.grd[4]+camLoc_utm[1],self.grd[5]),
                                                                                             'I':im_rectif})
                im_rectif_dict = {'x':np.arange(self.grd[0]+camLoc_utm[0],self.grd[1]+camLoc_utm[0],self.grd[2]),'y':np.arange(self.grd[3]+camLoc_utm[1],self.grd[4]+camLoc_utm[1],self.grd[5]),'I':im_rectif}
                with open(self.outputDirec+'/'+os.path.splitext(im)[0]+'_rectif.pkl','wb') as f:
                    pickle.dump(im_rectif_dict,f)
                
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
