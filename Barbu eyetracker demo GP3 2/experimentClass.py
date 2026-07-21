#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# "Experiment" class: eyetracker setup + calibration


"""
Created on Thu Oct 14 15:50:36 2021
Updated on Tue Apr 14 2026

@author: Barbu, Jonathan
"""
import os, pandas as pd
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

#import tobiiClass
from psychopy import visual, sound, event, core
from psychopy.hardware import keyboard
from psychopy.iohub import launchHubServer

class Experiment:
    def __init__(self,
                 psychopyWindow,
                 experimenterWindow,
                 usingEyetracker = True):

        self.psychopyWindow = psychopyWindow
        self.experimenterWindow = experimenterWindow

        if usingEyetracker:
            self.usingEyetracker = True

            # iohub_config.yaml Declares the monitor, keyboard, mouse — and critically, the eyetracker.hw.gazepoint.gp3.EyeTracker block (enable: True), which is the one active tracker definition (other trackers like SMI/LC Technologies are commented out). This file is what makes launchHubServer actually talk to your specific GP3 device.

            self.io=launchHubServer(iohub_config_name='iohub_config.yaml') # you are reliant on an external .yaml file.
            #This .yaml file contains information about both the monitor and the eye-tracker. The program will not work without it, and it must be named exactly this.
            #This is the only way to get it to present everything on the correct monitor: in the config file, make sure under "Display", device_number is set to 1

            display=self.io.devices.display
            self.eyetracker=self.io.devices.tracker
            #print tracker
            if self.eyetracker.isConnected():
                print('connected, whatever else happens')
            else:
                print('failed to establish connection, stopping')
                self.io.quit()
                quit()
            #self.eyetracker = tobiiClass.tobii(self.psychopyWindow)
            self.calibrationAttempt = 1
            self.calibrationSong = sound.Sound("Tobii/Calibration/calibrationSong.wav")

        else:
            self.usingEyetracker = False
            self.eyetracker = None

    #def adjustPosition(self, movieFileName = "calibrationMovie2.mov"):
    #    self.eyetracker.adjustPosition(movieFileName)

    def calibrate(self, numPoints = 5):



        self.psychopyWindow.close()
        core.wait(1)
        if self.calibrationAttempt == 1:
            self.calibrationSong.play()
        try:
            calib = self.eyetracker.runSetupProcedure()
            if calib == False:
                self.io.quit()
                quit()
        except:
            self.io.quit()
            core.quit()
            quit()
        core.wait(.2)
        resolution = (1920, 1080)

        # Open main window
        self.psychopyWindow = visual.Window(size = resolution,
                               screen = 1, fullscr = True,
                               units = 'height',
                               color = 'black',
                               colorSpace = "rgb",
                               winType = "pyglet",
                               waitBlanking = False,
                               allowGUI = False)
        self.eyetracker.setRecordingState(True)
        self.eyetracker.enableEventReporting(True)

        circArray = []
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[-.3,-.3], lineColor='white', fillColor='white'))
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[0,-.3], lineColor='white', fillColor='white'))
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[.3,-.3], lineColor='white', fillColor='white'))
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[-.3,0], lineColor='white', fillColor='white'))
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[0,0], lineColor='white', fillColor='white'))
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[.3,0], lineColor='white', fillColor='white'))
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[-.3,.300], lineColor='white', fillColor='white'))
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[0,.300], lineColor='white', fillColor='white'))
        circArray.append(visual.Circle(self.psychopyWindow, radius=.025,pos=[.300,.300], lineColor='white', fillColor='white'))
        circEyes = visual.Circle(self.psychopyWindow, radius = .05, lineColor='red', fillColor='red')


        self.experimenterWindow.flip()

        print("-------------------")
        print("Are you happy with calibration? [y/n] ")
        happy = event.getKeys(keyList = ["y", "Y", "n", "N"])
        while happy == []:
            gpos = self.eyetracker.getLastGazePosition()
            if type(gpos) in [tuple, list]:
                circEyes.pos = [gpos[0]/resolution[1], gpos[1]/resolution[1]]
                #print(gpos)
            else:
                circEyes.pos = [0,0]
            circEyes.draw()
            for i in range (0, len(circArray)):
                circArray[i].draw()
            self.psychopyWindow.flip()
            happy = event.getKeys(keyList = ["y", "Y", "n", "N"])


        if happy[0].lower() == "y":
            print("Calibration successful. Moving on...")
            print("-------------------\n")
            self.calibrationSong.stop()
            self.experimenterWindow.flip()

        else:
            self.calibrationAttempt += 1
            print("Unsuccessful calibration.")
            print("Should we recalibrate or start all over? \n Press 'c' to recalibrate, 'z' to start all over, 'a' to adjust the position and skip the recalibration: ")
            nextStep = event.waitKeys(keyList = ["c", "C", "z", "Z", "a", "A"])

            if nextStep[0].lower() == "c":
                print("\n")
                print("Starting recalibration... \n")
                self.experimenterWindow.flip()
                self.calibrate(numPoints = numPoints)

            elif nextStep[0].lower() == "z":
                print("\n")
                print("Starting all over...")
                self.experimenterWindow.flip()
                self.calibrationAttempt = 1
                self.calibrationSong.stop()
                #self.adjustPosition()
                self.calibrate(numPoints = numPoints)

            elif nextStep[0].lower() == "a":
                print("\n")
                print("Starting all over...")
                self.experimenterWindow.flip()
                self.calibrationSong.stop()
                #self.adjustPosition()
                # self.calibrate(numPoints = numPoints)



    # def getCalibrationImage(self):
    #     self.eyetracker.generateCalibrationPlot(self.calibrationFile)
    #     stimSize = self.psychopyWindow.size[0]/self.psychopyWindow.size[1]

    #     calibration = visual.ImageStim(self.experimenterWindow,
    #                                    self.calibrationFile[:-3] + "png",
    #                                    size = stimSize,
    #                                    interpolate = True)

    #     return calibration
