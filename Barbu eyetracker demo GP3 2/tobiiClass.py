#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 15:35:56 2021

@author: Barbu
"""

import tobii_research as tr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import csv
import random
import os
from psychopy import prefs
from psychopy.hardware import keyboard
prefs.hardware['audioLib'] = ['pygame']
from psychopy.tools.monitorunittools import (cm2pix, deg2pix, pix2cm,
                                             pix2deg)
from psychopy import event, visual, sound, core

from psychopy.preferences import prefs
prefs.general['shutdownKey'] = 'q'


class tobii:
    def __init__(self, psychopyWindow, 
                 eyetrackerID = 0, samplingRate = 60):        
        """Tobii controller for PsychoPy.
        
        tobii_research is required for this module.

        Args:
            psychopyWindow: psychopy.visual.Window object.
            eyetrackerID: the id of eyetracker. Default is 0 (use the first found eye-tracker).
            sampling rate: how many gaze data per second you want Tobii to output 
                valid sampling rates: 60, 120, 150, 300, 600 1200
                default: 60
        """
        
        self.psychopyWindow = psychopyWindow
        self.eyetrackerID = eyetrackerID
        self.initialTimestamp = tr.get_system_time_stamp()
        
        # ====================================================================
        # FIND THE REQUIRED EYETRACKER AND CONNECT TO IT    
        # ====================================================================
        # Find all eyetrackers
        # eyetrackers = [] #tr.find_all_eyetrackers()
        
        # Raise errors if not found
        timer = core.Clock()
        timer.add(30)
        
        while timer.getTime() < 0:
            eyetrackers = tr.find_all_eyetrackers()
            if eyetrackers:
                break
        
        if len(eyetrackers) == 0:
            raise RuntimeError("No eyetrackers found.")
    
        # Activate the one you want (0 is the default, if there's only 1 eyetracker)
        try:
            self.eyetracker = eyetrackers[self.eyetrackerID]
            
        except:
            raise ValueError(
                "Invalid eyetracker ID {}\n({} eyetrackers found)".format(
                    self.eyetrackerID, len(eyetrackers)))
            
        
        try:
            self.eyetracker.set_gaze_output_frequency(samplingRate)
        except:
            raise ValueError("Invalid sampling rate. Valid sampling rates are 60, 120, 150, 300, 600, 1200")
        
        # Set the CALIBRATION attribute to the one provided by Tobii
        self.calibration = tr.ScreenBasedCalibration(self.eyetracker)
        
        # Create an empty list for data storage
        self.gazeData = []
        
        # Create a parameter that tells Tobii whether to pause data collection
        self.recording = False
        
        # Create a parameter that tells the eyetracker what's happening on-screen
        self.currentEvent = None
        
        self.currentFolder = "Tobii/Calibration/"
        
    # ========================================================================
    # GAZE DATA FUNCTIONS  
    # ========================================================================
    def _on_gaze_data(self, gaze_data):
        """Callback function used by Tobii SDK. It appends the gaze data received
        to the gazeData list.

        Args:
            gaze_data: gaze data provided by the eye tracker.

        Returns:
            None
        """
        self.gazeData.append(gaze_data)
        self.gazeData[-1]['event'] = self.currentEvent
    
    def getGazeData(self):
        """
        Function that can send the stored gaze data to the main script.

        Returns
        -------
        Stored gaze data.

        """
        return self.gazeData
        
    def clearGazeData(self):
        """
        Clear the list of gaze data stored so far.

        Returns
        -------
        None.

        """
        self.gazeData = []
    
    def getLastGaze(self):
        """ Get the last gaze sent by the eyetracker.

        Parameters
        ----------
        None.

        Returns
        -------
        If the gaze data is valid, returns the x-y coordinates of the
        gaze in psychopy coordinates, averaged over both eyes.
        Otherwise, returns the 2-place tuple (np.nan, np.nan).
        """
        try: 
            gaze = self.gazeData[-1]
            lv = gaze["left_gaze_point_validity"]
            rv = gaze["right_gaze_point_validity"]
            lx, ly = gaze["left_gaze_point_on_display_area"]
            rx, ry = gaze["right_gaze_point_on_display_area"]
            
            lx, ly = self._get_psychopy_pos([lx, ly])
            rx, ry = self._get_psychopy_pos([rx, ry])
            
            if lv or rv:
                avgx = np.mean([x for x in [lx, rx] if not np.isnan(x)])
                avgy = np.mean([y for y in [ly, ry] if not np.isnan(y)]) 
    
                return (avgx, avgy)
    
            return (np.nan, np.nan)
        
        except:
            return (np.nan, np.nan)
        
    def setCurrentEvent(self, event):
        self.currentEvent = event
    
    def updateSystemTimestamp(self):
        self.initialTimestamp = tr.get_system_time_stamp()
    
    # ========================================================================
    # PSYCHOPY-TOBII CONVERSION FUNCTIONS
    # ========================================================================
    def _get_psychopy_pos(self, p):
        """Convert Tobii ADCS coordinates to PsychoPy coordinates.

        Args:
            p: Gaze position (x, y) in Tobii ADCS.

        Returns:
            Gaze position in PsychoPy coordinate systems. For example: (0,0).
        """
        
        if self.psychopyWindow.units == "norm":
            return (2 * p[0] - 1, -2 * p[1] + 1)
        elif self.psychopyWindow.units == "height":
            return ((p[0] - 0.5) * (self.psychopyWindow.size[0] / self.psychopyWindow.size[1]),
                    -p[1] + 0.5)
        elif self.psychopyWindow.units in ["pix", "cm", "deg", "degFlat", "degFlatPos"]:
            p_pix = ((p[0] - 0.5) * self.psychopyWindow.size[0],
                     (-p[1] + 0.5) * self.psychopyWindow.size[1])
            if self.psychopyWindow.units == "pix":
                return p_pix
            elif self.psychopyWindow.units == "cm":
                return (
                    pix2cm(p_pix[0], self.psychopyWindow.monitor),
                    pix2cm(p_pix[1], self.psychopyWindow.monitor),
                )
            elif self.psychopyWindow.units == "deg":
                return (
                    pix2deg(p_pix[0], self.psychopyWindow.monitor),
                    pix2deg(p_pix[1], self.psychopyWindow.monitor),
                )
            else:
                return pix2deg(np.array(p_pix),
                               self.psychopyWindow.monitor,
                               correctFlat=True)
        else:
            raise ValueError("unit ({}) is not supported.".format(
                self.psychopyWindow.units))

    def _get_tobii_pos(self, p):
        """Convert PsychoPy coordinates to Tobii ADCS coordinates.

        Args:
            p: Gaze position (x, y) in PsychoPy coordinate systems.

        Returns:
            Gaze position in Tobii ADCS. For example: (0,0).
        """

        if self.psychopyWindow.units == "norm":
            return ((p[0] + 1) / 2, (p[1] - 1) / -2)
        elif self.psychopyWindow.units == "height":
            return (p[0] * (self.psychopyWindow.size[1] / self.psychopyWindow.size[0]) + 0.5,
                    -p[1] + 0.5)
        elif self.psychopyWindow.units == "pix":
            return self._pix2tobii(p)
        elif self.psychopyWindow.units in ["cm", "deg", "degFlat", "degFlatPos"]:
            if self.psychopyWindow.units == "cm":
                p_pix = (cm2pix(p[0], self.psychopyWindow.monitor),
                         cm2pix(p[1], self.psychopyWindow.monitor))
            elif self.psychopyWindow.units == "deg":
                p_pix = (
                    deg2pix(p[0], self.psychopyWindow.monitor),
                    deg2pix(p[1], self.psychopyWindow.monitor),
                )
            elif self.psychopyWindow.units in ["degFlat", "degFlatPos"]:
                p_pix = deg2pix(np.array(p),
                                self.psychopyWindow.monitor,
                                correctFlat=True)

            return self._pix2tobii(p_pix)
        else:
            raise ValueError("unit ({}) is not supported".format(
                self.psychopyWindow.units))

    def _pix2tobii(self, p):
        """Convert PsychoPy pixel coordinates to Tobii ADCS.

            Called by _get_tobii_pos.

        Args:
            p: Gaze position (x, y) in pixels.

        Returns:
            Gaze position in Tobii ADCS. For example: (0,0).
        """
        return (p[0] / self.psychopyWindow.size[0] + 0.5, -p[1] / self.psychopyWindow.size[1] + 0.5)

    def _get_psychopy_pos_from_trackbox(self, p, units = None):
        """Convert Tobii TBCS coordinates to PsychoPy coordinates.

            Called by adjustPosition.

        Args:
            p: Gaze position (x, y) in Tobii TBCS.
            units: The PsychoPy coordinate system to use.

        Returns:
            Gaze position in PsychoPy coordinate systems. For example: (0,0).
        """

        if units is None:
            units = self.psychopyWindow.units

        if units == "norm":
            return (-2 * p[0] + 1, -2 * p[1] + 1)
        elif units == "height":
            return ((-p[0] + 0.5) * (self.psychopyWindow.size[0] / self.psychopyWindow.size[1]),
                    -p[1] + 0.4)
        elif units in ["pix", "cm", "deg", "degFlat", "degFlatPos"]:
            p_pix = (
                (-2 * p[0] + 1) * self.psychopyWindow.size[0] / 2,
                (-2 * p[1] + 1) * self.psychopyWindow.size[1] / 2,
            )
            if units == "pix":
                return tuple([round(p) for p in p_pix])
            elif units == "cm":
                return (
                    pix2cm(p_pix[0], self.psychopyWindow.monitor),
                    pix2cm(p_pix[1], self.psychopyWindow.monitor),
                )
            elif units == "deg":
                return (
                    pix2deg(p_pix[0], self.psychopyWindow.monitor),
                    pix2deg(p_pix[1], self.psychopyWindow.monitor),
                )
            else:
                return pix2deg(np.array(p_pix),
                               self.psychopyWindow.monitor,
                               correctFlat=True)
        else:
            raise ValueError("unit ({}) is not supported.".format(
                self.psychopyWindow.units))
    
    def adjustPosition(self, movieFileName = "calibrationMovie2.mov"):
        """Showing the participant's gaze position in track box.
        The red and green dots signal whether the participant is correctly
        positioned on the x- and y-axes (left-right, up-down).
        
        The green trackbar, together with the black rectangle, signals
        whether the participant is correctly positioned on the z-axis
        (back and forth).

        Args:
            None

        Returns:
            None
        """
        print("\n-------------------")
        print("Position adjustment started... Press SPACE to start the calibration.")                                
        print("-------------------\n")    
        
        
        self.setCurrentEvent("adjustPosition")

        movieSize = self.psychopyWindow.size
        moviePath = self.currentFolder + movieFileName
        # Initialize calibration movie (for adjusting position)
        mov = visual.MovieStim3(self.psychopyWindow, moviePath, size = movieSize, 
                                loop = True)

        # Circle representing the left eye position
        leye = visual.Circle(
            self.psychopyWindow,
            size = 0.05,
            lineColor = None,
            fillColor = "red",
            autoLog = False,
        )

        # Circle representing the right eye position
        reye = visual.Circle(
            self.psychopyWindow,
            size = 0.05,
            lineColor = None,
            fillColor = "red",
            autoLog = False,
        )

        # Trackbar for adjusting position on the z-axis (back-and-forth)
        zbar = visual.Rect(
            self.psychopyWindow,
            pos = (0, 0.4),
            width = 0.25,
            height = 0.03,
            lineColor = "green",
            fillColor = "green",
            autoLog = False,
        )
        
        # White rectangle representing the goal of positioning on the z-axis
        zc = visual.Rect(
            self.psychopyWindow,
            pos = (0, 0.4),
            width = 0.01,
            height = 0.03,
            lineColor = "white",
            fillColor = "white",
            autoLog = False,
        )

        # Black rectangle representing the actual position on the z-axis
        zpos = visual.Rect(
            self.psychopyWindow,
            pos = (0, 0.4),
            width = 0.008,
            height = 0.03,
            lineColor = "black",
            fillColor = "black",
            autoLog = False,
        )

        # Raise error if eyetracker hasn't been initalized
        if self.eyetracker is None:
            raise RuntimeError("Eyetracker is not found.")

        # Subscribe to data from the eyetracker in user_position mode
        self.eyetracker.subscribe_to(tr.EYETRACKER_USER_POSITION_GUIDE,
                                     self._on_gaze_data,
                                     as_dictionary=True)
        # Wait a bit for the eyetracker to get ready
        time.sleep(0.5)  
        
        adjusted = False

        # While not adjusted ('space' has not been pressed by the experimenter...)
        while not adjusted:
            
            # Start and keep playing the movie
            mov.draw()
            
            # Draw the z-axis goal
            zbar.draw()
            zc.draw()
            
            # get the last data the eyetracker received
            lastGaze = self.gazeData[-1]
            
            # Does the eyetracker find the participant?
            lv = lastGaze["left_user_position_validity"]
            rv = lastGaze["right_user_position_validity"]
            
            # Get the participant position x-y-z (trackbox coordinates)
            lx, ly, lz = lastGaze["left_user_position"]
            rx, ry, rz = lastGaze["right_user_position"]
            
            # If left valid, draw the left eye
            if lv:
                lx, ly = self._get_psychopy_pos_from_trackbox([lx, ly],
                                                              units="height")
                leye.setPos((lx * 0.25, 
                             ly * 0.25))
                
                # Green if close to the central position
                if abs(leye.pos[1]) < 0.1 and abs(leye.pos[0]) < 0.15:
                    leye.color = "green"
                    
                # Red otherwise
                else:
                    leye.color = "red"
                leye.draw()
                
            # Same for the right eye
            if rv:
                rx, ry = self._get_psychopy_pos_from_trackbox([rx, ry],
                                                              units="height")
                reye.setPos((rx * 0.25, 
                             ry * 0.25))
                if abs(reye.pos[1]) < 0.1 and abs(reye.pos[0]) < 0.15:
                    reye.color = "green"
                else:
                    reye.color = "red"
                reye.draw()
                
            # Draw the black rectangle to represent position back-and-forth
            if lv or rv:
                zpos.setPos((
                    (((lz * int(lv) + rz * int(rv)) /
                      (int(lv) + int(rv))) - 0.5) * 0.125, 0.4,
                ))
                zpos.draw()
            
            # Once participant is set, press 'space' to move on to calibration
            for key in event.getKeys():
                if key == "space":
                    mov.pause()
                    event.clearEvents()
                    adjusted = True
                    break
            
            self.psychopyWindow.flip()
        
        # Unsubscribe from the eyetracker
        self.eyetracker.unsubscribe_from(tr.EYETRACKER_USER_POSITION_GUIDE,
                                         self._on_gaze_data)
        
        # Delete the movie from memory
        del mov
        
        # Clear gaze data
        self.clearGazeData()
               
    def calibrate(self, numPoints = 5):
        """

        Parameters
        ----------
        numPoints : int, optional
            number of points to calibrate. The default is 5.

        Returns
        -------
        None.

        """
        # ====================================================================
        # Move calibration point function
        # ====================================================================
        
        kb = keyboard.Keyboard()
        
        def moveToNextPoint(calibStim, nextPoint, speed = 1/80):
            """Moves a stimulus from its current position to the position 
            given by next point.

            Args:
                calibStim: psychopy visual object to be moved.
                nextPoint: coordinates of the goal destination
                speed: speed of movement
    
            Returns:
                None
            """
            # Is the calibration smaller than 0.1?
            smallerThanTarget = calibStim.size[0] - 0.1 < 0
            
            # If yes, make it larger until it reaches default size
            if smallerThanTarget:
                while abs(calibStim.size[0] - 0.1) > 0.001:
                    calibStim.size *= 1.02
                    calibStim.ori += 4
                    calibStim.draw()
                    self.psychopyWindow.flip()
            
            # If not, make it smaller until it reaches default size
            elif calibStim.size[0] - 0.1 > 0:
                while abs(calibStim.size[0] - 0.1) > 0.01:   
                    calibStim.size /= 1.02
                    calibStim.ori -= 4
                    calibStim.draw()
                    self.psychopyWindow.flip()
            
            # Set back to default size (minor correction)
            calibStim.size = (0.1, 0.1)
            
            # Draw it
            calibStim.draw()
            
            time.sleep(0.2)
            
            # Calculate distance to next point on both x- and y-axis
            distanceToNextPoint = (nextPoint[0] - calibStim.pos[0], nextPoint[1] - calibStim.pos[1])
            
            # Get the distance to travel (straight)
            distanceToTravel = (distanceToNextPoint[0] ** 2 + distanceToNextPoint[1] ** 2)**0.5
            
            # Get time needed to get there
            timeToTravel = int(round(distanceToTravel/speed))
            
            # For the time it takes to travel there, move the stimulus in that direction while rotating it
            # for frame in range(timeToTravel):
            #     calibStim.pos += (distanceToNextPoint[0] / timeToTravel, 
            #                       distanceToNextPoint[1] / timeToTravel)
            #     calibStim.draw()
            #     calibStim.ori -= 4
                
            #     self.psychopyWindow.flip()
                
            #     # keys = kb.getKeys(['s'], waitRelease = True)
            #     if 's' in keys:
            #         break
                
            # Correct minor deviations
            calibStim.pos = nextPoint
            
        # ====================================================================
        # CALIBRATION PRELIMINARIES         
        # ====================================================================
        # Pause so you don't get data when eye is moving
        
        print("-------------------")
        print("Calibration started... Advancement is automatic. Press 's' to skip calibration.")                                
        print("-------------------\n")    
        
        self.setCurrentEvent("stimulusMovement")
        
        calibrationPoints = [(0.5, 0.5), (0.1, 0.1), (0.9, 0.1),  
                             (0.1, 0.9), (0.9, 0.9)]
        
        # Select points based on number of points passed to the function
        calibrationPoints = calibrationPoints[:numPoints] 
            
        # # Choose curtain
        # curtainPath = self.currentFolder + "curtain.png"
                
        # # Load curtain
        # curtain = visual.ImageStim(self.psychopyWindow, curtainPath, 
        #                            size = self._get_psychopy_pos((1, 0))) 
        # curtain.size *= 2
        
        # Change psychopy window color background
        # self.psychopyWindow.color = "#fafafa"
        
        # Load stimulus sound
        calibSound = sound.Sound(self.currentFolder + "calibrationSound.wav")
        
        # The colors in which calibStim happens to come in
        colors = ["Red", "Green", "Blue", "Yellow", "Pink"]
        
        # Color of first stimulus
        currentColor = random.choice(colors)
        
        # Create the stimulus
        calibStim = visual.ImageStim(self.psychopyWindow, 
                                     self.currentFolder + "calibration" + currentColor + ".png", 
                                     size = (0.1, 0.1), 
                                     interpolate = True)

        # # Raise the curtain        
        # curtain.pos = (0, 0)
            
        # for frame in range(150):
        #     curtain.pos += (0, 1/150)
        #     calibStim.ori += 4
        #     calibStim.draw()
        #     curtain.draw()
        #     self.psychopyWindow.flip()
        
        # curtain.pos = (0, 1)
       
        # Connect to Tobii                 
        self.eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, 
                                     self._on_gaze_data,
                                     as_dictionary = True)
    
        # Enter calibration mode
        self.calibration.enter_calibration_mode()
        
        self.updateSystemTimestamp()
        
        # Randomize order of calibration points (once)
        np.random.shuffle(calibrationPoints)
        
            
        # For all points, draw them in one of the calibrated points           
        for point in calibrationPoints:
            keys = kb.getKeys(['s'], waitRelease = True)
            if 's' in keys:
                break
                
            # Make a copy of the color list, so you don't mutate the original one
            colorCopy = colors[:]
            
            # MOVE TO NEXT POINT
            moveToNextPoint(calibStim, self._get_psychopy_pos(point))
            
            if 's' in keys:
                break
            
            # Remove the current color, so you can change the color of the
            # Stimulus with a new one
            colorCopy.remove(currentColor)
            
            # Choose a new color
            currentColor = random.choice(colorCopy)
            
            # Load the differently-colored stimulus in the same position
            calibStim = visual.ImageStim(self.psychopyWindow, 
                        self.currentFolder + "calibration" + currentColor + ".png", 
                         size = calibStim.size, 
                         pos = calibStim.pos,
                         ori = calibStim.ori,
                         interpolate = True)
            
            # Play the sound
            calibSound.play()
            
            # Refresh the window
            calibStim.draw()           
            self.psychopyWindow.flip()
        
            if 's' in keys:
                break    
        
            # Shrink stimulus
            while calibStim.size[0] > 0.04:                        
                calibStim.size /= 1.02
                calibStim.ori -= 4
                calibStim.draw()
                self.psychopyWindow.flip()
            
            self.setCurrentEvent("fixation")
            time.sleep(0.2)
            
            
            # frame = 0
            # while True:
                
            #     if (frame // 45) % 2 == 0:
            #         calibStim.size *= 1.02
            #     else:
            #         calibStim.size /= 1.02
                    
            #     if event.getKeys(['space']):
            #         event.clearEvents()
            #         self.setCurrentEvent("stimulusMovement")
            #         break
                
            #     calibStim.ori -= 4
            #     calibStim.draw()
            #     self.psychopyWindow.flip()
            #     frame += 1
            
            if 's' in keys:
                break   
            
            
            print("------")
            print("Collecting data at {0}.".format(point))
            collectResult = self.calibration.collect_data(point[0], point[1])
            print(collectResult)
            print("------")
            # if collectResult != tr.CALIBRATION_STATUS_SUCCESS:
            #     collectResult = self.calibration.collect_data(point[0], point[1])
            self.setCurrentEvent("stimulusMovement")
            if 's' in keys:
                break   
            


        
            
            
        # # Lower the curtain after calibration
        # curtain.pos = (0, 1)
        
        # for frame in range(150):
        #     curtain.pos -= (0, 1/150)
        #     calibStim.ori += 4
        #     calibStim.draw()
        #     curtain.draw()
        #     self.psychopyWindow.flip()
        
        # curtain.pos = (0, 0)
        event.clearEvents()
        
        calibrationResult = self.calibration.compute_and_apply()
        
        self.psychopyWindow.flip()
        
        print("-------------------")    
        print("Compute and apply returned {0} and collected at {1} points.".format(calibrationResult.status, 
                                                                              len(calibrationResult.calibration_points)))   
        print("-------------------\n")    
        self.calibration.leave_calibration_mode()
        self.eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA)
    
    def writeToFile(self, filename, ID, expOrder, trialNumber):        
        if not os.path.isfile(filename):
            header = ["timestamp", 
                      "ID", "expOrder",
                      "trialNumber",
                      "event", 
                      "lv", "lx", "ly",
                      "lpv", "lps", 
                      "rv", "rx", "ry",
                      "rpv", "rps"]
            
            with open(filename, 'w', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow(header)
        
        for gaze in self.gazeData:
            
            # System timestamp
            timestamp = (gaze["system_time_stamp"] - self.initialTimestamp) / 1e3
            event = gaze["event"]
            
            # LEFT EYE DATA
            # Validity
            lv = gaze["left_gaze_point_validity"]
            
            # x-avis
            lx = gaze["left_gaze_point_on_display_area"][0]
            
            # y-axis
            ly = gaze["left_gaze_point_on_display_area"][1]
            
            # Pupil validity
            lpv = gaze["left_pupil_validity"]
            lps = gaze["left_pupil_diameter"]
            
            # RIGHT EYE DATA
            rv = gaze["right_gaze_point_validity"]
            rx = gaze["right_gaze_point_on_display_area"][0]
            ry = gaze["right_gaze_point_on_display_area"][1]
            rpv = gaze["right_pupil_validity"]
            rps = gaze["right_pupil_diameter"]
            
            # Convert tobii to psychopy
            lx, ly = self._get_psychopy_pos([lx, ly])
            rx, ry = self._get_psychopy_pos([rx, ry])
            
            # Data row to be written to csv file
            data = [timestamp, 
                    ID, expOrder, 
                    trialNumber, 
                    event,
                    lv, lx, ly,
                    lpv, lps,
                    rv, rx, ry,
                    rpv, rps]        
            
            # Write to csv file
            with open(filename, 'a', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow(data) 
        
    def generateCalibrationPlot(self, filename):          
        calibDF = pd.read_csv(filename, 
                              usecols = ['event', 'lx', 'ly', 'rx', 'ry'])
        
        calibDF = calibDF.loc[calibDF["event"] == "fixation"]
        
        ax = calibDF.plot(kind = 'scatter', x = "lx", y = "ly", 
                          color = "lightblue", label = "left") 
        
        calibDF.plot(kind = 'scatter', x = "rx", y = "ry", 
                    color = "darkblue", label = "right", ax = ax)

        ax.set_xlabel("x-coord")
        ax.set_ylabel("y-coord")
        ax.legend(loc = "center right")
        ax.set_xlim([-1, 1])
        ax.set_ylim([-0.7, 0.7])

        plt.savefig(filename[:-3] + "png")
    
    def startRecording(self):
        self.recording = True
        self.setCurrentEvent("startRecording")
        self.eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, 
                             self._on_gaze_data,
                             as_dictionary = True)
        time.sleep(0.5)
    
    def stopRecording(self):
        self.recording = False
        self.eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA)