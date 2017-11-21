from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math

class GamePlay(object):
    def __init__(self):
        self.mode = "startScreen"
        self.gameOver = False
        self.playAgain = False
        self.wordToGuess = ""
        self.currentWord = ""
        self.guessed = set()
        self.difficultyLevel = -1
    
    def handleStartScreen():
        pass
    
    def handlePlayMode():
        pass

    def handleGameOver():
        pass 
