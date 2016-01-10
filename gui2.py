#!/usr/bin/env
import pygame, sys, os
from pygame.locals import *
from pgu import gui
from evdev import InputDevice, categorize, ecodes
import time

import threading
import tuner

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
        pygame.event.pump()
        event = dev.read_one()
        if event and event.type == ecodes.EV_ABS:
            self.handle_pos(event.code, event.value)

        for e in pygame.event.get():
            if not (e.type == QUIT and self.mywindow):
                self.event(e)

        # e = pygame.event.poll()
        # if not (e.type == QUIT and self.mywindow):
        #     self.event(e)   

        rects = self.update(self.screen)
        pygame.display.update(rects)

### Generic buttons ###

class Tune(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Tune'
        gui.Button.__init__(self,**params)

class Options(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Options'
        gui.Button.__init__(self,**params)

class Quit(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Quit'
        gui.Button.__init__(self,**params)

class Back(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Back'
        gui.Button.__init__(self,**params)

### Tuning screens buttons ###

class TuneOne(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Tune one'
        gui.Button.__init__(self,**params)

class TuneAll(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Tune all'
        gui.Button.__init__(self,**params)

class StringButton(gui.Button):
    # pass value!!!!11
    def __init__(self,**params):
        #params['value'] = 'Tune one'
        gui.Button.__init__(self,**params)

class DrawGUI:
    def __init__(self):

        self.container = gui.Container(width=480, height=320)
        self.mainscreencontainer = gui.Container(width=480, height=320)
        self.tunescreencontainer = gui.Container(width=480, height=320)
        self.optionscontainer = gui.Container(width=480, height=320)
        self.tuneonecontainer = gui.Container(width=480, height=320)
        self.set_background("/home/pi/Dyplom/guitar-tuning-system/bg.jpg")

        self.init_screens()
        
        self.container.add(self.mainscreencontainer, 0, 0)

    def init_screens(self):
        self.main_screen_init()
        self.tune_screen_init()
        self.options_screen_init()        
        self.tune_one_screen_init()

    def main_screen_init(self):
        self.options_button = Options(width=150, height=100)
        self.options_button.connect(gui.CLICK, self.draw_options)        
        
        self.tune_button = Tune(width=150, height=100)
        self.tune_button.connect(gui.CLICK, self.draw_tunescreen)
        
        self.mainscreencontainer.add(self.tune_button, 70, 110)        
        self.mainscreencontainer.add(self.options_button, 250, 110)
        
    def tune_screen_init(self):     
        self.tune_one_button = TuneOne(width=150, height=100)
        self.tune_one_button.connect(gui.CLICK, self.draw_tuneone)

        self.tune_all_button = TuneAll(width=150, height=100)
        self.tune_all_button.connect(gui.CLICK, self.draw_tuneall)

        self.back_button_tune = Back(width=50, height=50)
        self.back_button_tune.connect(gui.CLICK, self.back, 't')        

        self.tunescreencontainer.add(self.tune_one_button, 70, 110)
        self.tunescreencontainer.add(self.tune_all_button, 250, 110)
        self.tunescreencontainer.add(self.back_button_tune, 30, 240)    

    def tune_one_screen_init(self):
        self.string_buttons = {}
        offset_y = 0
        string_names = ['E', 'A', 'D', 'G', 'B', 'E']

        self.quit_button = Quit(width=100, height=100)
        self.quit_button.connect(gui.CLICK, app.quit, None)
        self.tuneonecontainer.add(self.quit_button, 200, 200)

        for i in range(0,6):
            self.string_buttons[i] = StringButton(width=50, height=42, value=string_names[i])
            self.tuneonecontainer.add(self.string_buttons[i], 10, 10+offset_y)
            self.string_buttons[i].connect(gui.CLICK, self.tune_one, i)
            offset_y += 52

    def options_screen_init(self):
        self.back_button_opt = Back(width=50, height=50)
        self.back_button_opt.connect(gui.CLICK, self.back, 'o')

        self.options_button = Options(width=150, height=100)
        self.options_button.connect(gui.CLICK, self.draw_options)

        self.optionscontainer.add(self.back_button_opt, 30, 240)

    def set_background(self, path):
        img = gui.Image(path)
        self.container.add(img, 0, 0)

    def draw_options(self):
        self.container.remove(self.mainscreencontainer)
        self.container.add(self.optionscontainer, 0, 0)

        self.container.reupdate()

    def draw_tunescreen(self):
        self.container.remove(self.mainscreencontainer)
        self.container.add(self.tunescreencontainer, 0, 0)

        self.container.reupdate()

    def back(self, screen):
        if screen == 't':
            self.container.remove(self.tunescreencontainer)
            self.container.add(self.mainscreencontainer, 0, 0)
        elif screen == 'o':
            self.container.remove(self.optionscontainer)
            self.container.add(self.mainscreencontainer, 0, 0)

        self.container.reupdate()

    def draw_tuneall(self):
        pass

    def draw_tuneone(self):
        self.container.remove(self.tunescreencontainer)
        self.container.add(self.tuneonecontainer, 0, 0)
        self.container.reupdate()

    def tune_one(self, string_number):
        self.tuner_thread = threading.Thread(target=self.run_thread, args=(string_number,))
        self.tuner_thread.daemon = True
        self.tuner_thread.start()

    def run_thread(self, string_number):
        import tuner
        #try:
        string_set = tuner.StringSet()
        self.tun = tuner.TuningHandler(string_set)
        self.tun.add_observer(self)
        self.tun.start(string_number)
        # except (KeyboardInterrupt, SystemExit):
        #     self.tun.stop()
        #     print '\n! Received keyboard interrupt, quitting threads.\n'

    def string_tuned(self, string_number):
        self.tun.del_observer(self)
        self.tun.stop()
        del self.tuner_thread
        print "String number %s tuned!" % string_number

if __name__ == "__main__":

    app = GUIApp()
    draw_gui = DrawGUI()
    try:
        app.run(draw_gui.container)
    except KeyboardInterrupt:
        print sys.exc_info()
        app.quit()
        raise SystemExit
    except:
        print sys.exc_info()
        raise SystemExit