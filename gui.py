#!/usr/bin/env
import pygame, sys, os
from pygame.locals import *
from pgu import gui
from evdev import InputDevice, categorize, ecodes

os.environ["SDL_FBDEV"] = "/dev/fb1"
dev = InputDevice('/dev/input/event1')

class GUIApp(gui.Desktop):
    def __init__(self, theme=None, **params):
        super(GUIApp, self).__init__(theme=None, **params)
        self.input_position = [None, None]
        self.connect(gui.QUIT,self.quit,None)

    """Child class to override PGU application loop method, changes touchscreen input mechanism"""
    def handle_pos(self, code, value):
        if code == 0:
            mapped_value = self.map_values(value, 75, 1905, 0, 479)
            self.input_position[0] = mapped_value
        elif code == 1:
            mapped_value = self.map_values(value, 100, 1988, 0, 319)
            self.input_position[1] = mapped_value
        if self.input_position[0] and self.input_position[1]:
            pygame.mouse.set_pos(self.input_position)
            self.input_position = [None, None]

    def map_values(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def loop(self):
        self.set_global_app()

        event = dev.read_one()
        if event and event.type == ecodes.EV_ABS:
            self.handle_pos(event.code, event.value)

        for e in pygame.event.get():
            if not (e.type == QUIT and self.mywindow):
                self.event(e)

        rects = self.update(self.screen)
        pygame.display.update(rects)

class Quit(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Quit'
        gui.Button.__init__(self,**params)

class Options(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Options'
        gui.Button.__init__(self,**params)

class Back(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Back'
        gui.Button.__init__(self,**params)

class DrawGUI:
    def __init__(self):
        self.container = gui.Container(width=480, height=320)
        self.set_background("/home/pi/Dyplom/guitar-tuning-system/bg.jpg")
        self.initialise_buttons()
        self.draw_mainscreen()

    def set_background(self, path):
        img = gui.Image(path)
        self.container.add(img, 0, 0)

    def initialise_buttons(self):
        """
        Initialise and connect all the buttons here.
        """
        self.quit_button = Quit(width=100, height=100)
        self.quit_button.connect(gui.CLICK, app.quit, None)

        self.options_button = Options(width=100, height=100)
        self.options_button.connect(gui.CLICK, self.draw_options)

        self.back_button = Back(width=50, height=50)
        self.back_button.connect(gui.CLICK, self.draw_mainscreen)
   
    def draw_mainscreen(self):
        """
        Everything related to drawing the main screen.
        """
        try:
            self.container.remove(self.back_button)
        except:
            pass

        self.container.add(self.quit_button, 20, 20)        
        self.container.add(self.options_button, 120, 120)   

    def draw_options(self):
        """
        Everything related to drawing the options screen.
        """
        self.container.remove(self.quit_button)
        self.container.remove(self.options_button)

        self.container.add(self.back_button, 250, 250)

if __name__ == "__main__":

    app = GUIApp(background=(255,255,255))

    dgui = DrawGUI()

    app.run(dgui.container)