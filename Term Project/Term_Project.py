from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
from GamePlay import *

#Kinect framework code from Kinect Workshop

class RunGame(object):
    def __init__(self):
        pygame.init()
        self.screen_width = 1920
        self.screen_height = 1080
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode((self.screen_width//2,self.screen_height//2), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)
        self._done = False
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        self._bodies = None
        self.gamePlay = GamePlay()
        self.drawingSurface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        self.drawingSurface.fill((255,255,255))

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()


    def run(self):
        while not self._done:
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    self._done = True 

            #call the appropriate method depending on the game mode 
            while not self.gamePlay.gameOver:
                if self.gamePlay.mode == "startScreen":
                    self.gamePlay.handleStartScreen(self)

                elif self.gamePlay.mode == "play":
                    self.gamePlay.handlePlayMode(self)

            if self.gamePlay.mode == "gameOver":
                self.gamePlay.handleGameOver(self)
                if self.gamePlay.playAgain:
                    self.gamePlay = GamePlay()
                else:
                    #insert closing message 
                    self._done = True                  


        self._kinect.close()
        pygame.quit()

game = RunGame()
game.run()
