from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
from GamePlay import *

class RunGame(object):
    def __init__(self):
        pygame.init()
        self.screen_width = 1920
        self.screen_height = 1080
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)
        self._done = False
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        self._bodies = None
        self.gamePlay = GamePlay()

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

            # We have a color frame. Fill out back buffer surface with frame's data 
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

            while not self.gamePlay.gameOver:
                if self.gamePlay.mode == "startScreen":
                    self.gamePlay.handleStartScreen()

                elif self.gamePlay.mode == "play":
                    self.gamePlay.handlePlayMode()

            if self.gamePlay.mode == "gameOver":
                self.gamePlay.handleGameOver()
                if self.gamePlay.playAgain:
                    self.gamePlay = GamePlay()
                #else:
                    #handle if the player doesn't want to play again                   

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()
            self._clock.tick(60)

        self._kinect.close()
        pygame.quit()

game = RunGame()
game.run()
