from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
import random
from Words import * 
from textrecognition import *

#Kinect framework code from Kinect Workshop

class GamePlay(object):
    def __init__(self):
        self.mode = "startScreen"
        self.gameOver = False
        self.playAgain = False
        self.guessed = set() #stores letters the player has already guessed 
        self.pointList = [] #stores positions of hand while drawing a letter 
        self.dictionary = Words() #has words to choose from 
        self.win = False
        self.doneDrawing = False
        #the following will be handled in handleStartScreen(), based on what difficulty level is chosen 
        self.wordToGuess = ""
        self.difficultyLevel = -1
        self.guessesLeft = -1
        self.currentWord = [] #stores the current state of the word that the player has reached 
        self.mergedSurface = None

    def handleStartScreen(self, runGame):
        #process Kinect data
        rightHandX = -1 #start out with the position of the hand negative 
        #loop until a difficulty Level is chosen 
        while self.difficultyLevel == -1:
            # We have a color frame. Fill out back buffer surface with frame's data 
            if runGame._kinect.has_new_color_frame():
                frame = runGame._kinect.get_last_color_frame()
                runGame.draw_color_frame(frame, runGame._frame_surface)
                frame = None

            if runGame._kinect.has_new_body_frame(): 
                runGame._bodies = runGame._kinect.get_last_body_frame()

                if runGame._bodies is not None: 
                    for i in range(0, runGame._kinect.max_body_count):
                        body = runGame._bodies.bodies[i]
          
                        if not body.is_tracked: 
                            continue
                        joints = body.joints 
                        #convert the points in 3d space to a point on the screen  
                        joint_points = runGame._kinect.body_joints_to_color_space(joints)
                        #open right hand in area of screen corresponding to difficulty level 
                        if joints[PyKinectV2.JointType_HandTipRight].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open:
                            rightHandX = joint_points[PyKinectV2.JointType_HandRight].x
                        #assign difficulty level based on hand position 
                        if rightHandX != -1:
                            if 0 <= rightHandX <= runGame.screen_width//3:
                                self.difficultyLevel = 1
                            elif runGame.screen_width//3 < rightHandX <= 2 * runGame.screen_width//3:
                                self.difficultyLevel = 2
                            else:
                                self.difficultyLevel = 3
            #draw lines to signify boundaries of areas to choose from 
            pygame.draw.line(runGame._frame_surface, (152,66,244), (runGame.screen_width//3, 0), (runGame.screen_width//3, runGame.screen_height), 25)
            pygame.draw.line(runGame._frame_surface, (152,66,244), (2*runGame.screen_width//3, 0), (2*runGame.screen_width//3, runGame.screen_height), 25)
            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(runGame._frame_surface.get_height()) / runGame._frame_surface.get_width()
            target_height = int(h_to_w * runGame._screen.get_width())
            surface_to_draw = pygame.transform.scale(runGame._frame_surface, (runGame._screen.get_width(), target_height));
            runGame._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()
            runGame._clock.tick(60)

        print(self.difficultyLevel)
        self.wordToGuess = self.dictionary.words[self.difficultyLevel][random.randint(0, len(self.dictionary.words[self.difficultyLevel]) - 1)]
        print(self.wordToGuess)
        self.currentWord = ["_"] * len(self.wordToGuess)
        self.guessesLeft = self.difficultyLevel * 5 
        self.mode = "play"
    
    def handlePlayMode(self, runGame): 
        imageWidth = 720
        imageHeight = 405 
        repeatImage = 4
        print(self.doneDrawing)
        #keep running as long as the game is not over
        while not self.gameOver:
            #handle kinect input as long as the player is drawing 
            xPoints = []
            yPoints = []
            while not self.doneDrawing:
                # We have a color frame. Fill out back buffer surface with frame's data 
                if runGame._kinect.has_new_color_frame():
                    frame = runGame._kinect.get_last_color_frame()
                    runGame.draw_color_frame(frame, runGame._frame_surface)
                    frame = None

                if runGame._kinect.has_new_body_frame(): 
                    runGame._bodies = runGame._kinect.get_last_body_frame()

                    if runGame._bodies is not None: 
                        for i in range(0, runGame._kinect.max_body_count):
                            body = runGame._bodies.bodies[i]

                            if not body.is_tracked: 
                                continue
                            '''else:
                                if runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Closed:
                                    print("closed")
                                elif (runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open):
                                    print("open")
                                elif (runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Lasso):
                                    print("lasso")'''

                            joints = body.joints 
                            #convert the points in 3d space to a point on the screen  
                            joint_points = runGame._kinect.body_joints_to_color_space(joints)
                            #save the hand positions
                            #Closed right hand to draw 
                            if joints[PyKinectV2.JointType_HandTipRight].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Closed:
                                self.pointList.append((joint_points[PyKinectV2.JointType_HandTipRight].x, joint_points[PyKinectV2.JointType_HandTipRight].y))
                                xPoints.append(joint_points[PyKinectV2.JointType_HandTipRight].x)
                                yPoints.append(joint_points[PyKinectV2.JointType_HandTipRight].y)
                            #Open left hand to signal done drawing 
                            if (runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Open):
                                self.doneDrawing = True 
                            #Open right hand to move hand without drawing (simulate "picking up your pencil")
                            if (runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open):
                                self.pointList = [] #clear the list of points to draw 
                #draw the points of the hand positions as circles to show drawing 
                if len(self.pointList) > 1:
                    for i in range(len(self.pointList)-1):
                        pygame.draw.circle(runGame.drawingSurface, (0,0,0), (int(self.pointList[i][0]), int(self.pointList[i][1])), 25)           
                        pygame.draw.line(runGame.drawingSurface, (0,0,0), self.pointList[i], self.pointList[i+1], 50)   
            
                    
               
                # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
                # --- (screen size may be different from Kinect's color frame size) 
                ratio = 0.75 #make the drawing screen smaller than whole window to have space for other stats 
                h_to_w = float((ratio * runGame._frame_surface.get_height()) / ( ratio * runGame._frame_surface.get_width()))
                target_height = int(h_to_w * (ratio * runGame._screen.get_width()))
                surface_to_draw = pygame.transform.scale(runGame.drawingSurface, (int(ratio * runGame._screen.get_width()), target_height));
                runGame._screen.fill((255,255,255))
                runGame._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None    

                pygame.display.update()
                runGame._clock.tick(60)
            factor = 0.375
            offset = 50
            #save the drawing with a unique filename (the timestamp) 
            timeStamp = str(time.mktime(time.localtime()))[:-2]
            if len(xPoints) > 0 and len(yPoints) > 0:
                left = factor*min(xPoints)-offset
                if left < 0: 
                    left = 0
                top = factor*min(yPoints)-offset
                if top < 0:
                    top = 0
                rectangleWidth = factor*max(xPoints) - left + offset
                if left + rectangleWidth > runGame._screen.get_width():
                    rectangleWidth = runGame._screen.get_width() - left
                rectangleHeight = factor*max(yPoints) - top + offset
                if top + rectangleHeight > runGame._screen.get_height():
                    rectangleHeight = runGame._screen.get_height() - top
            rectangle = pygame.Rect(left, top, rectangleWidth, rectangleHeight)
            subscreen = runGame._screen.subsurface(rectangle)
            pygame.image.save(subscreen, timeStamp + ".png")
            currentImage = pygame.image.load(timeStamp + ".png")
            self.mergedSurface = pygame.Surface((repeatImage*subscreen.get_width(), subscreen.get_height()))
            for i in range(repeatImage):
                self.mergedSurface.blit(currentImage, (i*subscreen.get_width(),0))
            pygame.image.save(self.mergedSurface, "merged.png")
            #run the text recognition API on the image 
            guessedLetter = getText("merged.png")
            #failure to recognize letter - try again, doesn't count against user's number of guesses left 
            if guessedLetter == "Error":
                print("Try again.")
            else:
                print(guessedLetter)
                guessedLetter = guessedLetter.lower().strip() #standardize the letter to be lowercase 
                guessedLetter = calibrateLetter(guessedLetter) 
                print(guessedLetter)
                #replace the elements in the currentWord list with the guessed letters wherever they show up in the word to be guessed 
                for i in range(len(self.wordToGuess)):
                    if self.wordToGuess[i] == guessedLetter:
                        self.currentWord[i] = guessedLetter
                        print(self.currentWord)
                self.guessesLeft -= 1
                self.guessed.add(guessedLetter)

            #all letters have been guessed correctly, so player wins and game is over 
            if "_" not in self.currentWord:
                self.gameOver = True
                self.win = True
                self.mode = "gameOver"    
                
            #no more guesses left but still letters to be guessed -> game over 
            if self.guessesLeft == 0:
                self.gameOver = True
                self.win = False 
                self.mode = "gameOver"
            
            #reset doneDrawing to False so player can draw a letter again 
            self.doneDrawing = False
            #clear list of points to draw
            self.pointList = []
            #clear the screen 
            runGame.drawingSurface.fill((255,255,255))
            runGame._screen.blit(runGame.drawingSurface, (0,0))
            pygame.display.update()


    def handleGameOver(self, runGame):
        runGame._done = True

#fix known consistent misrecognitions of the text recognition method 
def calibrateLetter(letter):
    if letter == "0":
        return "o"
    if letter == "1":
        return "l"
    if letter == "2":
        return "z"
    if letter == "9":
        return "y"
    if letter == "+":
        return "f"
    else:
        return letter 