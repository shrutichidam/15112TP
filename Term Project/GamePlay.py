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
    dictionary = Words()

    def __init__(self):
        self.mode = "startScreen"
        self.gameOver = False
        self.playAgain = None
        self.guessed = set() #stores letters the player has already guessed 
        self.pointList = [] #stores positions of hand while drawing a letter 
        self.visitedPoints = []
        self.allDrawnPoints = set()
        self.win = False
        self.doneDrawing = False
        self.mergedSurface = None
        self.currentMessage = "Draw a Letter!"
        self.chosenMode = "" #whether player decides to play against computer or not, decided later 
        self.dominantHand = ""
        #the following will be handled in chooseDifficulty(), based on what difficulty level is chosen 
        self.wordToGuess = ""
        self.difficultyLevel = -1
        self.guessesLeft = -1
        self.currentWord = [] #stores the current state of the word that the player has reached        
    
    def handleStartScreen(self, runGame):
        runGame._screen.fill((99,199,178))
        textFont = pygame.font.SysFont("britannic", 100)
        label = textFont.render("The AIr Word Game!", 1, (0,0,0))
        length = textFont.size("The AIr Word Game!")
        xPosition = (runGame._screen.get_width()- length[0])/2
        yPosition = (runGame._screen.get_height()- length[1])/2
        runGame._screen.blit(label, (xPosition,yPosition))
        pygame.display.update()
        time.sleep(3.5)
        runGame._screen.fill((99,199,178))
        textFont2 = pygame.font.SysFont("britannic", 50)
        label2 = textFont2.render("Please close both hands before we begin!", 1, (0,0,0))
        length2 = textFont2.size("Please close both hands before we begin!")
        xPosition2 =(runGame._screen.get_width()- length2[0])/2
        yPosition2 = (runGame._screen.get_height()- length2[1])/2 
        runGame._screen.blit(label2, (xPosition2,yPosition2))
        pygame.display.update()
        time.sleep(4)
        label3 = textFont.render("Ready? Let's go!",1,(0,0,0))
        length3 = textFont.size("Ready? Let's go!")
        xPosition3 =(runGame._screen.get_width()- length3[0])/2
        yPosition3 = (runGame._screen.get_height()- length3[1])/2  + 150       
        runGame._screen.blit(label3, (xPosition3,yPosition3))
        pygame.display.update()
        time.sleep(1.5)
        self.mode = "chooseHand"

    def chooseHand(self, runGame):
        #process Kinect data
        #loop until a dominant hand is chosen 
        while self.dominantHand == "":
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
                        if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open:
                            self.dominantHand = "Right"
                        elif joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Open:
                            self.dominantHand = "Left"
                        #assign difficulty level based on hand position 

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(runGame._frame_surface.get_height()) / runGame._frame_surface.get_width()
            target_height = int(h_to_w * runGame._screen.get_width())
            surface_to_draw = pygame.transform.scale(runGame._frame_surface, (runGame._screen.get_width(), target_height));
            runGame._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            textFont = pygame.font.SysFont("britannic", 50)
            label = textFont.render("Open the hand you wish to draw with.", 1, (0,0,0), (255,255,255))
            length = textFont.size("Open the hand you wish to draw with.")
            xPosition = (runGame._screen.get_width()- length[0])/2
            yPosition = 50
            runGame._screen.blit(label, (xPosition,yPosition))
            pygame.display.update()
            runGame._clock.tick(60)

        textFont = pygame.font.SysFont("britannic", 50)
        label = textFont.render("Great! Now let's choose a difficulty level", 1, (0,0,0), (255,255,255))
        length = textFont.size("Great! Now let's choose a difficulty level")
        xPosition = (runGame._screen.get_width()- length[0])/2
        yPosition = 475
        runGame._screen.blit(label, (xPosition,yPosition))
        pygame.display.update()
        time.sleep(1)
        runGame._screen.fill(((99,199,178)))
        textFont2 = pygame.font.SysFont("britannic", 50)
        label2 = textFont2.render("Please close both hands once more!", 1, (0,0,0))
        length2 = textFont2.size("Please close both hands once more!")
        xPosition2 =(runGame._screen.get_width()- length2[0])/2
        yPosition2 = (runGame._screen.get_height()- length2[1])/2 
        runGame._screen.blit(label2, (xPosition2,yPosition2))
        pygame.display.update()
        time.sleep(2.5)
        self.mode = "chooseDifficulty"

    def chooseDifficulty(self, runGame):
        #process Kinect data
        handX = -1 #start out with the position of the hand negative 
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
                        #open dominant hand in area of screen corresponding to difficulty level 
                        if self.dominantHand == "Right":
                            if joints[PyKinectV2.JointType_HandTipRight].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open:
                                handX = joint_points[PyKinectV2.JointType_HandRight].x
                            #assign difficulty level based on hand position 
                            if handX != -1:
                                if 0 <= handX <= runGame.screen_width//3:
                                    self.difficultyLevel = 1
                                elif runGame.screen_width//3 < handX <= 2 * runGame.screen_width//3:
                                    self.difficultyLevel = 2
                                else:
                                    self.difficultyLevel = 3
                        else:
                            if joints[PyKinectV2.JointType_HandTipLeft].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Open:
                                handX = joint_points[PyKinectV2.JointType_HandLeft].x
                            #assign difficulty level based on hand position 
                            if handX != -1:
                                if 0 <= handX <= runGame.screen_width//3:
                                    self.difficultyLevel = 1
                                elif runGame.screen_width//3 < handX <= 2 * runGame.screen_width//3:
                                    self.difficultyLevel = 2
                                else:
                                    self.difficultyLevel = 3
            #draw lines to signify boundaries of areas to choose from 
            pygame.draw.line(runGame._frame_surface, (99,199,178), (runGame.screen_width//3, 0), (runGame.screen_width//3, runGame.screen_height), 25)
            pygame.draw.line(runGame._frame_surface, (99,199,178), (2*runGame.screen_width//3, 0), (2*runGame.screen_width//3, runGame.screen_height), 25)
            numFont = pygame.font.SysFont("britannic", 75)
            num1 = numFont.render("1", 1, (0,0,0), (255,255,255))
            num2 = numFont.render("2", 1, (0,0,0), (255,255,255))
            num3 = numFont.render("3", 1, (0,0,0), (255,255,255))
            length1 = numFont.size("1")
            length2 = numFont.size("2")
            length3 = numFont.size("3")
            numY = (runGame._screen.get_height()- length1[1])/2
            textFont = pygame.font.SysFont("britannic", 32)
            label = textFont.render("Move your hand to the level you want to play. Then, open your hand.", 1, (0,0,0), (255,255,255))
            length = textFont.size("Move your hand to the level you want to play. Then, open your hand.")
            xPosition = (runGame._screen.get_width()- length[0])/2
            yPosition = 475
            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(runGame._frame_surface.get_height()) / runGame._frame_surface.get_width()
            target_height = int(h_to_w * runGame._screen.get_width())
            surface_to_draw = pygame.transform.scale(runGame._frame_surface, (runGame._screen.get_width(), target_height));
            runGame._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            runGame._screen.blit(label, (xPosition,yPosition))
            runGame._screen.blit(num1, ((runGame.screen_width//6 - length1[0])//2 , numY))
            runGame._screen.blit(num2, ((3*runGame.screen_width//6 - length2[0])//2, numY))
            runGame._screen.blit(num3, ((5*runGame.screen_width//6 - length2[0])//2, numY))
            pygame.display.update()
            runGame._clock.tick(60)

        print(self.difficultyLevel)
        self.wordToGuess = GamePlay.dictionary.words[self.difficultyLevel][random.randint(0, len(GamePlay.dictionary.words[self.difficultyLevel]) - 1)]
        print(self.wordToGuess)
        self.currentWord = ["_"] * len(self.wordToGuess)
        self.guessesLeft = self.difficultyLevel * 4 
        runGame._screen.fill(((99,199,178)))
        textFont = pygame.font.SysFont("britannic", 50)
        label = textFont.render("Almost there! Now let's choose a mode.", 1, (0,0,0))
        length = textFont.size("Almost there! Now let's choose a mode.")
        xPosition = (runGame._screen.get_width()- length[0])/2
        yPosition = 475
        runGame._screen.blit(label, (xPosition,yPosition))
        pygame.display.update()
        time.sleep(2)
        runGame._screen.fill(((99,199,178)))
        textFont2 = pygame.font.SysFont("britannic", 50)
        label2 = textFont2.render("Please close both hands one last time!", 1, (0,0,0))
        length2 = textFont2.size("Please close both hands one last time!")
        xPosition2 =(runGame._screen.get_width()- length2[0])/2
        yPosition2 = (runGame._screen.get_height()- length2[1])/2 
        runGame._screen.blit(label2, (xPosition2,yPosition2))
        pygame.display.update()
        time.sleep(2)
        self.mode = "chooseMode"
    
    def chooseMode(self, runGame):
        #process Kinect data
        #loop until a difficulty Level is chosen
        handX = -1 
        while self.chosenMode == "":
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
                        #open dominant hand in area of screen corresponding to difficulty level 
                        if self.dominantHand == "Right":
                            if joints[PyKinectV2.JointType_HandTipRight].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open:
                                handX = joint_points[PyKinectV2.JointType_HandRight].x
                            if handX != -1:
                                if 0 <= handX <= runGame.screen_width//2:
                                    self.chosenMode = "playClassic"
                                else:
                                    self.chosenMode = "playAI"
                        else:
                            if joints[PyKinectV2.JointType_HandTipLeft].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Open:
                                handX = joint_points[PyKinectV2.JointType_HandLeft].x
                            if handX != -1:
                                if 0 <= handX <= runGame.screen_width//2:
                                    self.chosenMode = "playClassic"
                                else:
                                    self.chosenMode = "playAI"

            #draw lines to signify boundaries of areas to choose from 
            pygame.draw.line(runGame._frame_surface, (99,199,178), (runGame.screen_width//2, 0), (runGame.screen_width//2, runGame.screen_height), 25)
            modeFont = pygame.font.SysFont("britannic", 50)
            mode1 = modeFont.render("1-Player Mode", 1, (0,0,0), (255,255,255))
            mode2 = modeFont.render("Play vs. Computer", 1, (0,0,0), (255,255,255))
            length1 = modeFont.size("1-Player Mode")
            length2 = modeFont.size("Play vs. Computer")
            modeY = (runGame._screen.get_height()- length1[1])/2
            textFont = pygame.font.SysFont("britannic", 32)
            label = textFont.render("Move your hand to the mode you want to play. Then, open your hand.", 1, (0,0,0), (255,255,255))
            length = textFont.size("Move your hand to the mode you want to play. Then, open your hand.")
            xPosition = (runGame._screen.get_width()- length[0])/2
            yPosition = 475
            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(runGame._frame_surface.get_height()) / runGame._frame_surface.get_width()
            target_height = int(h_to_w * runGame._screen.get_width())
            surface_to_draw = pygame.transform.scale(runGame._frame_surface, (runGame._screen.get_width(), target_height));
            runGame._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            runGame._screen.blit(label, (xPosition,yPosition))
            runGame._screen.blit(mode1, ((runGame.screen_width//4 - length1[0])//2 , modeY))
            runGame._screen.blit(mode2, ((3*runGame.screen_width//4 - length2[0])//2, modeY))
            pygame.display.update()
            runGame._clock.tick(60)

        runGame._screen.fill(((99,199,178)))
        textFont = pygame.font.SysFont("britannic", 60)
        label = textFont.render("Awesome! Let's Play!", 1, (0,0,0))
        length = textFont.size("Awesome! Let's Play!")
        xPosition = (runGame._screen.get_width()- length[0])/2
        yPosition = (runGame._screen.get_height()- length[1])/2
        runGame._screen.blit(label, (xPosition,yPosition))
        pygame.display.update()
        time.sleep(2)
        self.mode = "instructions"

    def displayInstructions(self, runGame):
        runGame._screen.fill(((99,199,178)))
        textFont = pygame.font.SysFont("britannic", 40)
        textLines = ["How To Play: ", "To draw a letter, close your hand and draw in the air.", "Open your nondominant hand when you are done", "drawing.", "Opening your dominant hand will show you where", "you are on the screen.", "Hint: The words can be anything- objects, places, etc."]
        x = 10
        y = 50
        for i in range(len(textLines)):
            if i in set([0,2,3,6]):
                line = textFont.render(textLines[i], 1, (0,0,0))
            else:
                line = textFont.render(textLines[i], 1, (255,255,255))
            runGame._screen.blit(line, (x, i*y))
            pygame.display.update() 
        
        time.sleep(10)
        self.mode = self.chosenMode
        

    def handleClassicMode(self, runGame): 
        repeatImage = 5
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

                            joints = body.joints 
                            #convert the points in 3d space to a point on the screen  
                            joint_points = runGame._kinect.body_joints_to_color_space(joints)
                                
                            if self.dominantHand == "Right":
                                #Closed right hand to draw 
                                if joints[PyKinectV2.JointType_HandTipRight].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Closed:
                                    self.visitedPoints = []
                                    self.pointList.append((int(joint_points[PyKinectV2.JointType_HandTipRight].x), int(joint_points[PyKinectV2.JointType_HandTipRight].y)))
                                    self.allDrawnPoints.add((int(joint_points[PyKinectV2.JointType_HandTipRight].x), int(joint_points[PyKinectV2.JointType_HandTipRight].y)))
                                    xPoints.append(joint_points[PyKinectV2.JointType_HandTipRight].x)
                                    yPoints.append(joint_points[PyKinectV2.JointType_HandTipRight].y)

                                #Open left hand to signal done drawing 
                                if (runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Open):
                                    self.doneDrawing = True 

                                #Open right hand to move hand without drawing (simulate "picking up your pencil")
                                if (runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open):
                                    self.pointList = [] #clear the list of points to draw
                                    if not isSimilarPoint((int(joint_points[PyKinectV2.JointType_HandTipRight].x), int(joint_points[PyKinectV2.JointType_HandTipRight].y)),self.allDrawnPoints):
                                        self.visitedPoints.append((int(joint_points[PyKinectV2.JointType_HandTipRight].x), int(joint_points[PyKinectV2.JointType_HandTipRight].y)))
                            else:
                                #Closed left hand to draw 
                                if joints[PyKinectV2.JointType_HandTipLeft].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Closed:
                                    self.visitedPoints = []
                                    self.pointList.append((int(joint_points[PyKinectV2.JointType_HandTipLeft].x), int(joint_points[PyKinectV2.JointType_HandTipLeft].y)))
                                    self.allDrawnPoints.add((int(joint_points[PyKinectV2.JointType_HandTipLeft].x), int(joint_points[PyKinectV2.JointType_HandTipLeft].y)))
                                    xPoints.append(joint_points[PyKinectV2.JointType_HandTipLeft].x)
                                    yPoints.append(joint_points[PyKinectV2.JointType_HandTipLeft].y)

                                #Open right hand to signal done drawing 
                                if (runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open):
                                    self.doneDrawing = True 

                                #Open left hand to move hand without drawing (simulate "picking up your pencil")
                                if (runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Open):
                                    self.pointList = [] #clear the list of points to draw
                                    if not isSimilarPoint((int(joint_points[PyKinectV2.JointType_HandTipLeft].x), int(joint_points[PyKinectV2.JointType_HandTipLeft].y)),self.allDrawnPoints):
                                        self.visitedPoints.append((int(joint_points[PyKinectV2.JointType_HandTipLeft].x), int(joint_points[PyKinectV2.JointType_HandTipLeft].y)))

        
                if len(self.visitedPoints) > 1:
                    for i in range(len(self.visitedPoints)):
                        if not isSimilarPoint(self.visitedPoints[i], self.allDrawnPoints):
                            pygame.draw.circle(runGame.drawingSurface, (255,255,255), (int(self.visitedPoints[i][0]), int(self.visitedPoints[i][1])), 25)
                            if i == len(self.visitedPoints)-1:
                                pygame.draw.circle(runGame.drawingSurface, (0,0,0), (int(self.visitedPoints[i][0]), int(self.visitedPoints[i][1])), 25)

                #draw the points of the hand positions as circles to show drawing 
                if len(self.pointList) > 1:
                    for i in range(len(self.pointList)-1):
                        pygame.draw.circle(runGame.drawingSurface, (0,0,0), self.pointList[i], 25)           
                        #pygame.draw.line(runGame.drawingSurface, (0,0,0), self.pointList[i], self.pointList[i+1], 50)   
          

                # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
                # --- (screen size may be different from Kinect's color frame size) 
                ratio = 0.75 #make the drawing screen smaller than whole window to have space for other stats 
                h_to_w = float((ratio * runGame._frame_surface.get_height()) / ( ratio * runGame._frame_surface.get_width()))
                target_height = int(h_to_w * (ratio * runGame._screen.get_width()))
                surface_to_draw = pygame.transform.scale(runGame.drawingSurface, (int(ratio * runGame._screen.get_width()), target_height));
                runGame._screen.fill((255,255,255))
                runGame._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None  
                self.currentMessage = "Guess a Letter!"
                self.redrawStats(runGame)

                pygame.display.update()
                runGame._clock.tick(60)

            self.currentMessage = "Please Wait!"
            self.redrawStats(runGame)
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
                if guessedLetter == "Error" or not guessedLetter.isalpha():
                    print("Try Again")
                    self.currentMessage = "My bad. Try again!"
                    self.redrawStats(runGame)
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
                    if guessedLetter in self.wordToGuess:
                        self.currentMessage = "Success!"
                        self.redrawStats(runGame)
                    else:
                        self.currentMessage = "Wrong guess."
                        self.redrawStats(runGame)

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
            self.allDrawnPoints = set()
            self.visitedPoints = []
            #clear the screen 
            runGame.drawingSurface.fill((255,255,255))
            runGame._screen.blit(runGame.drawingSurface, (0,0))

    def redrawStats(self, runGame):
        wordText = " ". join(self.currentWord)
        textFont = pygame.font.SysFont("britannic", 60, bold=True)
        textFont2 = pygame.font.SysFont("britannic", 28) 
        label = textFont.render(wordText, 1, (0,0,0))
        length = textFont.size(wordText)
        x1 = (runGame._screen.get_width()- length[0])/2
        y1 = 400
        guessedLetters = ", ".join(self.guessed)
        guessedLetters = "Letters Guessed: " + guessedLetters
        label2 = textFont2.render(guessedLetters, 1, (0,0,0))
        x2 = 20
        y2 = 500
        label3 = textFont2.render("Guesses Left: " + str(self.guessesLeft), 1, (0,0,0))
        x3 = 750
        y3 = 50
        messagetoDraw = textFont2.render("" + self.currentMessage, 1, (99,199,178))
        x4 = 750
        y4 = 250
        emptySurface = pygame.Surface((240,250))
        emptySurface.fill((255,255,255))
        runGame._screen.blit(label, (x1,y1))
        runGame._screen.blit(label2, (x2, y2))
        runGame._screen.blit(label3, (x3,y3))
        runGame._screen.blit(emptySurface, (750,250))
        runGame._screen.blit(messagetoDraw, (x4,y4))
        pygame.display.update()
        if self.currentMessage == "Success!" or self.currentMessage == "Wrong guess." or self.currentMessage == "My bad. Try again!":
            time.sleep(1.5)


    def handleAIMode(self, runGame):
        pass

    def handleGameOver(self, runGame):
        if self.chosenMode == "playClassic":
            if self.win:
                self.handleWinClassic(runGame)
            else:
                self.handleLoseClassic(runGame)
        else:
            if self.win:
                self.handleWinAI(runGame)
            else:
                self.handleLoseAI(runGame)
        handX = -1
        while self.playAgain == None:
            #Fill out back buffer surface with frame's data 
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
                        #open dominant hand in area of screen corresponding to difficulty level 
                        if self.dominantHand == "Right":
                            if joints[PyKinectV2.JointType_HandTipRight].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_right_state == HandState_Open:
                                handX = joint_points[PyKinectV2.JointType_HandRight].x
                            if handX != -1:
                                if 0 <= handX <= runGame.screen_width//2:
                                    self.playAgain = True
                                else:
                                    self.playAgain = False
                        else:
                            if joints[PyKinectV2.JointType_HandTipLeft].TrackingState != PyKinectV2.TrackingState_NotTracked and runGame._kinect._body_frame_bodies.bodies[i].hand_left_state == HandState_Open:
                                handX = joint_points[PyKinectV2.JointType_HandLeft].x
                            if handX != -1:
                                if 0 <= handX <= runGame.screen_width//2:
                                    self.playAgain = True
                                else:
                                    self.playAgain = False
            
            #draw lines to signify boundaries of areas to choose from 
            pygame.draw.line(runGame._frame_surface, (99,199,178), (runGame.screen_width//2, 0), (runGame.screen_width//2, runGame.screen_height), 25)
            modeFont = pygame.font.SysFont("britannic", 50)
            option1 = modeFont.render("Play Again", 1, (0,0,0), (255,255,255))
            option2 = modeFont.render("Quit", 1, (0,0,0), (255,255,255))
            length1 = modeFont.size("Play Again")
            length2 = modeFont.size("Quit")
            y = (runGame._screen.get_height()- length1[1])/2
            textFont = pygame.font.SysFont("britannic", 29)
            label = textFont.render("Move your hand to the option you want to choose. Then, open your hand.", 1, (0,0,0), (255,255,255))
            length3 = textFont.size("Move your hand to the option you want to choose. Then, open your hand.")
            x2 = (runGame._screen.get_width()- length3[0])/2
            y2 = 475
            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(runGame._frame_surface.get_height()) / runGame._frame_surface.get_width()
            target_height = int(h_to_w * runGame._screen.get_width())
            surface_to_draw = pygame.transform.scale(runGame._frame_surface, (runGame._screen.get_width(), target_height));
            runGame._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            runGame._screen.blit(label, (x2,y2))
            runGame._screen.blit(option1, ((runGame.screen_width//4 - length1[0])//2 , y))
            runGame._screen.blit(option2, ((3*runGame.screen_width//4 - length2[0])//2, y))
            pygame.display.update()
            runGame._clock.tick(60)        

    def handleWinClassic(self, runGame):
        runGame._screen.fill(((99,199,178)))
        textFont = pygame.font.SysFont("britannic", 70)
        textLines = ["You Win!", "It took you", str(self.guessesLeft-len(self.guessed)), "guesses!"]
        height = 0
        for j in range(len(textLines)):
            height += textFont.size(textLines[j])[1]
        y =  (runGame._screen.get_height()- height)/2

        for i in range(len(textLines)):
            if i == 2:
                line = textFont.render(textLines[i], 1, (255,255,255))
            else:
                line = textFont.render(textLines[i], 1, (0,0,0))
            x = (runGame._screen.get_width()- textFont.size(textLines[i])[0])/2
            runGame._screen.blit(line, (x, y + i*textFont.size(textLines[i])[1]))
            pygame.display.update() 
        time.sleep(3)
    
    def handleLoseClassic(self, runGame):
        runGame._screen.fill(((99,199,178)))
        textFont = pygame.font.SysFont("britannic", 70)
        textLines = ["Better Luck Next Time!", "The word was:", self.wordToGuess]
        height = 0
        for j in range(len(textLines)):
            height += textFont.size(textLines[j])[1]
        y =  (runGame._screen.get_height()- height)/2
        for i in range(len(textLines)):
            if i == 2:
                line = textFont.render(textLines[i], 1, (255,255,255))
            else:
                line = textFont.render(textLines[i], 1, (0,0,0))
            x = (runGame._screen.get_width()- textFont.size(textLines[i])[0])/2
            runGame._screen.blit(line, (x, y*i + 50))
            pygame.display.update() 
        time.sleep(3)

    def handleWinAI(self, runGame):
        runGame._screen.fill(((99,199,178)))
        textFont = pygame.font.SysFont("britannic", 70)
        text = "You beat the computer!"
        x = (runGame._screen.get_width()- textFont.size(text)[0])/2
        y =  (runGame._screen.get_height()- textFont.size(text)[1])/2
        line = textFont.render(text, 1, (255,255,255))
        runGame._screen.blit(line, (x, y))
        pygame.display.update() 
        time.sleep(3)

    def handleLoseAI(self, runGame):
        runGame._screen.fill(((99,199,178)))
        textFont = pygame.font.SysFont("britannic", 70)
        textLines = ["The Computer Beat You!", "The word was:", self.wordToGuess]
        height = 0
        for j in range(len(textLines)):
            height += textFont.size(textLines[j])[1]
        y =  (runGame._screen.get_height()- height)/2
        for i in range(len(textLines)):
            if i == 2:
                line = textFont.render(textLines[i], 1, (255,255,255))
            else:
                line = textFont.render(textLines[i], 1, (0,0,0))
            x = (runGame._screen.get_width()- textFont.size(textLines[i])[0])/2
            runGame._screen.blit(line, (x, y*i + 50))
            pygame.display.update() 
        time.sleep(3)

    def endGame(self, runGame):
        runGame._screen.fill(((99,199,178)))
        textFont = pygame.font.SysFont("britannic", 70)
        text = "Thanks for Playing!"
        x = (runGame._screen.get_width()- textFont.size(text)[0])/2
        y =  (runGame._screen.get_height()- textFont.size(text)[1])/2
        line = textFont.render(text, 1, (255,255,255))
        runGame._screen.blit(line, (x, y))
        pygame.display.update() 
        time.sleep(2)


def isSimilarPoint(point, pointSet):
    margin = 30
    for p in pointSet:
        if point[0] - margin <= p[0] <= point[0] + margin and point[1] - margin <= p[1] <= point[1] + margin:
            return True
    return False

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
        return "t"
    else:
        return letter 