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

    def init(self, widget=None, screen=None, area=None):
        super(GUIApp, self).init(widget, screen, area)        
        pygame.mouse.set_visible(False)
        
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

class TuningButton(gui.Button):
    # pass value!!!!11
    def __init__(self,**params):
        gui.Button.__init__(self,**params)        

class StopButton(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Stop / Back'
        gui.Button.__init__(self,**params)        

class StartButton(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Start'
        gui.Button.__init__(self,**params)   

class DrawGUI:
    def __init__(self):

        self.container = gui.Container(width=480, height=320)
        self.mainscreencontainer = gui.Container(width=480, height=320)
        self.tunescreencontainer = gui.Container(width=480, height=320)
        self.optionscontainer = gui.Container(width=480, height=320)
        self.tuneonecontainer = gui.Container(width=480, height=320)
        self.tuneallcontainer = gui.Container(width=480, height=320)
        self.set_background("/home/pi/Dyplom/guitar-tuning-system/bg.jpg")

        self.tuning_containers = [self.tuneonecontainer, self.tuneallcontainer]

        self.string_highlight_widget = None
        self.pluck_notification_widget = None

        self.string_set = tuner.StringSet()

        self.init_screens()
        
        self.container.add(self.mainscreencontainer, 0, 0)


    def init_screens(self):
        self.main_screen_init()
        self.tune_screen_init()
        self.options_screen_init()        
        self.tune_one_screen_init()
        self.tune_all_screen_init()
        self.generic_widgets_init()

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

        img = gui.Image("/home/pi/Dyplom/guitar-tuning-system/gryf.jpg")
        self.tuneonecontainer.add(img, 88, 0)

        self.stop_button = StopButton(width=100, height=100)
        self.stop_button.connect(gui.CLICK, self.stop_tuning)
        self.tuneonecontainer.add(self.stop_button, 360, 210)

        for i in range(0,6):
            self.string_buttons[i] = StringButton(width=50, height=42, value=string_names[i])
            self.tuneonecontainer.add(self.string_buttons[i], 10, 10+offset_y)
            self.string_buttons[i].connect(gui.CLICK, self.tune_one, i)
            offset_y += 52

    def tune_all_screen_init(self):
        img = gui.Image("/home/pi/Dyplom/guitar-tuning-system/gryf.jpg")
        self.tuneallcontainer.add(img, 88, 0)        

        self.stop_button = StopButton(width=100, height=100)
        self.stop_button.connect(gui.CLICK, self.stop_tuning)
        self.tuneallcontainer.add(self.stop_button, 360, 210)

        self.start_button = StartButton(width=100, height=100)
        self.start_button.connect(gui.CLICK, self.tune_all)
        self.tuneallcontainer.add(self.start_button, 360, 100)        

    def generic_widgets_init(self):
        self.string_highlight_widget = gui.Color(width=155, height=10)
        self.string_highlight_widget.value = (255, 0, 0)
        self.pluck_notification_widget = gui.Button(width=100, height=50, value="Pluck the string", background=(253, 194, 14))

    def options_screen_init(self):
        self.back_button_opt = Back(width=100, height=100)
        self.back_button_opt.connect(gui.CLICK, self.back, 'o')
        self.optionscontainer.add(self.back_button_opt, 360, 210)

        self.tune_E_button = TuningButton(width=300, height=42, value='Standard E')
        self.tune_E_button.connect(gui.CLICK, self.set_tuning, 'E')
        self.optionscontainer.add(self.tune_E_button, 0, 60)

        self.tune_Ds_button = TuningButton(width=300, height=42, value='D#')
        self.tune_Ds_button.connect(gui.CLICK, self.set_tuning, 'D#')
        self.optionscontainer.add(self.tune_Ds_button, 0, 112)

        self.tune_D_button = TuningButton(width=300, height=42, value='D')
        self.tune_D_button.connect(gui.CLICK, self.set_tuning, 'D')
        self.optionscontainer.add(self.tune_D_button, 0, 164)

        self.tune_dropD_button = TuningButton(width=300, height=42, value='Drop D')
        self.tune_dropD_button.connect(gui.CLICK, self.set_tuning, 'Drop D')
        self.optionscontainer.add(self.tune_dropD_button, 0, 216)        

        self.tune_dropC_button = TuningButton(width=300, height=42, value='Drop C')
        self.tune_dropC_button.connect(gui.CLICK, self.set_tuning, 'Drop C')
        self.optionscontainer.add(self.tune_dropC_button, 0, 268)

        self.current_tuning_label = gui.Button(width = 100, height = 20, value="Your current tuning:", background=(255, 255, 255))
        self.optionscontainer.add(self.current_tuning_label, 0, 0)

        current_tuning = self.current_tuning_helper()

        self.current_tuning_widget = gui.Button(height = 30, value=current_tuning, background=(255, 255, 255))
        self.optionscontainer.add(self.current_tuning_widget, 0, 20)

    def current_tuning_helper(self):
        current_tuning = self.string_set.get_string_sounds()
        parsed_current_tuning = {}
        for key, value in current_tuning.iteritems():
            parsed_current_tuning[key+1] = current_tuning[key] 
        return str(parsed_current_tuning)[1:-1]

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
    
    def draw_tuneall(self):
        self.container.remove(self.tunescreencontainer)
        self.container.add(self.tuneallcontainer, 0, 0)
        self.container.reupdate()
    
    def draw_tuneone(self):
        self.container.remove(self.tunescreencontainer)
        self.container.add(self.tuneonecontainer, 0, 0)
        self.container.reupdate()

    def set_tuning(self, tuning):
        tunings_dict = {
        'E': {0: 'E', 1: 'A', 2: 'D', 3: 'G', 4: 'B', 5: 'E'},
        'D#': {0: 'D#', 1: 'G#', 2: 'C#', 3: 'F#', 4: 'A#', 5: 'D#'},
        'D': {0: 'D', 1: 'G', 2: 'C', 3: 'F', 4: 'A', 5: 'D'},
        'Drop D': {0: 'D', 1: 'A', 2: 'D', 3: 'G', 4: 'B', 5: 'E'},
        'Drop C': {0: 'C', 1: 'G', 2: 'C', 3: 'F', 4: 'A', 5: 'D'}                           
        }

        self.string_set.set_new_tuning(tunings_dict[tuning])
        current_tuning = self.current_tuning_helper()
        self.current_tuning_widget.value = current_tuning
        self.container.reupdate()

    def back(self, screen):
        if screen == 't':
            self.container.remove(self.tunescreencontainer)
            self.container.add(self.mainscreencontainer, 0, 0)
        elif screen == 'o':
            self.container.remove(self.optionscontainer)
            self.container.add(self.mainscreencontainer, 0, 0)
        elif screen == 'toa':
            try:
                self.container.remove(self.tuneonecontainer)
            except:
                self.container.remove(self.tuneallcontainer)

            self.container.add(self.mainscreencontainer, 0, 0)

        self.container.reupdate()

    ### Dynamic GUI widgets drawing methods

    def highlight_string_draw(self, string_number):

        for container in self.tuning_containers:
            container.add(self.string_highlight_widget, 88, 15+(string_number*58)-string_number)     

        self.container.reupdate()

    def highlight_string_remove(self):

        for container in self.tuning_containers:
            container.remove(self.string_highlight_widget)
        
        self.container.reupdate()

    def pluck_notification_draw(self):
        try:
            for container in self.tuning_containers:
                container.add(self.pluck_notification_widget, 328, 10)
                self.container.reupdate()
        except:
            pass

    def pluck_notification_remove(self):
        try:
            for container in self.tuning_containers:
                container.remove(self.pluck_notification_widget)
                self.container.reupdate()
        except:
            pass

    def tune_one(self, string_number):
        if not hasattr(self, 'tuner_thread') and not hasattr(self, 'tun'):
            # self.pluck_notification_draw()
            # self.highlight_string_draw(string_number)
            self.tuner_thread = threading.Thread(target=self.run_thread, args=(string_number,))
            self.tuner_thread.daemon = True
            self.tuner_thread.start()
   
    def tune_all(self):
        if not hasattr(self, 'tuner_thread') and not hasattr(self, 'tun'):
            # self.pluck_notification_draw()
            # self.highlight_string_draw(string_number)
            self.tuner_thread = threading.Thread(target=self.run_thread, args=())
            self.tuner_thread.daemon = True
            self.tuner_thread.start()

    def run_thread(self, *args):
        self.tun = tuner.TuningHandler(self.string_set)
        self.tun.add_observer(self)
        if args:
            self.tun.start(args[0])
        else:
            self.tun.start()

    def stop_tuning(self):
        try:    
            self.clear_notifications()
            self.tun.del_observer(self)
            self.tun.stop()
            del self.tuner_thread, self.tun
            print "Tuning stopped."        
        except:
            self.back('toa')
            print "Nothing to stop."
    
    def clear_notifications(self):
        try:
            self.highlight_string_remove()
            self.pluck_notification_remove()
        except:
            pass

    ### Observer methods

    def string_tuned(self, string_number, finished):
        if finished == True:
            self.stop_tuning()

        self.clear_notifications()

        print "String number %s tuned!" % string_number

    def highlight_string(self, string_number):
        self.highlight_string_draw(string_number)

    def pluck_string(self):
        self.pluck_notification_draw()   

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