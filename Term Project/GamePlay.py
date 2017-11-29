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

class GamePlay(object):
    def __init__(self):
        self.mode = "startScreen" #fix this 
        self.gameOver = False
        self.playAgain = False
        self.guessed = set()
        #the following will be handled in handleStartScreen(), based on what difficulty level is chosen 
        self.wordToGuess = ""
        self.difficultyLevel = -1
        self.guessesLeft = -1
        self.currentWord = []
        self.dictionary = Words()
        self.win = False
        self.doneDrawing = False
        self.pointList = []

    
    def handleStartScreen(self, runGame):
        #process Kinect data
        #then:
        self.difficultyLevel = 1 # will come from the Kinect data
        self.wordToGuess = self.dictionary.words[self.difficultyLevel][random.randint(0, len(self.dictionary.words[self.difficultyLevel]) - 1)]
        print(self.wordToGuess)
        self.currentWord = [0] * len(self.wordToGuess)
        self.guessesLeft = self.difficultyLevel * 5 
        self.mode = "play"
    
    def handlePlayMode(self, runGame): 
        print(self.doneDrawing)
        while not self.gameOver:
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
                            joint_points = runGame._kinect.body_joints_to_color_space(joints)
                            # save the hand positions
                            if joints[PyKinectV2.JointType_HandTipRight].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Closed:
                                self.pointList.append((joint_points[PyKinectV2.JointType_HandTipRight].x, joint_points[PyKinectV2.JointType_HandTipRight].y))
                            if (runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Open):
                                self.doneDrawing = True 
                            if (runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open):
                                self.pointList = []
                if len(self.pointList) > 1:
                    for i in range(len(self.pointList)-1):
                        pygame.draw.circle(runGame.drawingSurface, (0,0,0), (int(self.pointList[i][0]), int(self.pointList[i][1])), 25)           
                        pygame.draw.line(runGame.drawingSurface, (0,0,0), self.pointList[i], self.pointList[i+1], 50)           
            
                    
               
                # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
                # --- (screen size may be different from Kinect's color frame size) 
                ratio = 0.75 
                h_to_w = float((ratio * runGame._frame_surface.get_height()) / ( ratio * runGame._frame_surface.get_width()))
                target_height = int(h_to_w * (ratio * runGame._screen.get_width()))
                surface_to_draw = pygame.transform.scale(runGame.drawingSurface, (int(ratio * runGame._screen.get_width()), target_height));
                runGame._screen.fill((255,255,255))
                runGame._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None    

                pygame.display.update()
                runGame._clock.tick(60)

            timeStamp = str(time.mktime(time.localtime()))[:-2]
            rectangle = pygame.Rect(0, 0, int(ratio*runGame._screen.get_width()), int(ratio*runGame._screen.get_height()))
            subscreen = runGame._screen.subsurface(rectangle)
            pygame.image.save(subscreen, timeStamp + ".png")
            guessedLetter = getText(timeStamp+".png")
            if guessedLetter == "Error":
                print("Try again.")
            else:
                print(guessedLetter)
                guessedLetter = guessedLetter.lower().strip()
                guessedLetter = calibrateLetter(guessedLetter)
                print(guessedLetter)
                for i in range(len(self.wordToGuess)):
                    if self.wordToGuess[i] == guessedLetter:
                        self.currentWord[i] = guessedLetter
                        print(self.currentWord)
                self.guessesLeft -= 1
                self.guessed.add(guessedLetter)
            
            if self.guessesLeft == 0:
                self.gameOver = True
                self.mode = "gameOver"
            if 0 not in self.currentWord:
                self.gameOver = True
                self.win = True
                self.mode = "gameOver"
            self.doneDrawing = False
            self.pointList = []
            runGame.drawingSurface.fill((255,255,255))
            runGame._screen.blit(runGame.drawingSurface, (0,0))
            pygame.display.update()


    def handleGameOver(self, runGame):
        runGame._done = True
        
def calibrateLetter(letter):
    if letter == "0":
        return "o"
    if letter == "1":
        return "l"
    if letter == "2":
        return "z"
    else:
        return letter 