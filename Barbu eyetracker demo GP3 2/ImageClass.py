#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 19 15:07:21 2022

@author: Barbu
"""
import os
import datetime
import random
import pandas as pd, numpy as np
from psychopy.hardware import keyboard

import sys
sys.path.insert(1, os.getcwd()) # TODO: make agnostic

from experimentClass import Experiment

from psychopy import visual, sound, core, event, constants

class ViennaFestival(Experiment):
    def __init__(self,
                  psychopyWindow,
                  experimenterWindow,
                  usingEyetracker = True):

        super().__init__(psychopyWindow,
                         experimenterWindow,
                         usingEyetracker = usingEyetracker)
        self.datetime = str(datetime.datetime.now())[:10] + "_" + str(datetime.datetime.now())[11:13] + "." + str(datetime.datetime.now())[14:16]
        self.calibrationFile = os.path.join("Data", "S" + str(1) + "_" + self.datetime + "_calibration.csv")
        self.imageFolder = "Images"+os.sep
        self.movieFolder = "Movies" + os.sep
        self.soundFolder = "Sounds" + os.sep
        self.items = []
        self.ID = 1
        self.expOrder = 1
        self.gazeDot = visual.Circle(self.psychopyWindow,
                                  radius = 0.1,
                                  pos = (0, 0),
                                  opacity = 0.25,
                                  size = 0.3,
                                  lineColor = 'white',
                                  fillColor = 'green')

        # Screen parameters
        self.screenResolution = self.psychopyWindow.size
        self.screenRatio = self.screenResolution[0]/self.screenResolution[1]
        self.xMax = self.screenRatio / 2
        self.yMax = 0.5

    def addItem(self, item):
        self.items.append(item)

    def removeItem(self, item):
        self.items.remove(item)

    def clearItems(self):
        self.items = []

    def draw(self):
        for i in range(0, len(self.items)):
            try:
                self.items[i].draw()
            except:
                print("Could not draw item at index " + str(i))
        #for item in self.items:
        #    item.draw()

    def flip(self):
        self.psychopyWindow.flip()
        self.experimenterWindow.flip()

    def drawFlip(self):
        self.draw()
        self.flip()

    def imageDissolve(self, images):
        # Start eyetracker
        if self.usingEyetracker:
            #self.eyetracker.updateSystemTimestamp()
            self.eyetracker.setRecordingState(True)
            self.eyetracker.enableEventReporting(True)

        print("\n")
        print("--------------------")
        print("Dissolve Image started. Press SPACE to advance to next image or Q to go back to task choice.")
        print("--------------------")
        print("\n")

        self.psychopyWindow.color = "black"
        random.shuffle(images)


        for image in images:

            self.img = visual.ImageStim(self.psychopyWindow, self.imageFolder + image,
                                       size = [1.6, 2 * self.yMax])

            self.items.append(self.img)

            width = 0.2

            for x in np.arange(-0.8 + width/2, 0.8 + width/2, width):
                for y in np.arange(-self.yMax + width/2, self.yMax + width/2, width):

                    r = visual.rect.Rect(self.psychopyWindow,
                                     width = width,
                                     height = width,
                                     lineWidth = 1,
                                     lineColor = 'white',
                                     lineColorSpace = None,
                                     fillColor = 'black',
                                     fillColorSpace = None,
                                     pos = (x, y),
                                     size = None,
                                     opacity = None)

                    self.items.append(r)
            self.gazeDot = visual.Circle(self.psychopyWindow,
                                  radius = 0.1,
                                  pos = (0, 0),
                                  opacity = 0.25,
                                  size = 0.3,
                                  lineColor = 'white',
                                  fillColor = 'green')
            self.items.append(self.gazeDot)



            kb = keyboard.Keyboard()

            for frame in range(3600):
                avgx, avgy = self.eyetracker.getLastGazePosition()
                avgx = avgx/1080
                avgy = avgy/1080
                self.gazeDot.pos = (avgx, avgy)
                keys = event.getKeys(['space', 'q'])

                if 'space' in keys:
                    break

                if 'q' in keys:
                    self.clearItems()
                    #kb.clearEvents()
                    self.draw()
                    self.flip()
                    if self.eyetracker:
                        self.eyetracker.setRecordingState(False)
                    return


                if not np.isnan(avgx) and not np.isnan(avgy) and -0.8 < avgx < 0.8 and -0.5 < avgy < 0.5:
                    blackX = int(np.floor((avgx + 0.8) * 1/width))
                    blackY = int(np.floor((avgy + 0.5) * 1/width))
                    self.items[5 * blackX + blackY + 1].opacity = 0

                # print(avgx, avgy)
                self.draw()
                self.flip()

                foundOpaque = False
                for elem in self.items[1:-1]:
                    if elem.opacity != 0:
                        foundOpaque = True
                        break

                if not foundOpaque:
                    break

            #kb.clearEvents()
            self.clearItems()
            self.draw()
            self.flip()


        if self.eyetracker:
            self.eyetracker.setRecordingState(False)


    def fruitMaze(self):
        # Start eyetracker
        if self.usingEyetracker:
            #self.eyetracker.updateSystemTimestamp()
            self.eyetracker.setRecordingState(True)
            self.eyetracker.enableEventReporting(True)

        print("\n")
        print("--------------------")
        print("Fruit Maze started. Press Q to go back to task choice.")
        print("--------------------")
        print("\n")

        self.psychopyWindow.color = "white"

        # ====================================================================
        # Load Objects
        # ====================================================================
        anim = random.choice(["bear", "rabbit"])


        # Animal
        animal = visual.ImageStim(self.psychopyWindow,
                                     self.imageFolder + anim + ".png")
        if anim == "bear":

            fruit = visual.ImageStim(self.psychopyWindow,
                                     self.imageFolder + "raspberry.png")
            fruit.size *= 0.15

        else:
            fruit = visual.ImageStim(self.psychopyWindow,
                                     self.imageFolder + "carrot.png")
            fruit.size *= 0.2

        animal.size *= 0.4

        # Found fruit?
        found = False

        # Create board
        width = 0.25

        for x in np.arange(-0.75 + width/2, 0.75 + width/2, width):
            for y in np.arange(-self.yMax + width/2, self.yMax + width/2, width):

                r = visual.rect.Rect(self.psychopyWindow,
                                 width = width,
                                 height = width,
                                 lineWidth = 1,
                                 lineColor = 'black',
                                 lineColorSpace = None,
                                 fillColor = 'white',
                                 fillColorSpace = None,
                                 pos = (x, y),
                                 size = None,
                                 opacity = None)

                self.items.append(r)

        # Sounds
        moveSound = sound.Sound(self.soundFolder + "xylophone.wav")
        eatSound = sound.Sound(self.soundFolder + "eatSound.wav")

        # ====================================================================
        # Initiate Positions
        # ====================================================================
        a = random.choice(list(range(4)))

        if a == 0:
            # Animal in lower left quadrant
            animalX = random.randint(0, 1)
            animalY = random.randint(0, 1)

            # Fruit in upper right quadrant
            fruitX = random.randint(4, 5)
            fruitY = random.randint(2, 3)

        elif a == 1:
            # Animal in upper left quadrant
            animalX = random.randint(0, 1)
            animalY = random.randint(2, 3)

            # Fruit in lower right quadrant
            fruitX = random.randint(4, 5)
            fruitY = random.randint(0, 1)

        elif a == 2:
            # Animal in lower right quadrant
            animalX = random.randint(4, 5)
            animalY = random.randint(0, 1)

            # Fruit in upper left quadrant
            fruitX = random.randint(0, 1)
            fruitY = random.randint(2, 3)

        elif a == 3:
            # Animal in upper right quadrant
            animalX = random.randint(4, 5)
            animalY = random.randint(2, 3)

            # Fruit in lower left quadrant
            fruitX = random.randint(0, 1)
            fruitY = random.randint(0, 1)

        currentAnimalCell = (animalX, animalY)
        fruitCell = (fruitX, fruitY)
        self.gazeDot.size *= 0.5



        def matrixToPsychopy(cell):
            psyX = cell[0] * width - 0.75
            psyY = cell[1] * width - 0.5
            return (psyX, psyY)

        def psychopyToMatrix(avgx, avgy):
            x = int(np.floor((avgx + 0.75) * 1/width))
            y = int(np.floor((avgy + 0.5) * 1/width))
            return (x, y)

        def psychopyPosition(cell):
            psyX, psyY = matrixToPsychopy(cell)

            return(psyX + 0.125, psyY + 0.125)

        def matrixToIndex(cell):
            return 4 * cell[0] + cell[1]

        def indexToMatrix(index):
            b = index % 4
            a = (index - b) // 4
            return (a, b)

        animal.pos = psychopyPosition(currentAnimalCell)
        fruit.pos = psychopyPosition(fruitCell)

        def validMoves(currentCell):
            currentX, currentY = currentCell
            validCells = []
            for x in [-1, 1]:
                candidateX = currentX + x
                if candidateX >= 0 and candidateX <= 5:
                    validCells.append((candidateX, currentY))
            for y in [-1, 1]:
                candidateY = currentY + y
                if candidateY >= 0 and candidateY <= 3:
                    validCells.append((currentX, candidateY))

            return validCells


        def createGraph():
            cells = {}

            for node in range(24):
                cells[node] = []
                cell = indexToMatrix(node)
                possibleMoves = validMoves(cell)

                for move in possibleMoves:
                    cells[node].append(matrixToIndex(move))

            return cells

        cells = createGraph()

        def getWallDirection(cell1, cell2):
            if cell1[0] == cell2[0]:
                return "horizontal"
            else:
                return "vertical"



        def createWallBetweenCells():
            wallsAdded = 0

            while True:
                cellOne = random.randint(0, 23)
                if cells[cellOne]:
                    cellTwo = random.choice(cells[cellOne])
                    break

            # remove path from graph
            cells[cellOne].remove(cellTwo)
            cells[cellTwo].remove(cellOne)

            cellA = indexToMatrix(cellOne)
            cellB = indexToMatrix(cellTwo)

            if cellA[0] != cellB[0]:
                wall = visual.rect.Rect(self.psychopyWindow,
                                 width = 0.01,
                                 height = width,
                                 lineWidth = 1,
                                 lineColor = 'black',
                                 fillColor = 'black',
                                 pos = (0, 0))

                wall.pos = psychopyPosition(cellA)
                wall.pos += psychopyPosition(cellB)
                wall.pos /= 2

            else:
                wall = visual.rect.Rect(self.psychopyWindow,
                                 width = width,
                                 height = 0.01,
                                 lineWidth = 1,
                                 lineColor = 'black',
                                 fillColor = 'black',
                                 pos = (0, 0))

                wall.pos = psychopyPosition(cellA)
                wall.pos += psychopyPosition(cellB)
                wall.pos /= 2

            self.items.append(wall)
            wallsAdded += 1

            try:
                if abs(cellOne - cellTwo) == 1:
                    if cellOne < 4 or cellTwo < 4:
                        cellThree = cellOne + 4
                        cellFour = cellTwo + 4
                    else:
                        cellThree = cellOne - 4
                        cellFour = cellTwo - 4

                else:
                    if cellOne % 4 == 0 or cellTwo % 4 == 0:
                        cellThree = cellOne + 1
                        cellFour = cellTwo + 1
                    else:
                        cellThree = cellOne - 1
                        cellFour = cellTwo - 1

                # remove path from graph
                cells[cellThree].remove(cellFour)
                cells[cellFour].remove(cellThree)

                cellA = indexToMatrix(cellThree)
                cellB = indexToMatrix(cellFour)

                if cellA[0] != cellB[0]:
                    wall = visual.rect.Rect(self.psychopyWindow,
                                     width = 0.01,
                                     height = width,
                                     lineWidth = 1,
                                     lineColor = 'black',
                                     fillColor = 'black',
                                     pos = (0, 0))

                    wall.pos = psychopyPosition(cellA)
                    wall.pos += psychopyPosition(cellB)
                    wall.pos /= 2

                else:
                    wall = visual.rect.Rect(self.psychopyWindow,
                                     width = width,
                                     height = 0.01,
                                     lineWidth = 1,
                                     lineColor = 'black',
                                     fillColor = 'black',
                                     pos = (0, 0))

                    wall.pos = psychopyPosition(cellA)
                    wall.pos += psychopyPosition(cellB)
                    wall.pos /= 2

                self.items.append(wall)
                wallsAdded += 1

            except:
                pass

            return wallsAdded

        def isReachable(currentAnimalCell, fruitCell):
            animalIndex = matrixToIndex(currentAnimalCell)
            fruitIndex = matrixToIndex(fruitCell)

            # Mark all the vertices as not visited
            visited = [False] * (24)

            # Create a queue for BFS
            queue = []

            # Mark the source node as visited and enqueue it
            queue.append(animalIndex)
            visited[animalIndex] = True

            while queue:

                # Dequeue a vertex from queue
                n = queue.pop(0)

                # If this adjacent node is the destination node,
                # then return true
                if n == fruitIndex:
                       return True

                #  Else, continue to do BFS
                for i in cells[n]:
                    if visited[i] == False:
                        queue.append(i)
                        visited[i] = True

            # If BFS is complete without visited d
            return False



        # Draw walls
        while True:
            wallsAdded = 0
            for i in range(5):
                wallsAdded += createWallBetweenCells()

            if isReachable(currentAnimalCell, fruitCell):
                break

            else:
                cells = createGraph()
                for i in range(wallsAdded):
                    self.items.pop(-1)

        # self.items.append(self.gazeDot)
        self.items.append(animal)
        self.items.append(fruit)

        def getGazeCell(avgx, avgy):
            return psychopyToMatrix(avgx, avgy)

        def validGazeMove(gazeCell, currentAnimalCell):
            gazeCellIndex = matrixToIndex(gazeCell)
            animalCellIndex = matrixToIndex(currentAnimalCell)

            return gazeCellIndex in cells[animalCellIndex]

        def move(currentAnimalCell, currentGazeCell, fruitCell):
            currentX, currentY = currentAnimalCell
            nextX, nextY = currentGazeCell
            foundFruit = currentGazeCell == fruitCell

            # vertical movement
            if currentX == nextX:
                for frame in range(25):
                    animal.pos += (0, 0.01 * (nextY - currentY))
                    if foundFruit and frame >= 17:
                        fruit.opacity -= 0.125
                    self.drawFlip()
            else:
                for frame in range(25):
                    animal.pos += (0.01 * (nextX - currentX), 0)
                    if foundFruit and frame >= 17:
                        fruit.opacity -= 0.125
                    self.drawFlip()

            moveSound.play()
            return foundFruit

        def jump():
            movement = 0.0015
            for frame in range(20):
                animal.pos += (0, movement)
                self.drawFlip()

            for frame in range(20):
                    animal.pos -= (0, movement)
                    self.drawFlip()

            for frame in range(20):
                    animal.pos += (0, movement)
                    self.drawFlip()

            for frame in range(20):
                    animal.pos -= (0, movement)
                    self.drawFlip()


        def highlight(cell):
            index = matrixToIndex(cell)

            highlighted = self.items[index]

            if highlighted.opacity == 1.0:
                highlighted.opacity = 0
                highlighted.fillColor = 'orange'

                for frame in range(30):
                    highlighted.opacity += 0.01
                    self.draw()
                    animal.draw()
                    self.flip()

        def checkPersistence(cell):
            for frame in range(10):
                avgx, avgy = self.eyetracker.getLastGazePosition()
                avgx = avgx/1080
                avgy = avgy/1080
                self.gazeDot.pos = (avgx, avgy)

                if not np.isnan(avgx) and not np.isnan(avgy):
                    currentCell = getGazeCell(avgx, avgy)
                    self.drawFlip()
                    if cell != currentCell:
                        return False
            return True

        kb = keyboard.Keyboard()
        #kb.clearEvents()

        while not found:
            avgx, avgy = self.eyetracker.getLastGazePosition()
            avgx = avgx/1080
            avgy = avgy/1080

            self.gazeDot.pos = (avgx, avgy)

            keys = event.getKeys(['q'])

            if 'q' in keys:
                self.gazeDot.size *= 2
                self.clearItems()
                self.drawFlip()
                if self.eyetracker:
                    self.eyetracker.setRecordingState(False)
                return


            if not np.isnan(avgx) and not np.isnan(avgy) and -0.75 < avgx < 0.75 and -0.5 < avgy < 0.5:

                gazeCell = getGazeCell(avgx, avgy)

                if validGazeMove(gazeCell, currentAnimalCell):

                    persist = checkPersistence(gazeCell)
                    if persist:
                        foundFruit = move(currentAnimalCell, gazeCell, fruitCell)
                        if foundFruit:
                            highlight(gazeCell)
                            break
                        highlight(gazeCell)
                        currentAnimalCell = gazeCell

            self.drawFlip()

        eatSound.play()

        jump()

        print("Fruit found. Press Q to go back to choice menu.")

        kb = keyboard.Keyboard()
        #kb.clearEvents()

        while True:
            keys = event.getKeys(['q'])
            self.drawFlip()

            if 'q' in keys:
                self.gazeDot.size *= 2
                self.clearItems()
                self.drawFlip()

                if self.eyetracker:
                    self.eyetracker.setRecordingState(False)

                print("--------------------")
                print("\n")
                return


    def bananas(self):

        def pause():
            print("\n")
            print("--------------------")
            print("Paused. Press SPACE to replay Bananas with gaze data.")
            print("--------------------")
            self.psychopyWindow.color = "white"
            self.draw()
            self.flip()
            self.draw()
            self.flip()
            #kb.clearEvents()

            while True:
                keys = event.getKeys(['space'])
                if 'space' in keys:
                    return

        def getGazePos(row):
            lv = row["lv"]
            rv = row["rv"]
            lx = row["lx"]
            ly = row["ly"]
            rx = row["rx"]
            ry = row["ry"]

            if lv or rv:
                avgx = np.mean([x for x in [lx, rx] if not np.isnan(x)])
                avgy = np.mean([y for y in [ly, ry] if not np.isnan(y)])

            else:
                avgx, avgy = -2, -2

            return (avgx, avgy)


        print("\n")
        print("--------------------")
        print("Playing Bananas. Press Q to quit.")
        print("--------------------")

        # Initialize keyboard
        kb = keyboard.Keyboard()
        #kb.clearEvents()

        # Datafiles to write to
        dateTime = str(datetime.datetime.now())[:10] + "_" + str(datetime.datetime.now())[11:13] + "." + str(datetime.datetime.now())[14:16]
        experimentFile = os.path.join("Data", "S1" + "_" + dateTime + "_eyeData.csv")

        # Start eyetracker
        if self.eyetracker:
            #self.eyetracker.updateSystemTimestamp()
            self.eyetracker.setRecordingState(True)
            self.eyetracker.enableEventReporting(True)

        movie1 = visual.MovieStim(self.psychopyWindow,
                                     self.movieFolder + 'fam.mov',
                                     size = (1920, 1080))

        movie2 = visual.MovieStim(self.psychopyWindow,
                                 self.movieFolder + 'test1.mov',
                                 size = (1920, 1080))

        movie3 = visual.MovieStim(self.psychopyWindow,
                                 self.movieFolder + 'test2.mov',
                                 size = (1920, 1080))

        # For-loop for all trials
        for trialNumber in range(1, 4):
            attention = visual.MovieStim(self.psychopyWindow,
                                         self.movieFolder + 'ball.mov',
                                         size = (1920, 1080))


            # ====================================================================
            # ATTENTION GETTER
            # ====================================================================
            #if self.eyetracker:
                #self.eyetracker.setCurrentEvent("attentionGetter") #TODO FIX


            self.items.append(attention)

            while attention.status != constants.FINISHED:
                keys = event.getKeys(['q'])
                if 'q' in keys:
                    self.eyetracker.setRecordingState(False)
                    self.clearItems()
                    return

                self.drawFlip()

            self.items.remove(attention)
            # ====================================================================
            # MOVIE
            # ====================================================================
            if self.eyetracker:
                self.eyetracker.setCurrentEvent("movie")

            done = False

            if trialNumber == 1:
                movie = movie1
            elif trialNumber == 2:
                movie = movie2
            else:
                movie = movie3

            self.items.append(movie)

            while movie.status != constants.FINISHED and not done:
                keys = event.getKeys(['q'])
                if 'q' in keys:
                    self.eyetracker.setRecordingState(False)
                    self.clearItems()
                    return
                self.drawFlip()

            movie.pause()

            # Write data at the end of the trial
            #if self.eyetracker:
                #self.eyetracker.setCurrentEvent("endTrial")
                #self.eyetracker.writeToFile(experimentFile, 1,1,trialNumber)
                #self.eyetracker.setCurrentEvent("preTrial")
                #self.eyetracker.updateSystemTimestamp()
                #self.eyetracker.clearGazeData()

            self.items.remove(movie)

        if self.eyetracker:
            self.eyetracker.setRecordingState(False)

        pause()

        # =============================================================================
        # REPLAY
        # =============================================================================
        print("\n")
        print("--------------------")
        print("Replaying Bananas with gaze data. Press Q to quit.")
        print("--------------------")

        movie1 = visual.MovieStim(self.psychopyWindow,
                                     self.movieFolder + 'fam.mov',
                                     size = (1920, 1080))

        movie2 = visual.MovieStim(self.psychopyWindow,
                                 self.movieFolder + 'test1.mov',
                                 size = (1920, 1080))

        movie3 = visual.MovieStim(self.psychopyWindow,
                                 self.movieFolder + 'test2.mov',
                                 size = (1920, 1080))


        gazeDot = visual.Circle(self.psychopyWindow,
                                  radius = 0.1,
                                  pos = (0, 0),
                                  opacity = 0.5,
                                  size = 0.2,
                                  lineColor = 'black',
                                  fillColor = 'black')

        df = pd.read_csv(experimentFile)
        self.items.append(gazeDot)

        # for-loop for all trials
        for trialNumber in range(1, 4):
            attention = visual.MovieStim(self.psychopyWindow,
                                         self.movieFolder + 'ball.mov',
                                         size = (1920, 1080))

            dfTrial = df.loc[df["trialNumber"] == trialNumber]

            if trialNumber == 1:
                movie = movie1
            elif trialNumber == 2:
                movie = movie2
            else:
                movie = movie3


            # ====================================================================
            # ATTENTION GETTER
            # ====================================================================
            dfAttention = dfTrial.loc[dfTrial["event"] == "attentionGetter"]

            self.items.append(attention)

            for index, row in dfAttention.iterrows():
                keys = event.getKeys(['q'])
                if 'q' in keys:
                    self.clearItems()
                    return

                gazeDot.pos = getGazePos(row)
                attention.draw()
                self.drawFlip()

            attention.pause()

            # ====================================================================
            # MOVIE
            # ====================================================================
            # self.items.insert(0, movie)
            # self.items.remove(attention)

            dfTest = dfTrial.loc[dfTrial["event"] == "movie"]

            for index, row in dfTest.iterrows():
                keys = event.getKeys(['q'])
                if 'q' in keys:
                    self.clearItems()
                    return

                movie.draw()
                gazeDot.pos = getGazePos(row)
                self.drawFlip()

            movie.pause()

            # self.items.remove(movie)

        self.clearItems()

    def playPauseMovie(self, movie):
        # Start eyetracker
        if self.usingEyetracker:
            #self.eyetracker.updateSystemTimestamp()
            self.eyetracker.setRecordingState(True)

        print("Play/Pause Movie started. Press Q to go back to task choice.")


        self.psychopyWindow.color = "white"
        self.psychopyWindow.close()

        kb = keyboard.Keyboard()
        #kb.clearEvents()

        items = []

        playWindow = visual.Window(size = (600, 1080),
                                   pos = (0, 0),
                                    screen = 1, fullscr = False,
                                       units = 'height',
                                       color = 'white',
                                       colorSpace = "rgb",
                                       winType = "pyglet",
                                       waitBlanking = False,
                                       allowGUI = False)


        # Play Button
        playBox = visual.Circle(playWindow,
                            radius = 0.3,
                            pos = (0, 0),
                            opacity = 0.1,
                            size = 0.3,
                            lineColor = 'white',
                            fillColor = 'gray')

        items.append(playBox)
        playButton = visual.polygon.Polygon(playWindow,
                                            edges = 3,
                                            opacity = 0.25,
                                            ori = 90,
                                            pos = (0, 0),
                                            size = (0.1),
                                            lineColor = "black",
                                            fillColor = "black")
        items.append(playButton)

        pauseWindow = visual.Window(size = (600, 1080),
                                   pos = (1320, 0),
                                    screen = 1, fullscr = False,
                                       units = 'height',
                                       color = 'white',
                                       colorSpace = "rgb",
                                       winType = "pyglet",
                                       waitBlanking = False,
                                       allowGUI = False)

        pauseBox = visual.Circle(pauseWindow,
                            radius = 0.3,
                            pos = (0, 0),
                            opacity = 0.1,
                            size = 0.3,
                            lineColor = 'white',
                            fillColor = 'gray')

        items.append(pauseBox)

        pauseButton1 = visual.rect.Rect(pauseWindow,
                                        width = 0.01,
                                        height = 0.1,
                                        opacity = 0.25,
                                        ori = 0,
                                        pos = (-0.015, 0),
                                        lineColor = "black",
                                        fillColor = "black")
        items.append(pauseButton1)

        pauseButton2 = visual.rect.Rect(pauseWindow,
                                        width = 0.01,
                                        height = 0.1,
                                        opacity = 0.25,
                                        ori = 0,
                                        pos = (0.015, 0),
                                        lineColor = "black",
                                        fillColor = "black")
        items.append(pauseButton2)

        movieWindow = visual.Window(size = (960, 540),
                                    screen = 1, fullscr = False,
                                       units = 'height',
                                       color = 'white',
                                       colorSpace = "rgb",
                                       winType = "pyglet",
                                       waitBlanking = False,
                                       allowGUI = False)

        movie = visual.MovieStim(movieWindow, self.movieFolder + movie,
                                  loop = False, size = (960, 540))


        def refresh():
            for item in items:
                item.draw()
            playWindow.flip()
            pauseWindow.flip()

        playing = False
        for frame in range(30):
            refresh()
            movie.pause()
            #movieWindow.flip()

        durationFixation = 15

        while movie.status != constants.FINISHED:

            keys = event.getKeys(['q'])
            if 'q' in keys:
                break

            avgx, avgy = self.eyetracker.getLastGazePosition()
            avgx = avgx/1080
            avgy = avgy/1080

            if 0.5 < avgx < 8/9 and abs(avgy) < 0.4 and playing:
                keys = event.getKeys(['q'])
                for frame in range(durationFixation):
                    if 'q' in keys:
                        break
                    avgx, avgy = self.eyetracker.getLastGazePosition()
                    avgx = avgx/1080
                    avgy = avgy/1080
                    if not (0.5 < avgx < 1 and abs(avgy) < 0.4):
                        break
                    if frame == durationFixation - 1:
                        playing = False
                        movie.pause()
                        playButton.opacity = 0.25
                        pauseButton1.opacity = 1
                        pauseButton2.opacity = 1

                    else:
                        movie.draw()
                        movieWindow.flip()

                    refresh()

            elif -8/9 < avgx < -0.5 and abs(avgy) < 0.4 and not playing:
                keys = event.getKeys(['q'])
                for frame in range(durationFixation):
                    if 'q' in keys:
                        break
                    avgx, avgy = self.eyetracker.getLastGazePosition()
                    avgx = avgx/1080
                    avgy = avgy/1080
                    if not (-8/9 < avgx < -0.5 and abs(avgy) < 0.4):
                        break

                    if frame == durationFixation - 1:
                        movie.play()
                        playing = True
                        playButton.opacity = 1
                        pauseButton1.opacity = 0.25
                        pauseButton2.opacity = 0.25

            elif playing:
                movie.draw()
                movieWindow.flip()

            refresh()

        movieWindow.close()
        playWindow.close()
        pauseWindow.close()


        self.psychopyWindow = visual.Window(size = (1920, 1080),
                                       screen = 1, fullscr = True,
                                       units = 'height',
                                       color = 'black',
                                       colorSpace = "rgb",
                                       winType = "pyglet",
                                       waitBlanking = False,
                                       allowGUI = False)

        if self.eyetracker:
            self.eyetracker.setRecordingState(False)

    def chooseNextTask(self):

        self.psychopyWindow.color = "#ADD8E6"

        # txt = visual.TextStim(self.psychopyWindow, text = "...", color = "black")
        # self.items.append(txt)

        self.draw()
        self.flip()

        self.draw()
        self.flip()

        print("--------------------")
        print("Choose next task: \n 1 = Dissolve Images; \n 2 = Play/Pause Movie; \n 3 = Fruit Maze; \n 4 = Bananas Experiment; \n 9 = Exit")
        print("--------------------")

        kb = keyboard.Keyboard()
        #kb.clearEvents()

        while True:

            keys = event.getKeys(['9', '1', '2', '3', '4'])
            if '9' in keys:
                self.clearItems()
                return False
            elif '1' in keys:
                self.clearItems()
                images = ["img1.jpeg", "img2.jpeg", "img3.jpeg", "img4.jpeg", "img5.jpeg", "img6.jpeg"]
                self.imageDissolve(images)
                return True
            elif '2' in keys:
                self.clearItems()
                self.playPauseMovie("piper.mp4")
                return True
            elif '3' in keys:
                self.clearItems()
                self.fruitMaze()
                return True
            elif '4' in keys:
                self.clearItems()
                self.bananas()
                return True
