#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 15:50:36 2021

@author: Barbu
"""
import os, pandas as pd
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import tobiiClass
from psychopy import visual, sound, event
from psychopy.hardware import keyboard


class Experiment:
    def __init__(self, 
                 psychopyWindow, 
                 experimenterWindow,
                 usingEyetracker = True):
        
        self.psychopyWindow = psychopyWindow
        self.experimenterWindow = experimenterWindow
        
        if usingEyetracker:
            self.usingEyetracker = True
            self.eyetracker = tobiiClass.tobii(self.psychopyWindow)
            self.calibrationAttempt = 1
            self.calibrationSong = sound.Sound("Tobii/Calibration/calibrationSong.wav")
        
        else:
            self.usingEyetracker = False
            self.eyetracker = None
            
    def adjustPosition(self, movieFileName = "calibrationMovie2.mov"):
        self.eyetracker.adjustPosition(movieFileName)

    def calibrate(self, numPoints = 5):

            
        if self.calibrationAttempt == 1:
            self.calibrationSong.play()
        
        
        self.eyetracker.calibrate(numPoints)
        self.eyetracker.writeToFile(self.calibrationFile,
                                    self.ID, self.expOrder,
                                    self.calibrationAttempt)
        
        
        # display calibration points
        calibStim = visual.ImageStim(self.experimenterWindow, 
            "Tobii/Calibration/calibrationGray.png",
             size = (0.03, 0.03), 
             interpolate = True)
        
        calibrationPoints = [(0.5, 0.5), (0.1, 0.1), (0.9, 0.1),  
                             (0.1, 0.9), (0.9, 0.9)]
        
        calibDF = pd.read_csv(self.calibrationFile, 
                              usecols = ['event', 'lx', 'ly', 'rx', 'ry'])
        
        calibDF = calibDF.loc[calibDF["event"] == "fixation"]
        
        for point in calibrationPoints:
            calibStim.pos = self.eyetracker._get_psychopy_pos(point)
            calibStim.draw()
        
        for index, row in calibDF.iterrows():
            if index % 2 == 0:
                lx = row['lx']
                ly = row['ly']
                rx = row['rx']
                ry = row['ry']
                
                gazeDotLeft = visual.Circle(self.experimenterWindow, 
                                      radius = 0.01,
                                      pos = (lx, ly),
                                      opacity = 1,
                                      lineColor = 'darkblue',
                                      fillColor = 'darkblue')
                gazeDotRight = visual.Circle(self.experimenterWindow, 
                          radius = 0.01,
                          pos = (rx, ry),
                          opacity = 1, 
                          lineColor = 'lightblue',
                          fillColor = 'lightblue')
                
                gazeDotLeft.draw()
                gazeDotRight.draw()
        
        self.experimenterWindow.flip()

        print("-------------------")         
        print("Are you happy with calibration? [y/n] ")
        happy = event.waitKeys(keyList = ["y", "Y", "n", "N"])
        
        if happy[0].lower() == "y":
            print("Calibration successful. Moving on...")
            print("-------------------\n")
            self.calibrationSong.stop()
            self.experimenterWindow.flip()
        
        else:
            self.eyetracker.clearGazeData()
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
                self.adjustPosition()
                self.calibrate(numPoints = numPoints)
            
            elif nextStep[0].lower() == "a":
                print("\n")
                print("Starting all over...")
                self.experimenterWindow.flip()
                self.calibrationSong.stop()
                self.adjustPosition()
                # self.calibrate(numPoints = numPoints)
        
        self.eyetracker.clearGazeData()
        
            
    def getCalibrationImage(self):        
        self.eyetracker.generateCalibrationPlot(self.calibrationFile)
        stimSize = self.psychopyWindow.size[0]/self.psychopyWindow.size[1]
        
        calibration = visual.ImageStim(self.experimenterWindow,
                                       self.calibrationFile[:-3] + "png",
                                       size = stimSize,
                                       interpolate = True)
        
        return calibration