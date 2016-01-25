import numpy as np
import RPi.GPIO as GPIO
import sys
import frequency
import pid
import time
import matplotlib
matplotlib.use("Pdf")
import matplotlib.pyplot as plt

import os

class String(object):
    """
    String class. Object representation of a single string. Calculates target frequency based on string number and sound name input.

    (Will the naming collide with python string module?)
    """
    def __init__(self, string_number, sound):
        super(String, self).__init__()
        self.string_number = string_number
        self.sound = sound
        self._set_frequency()

    def _calculate_frequency(self):
        sounds = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        great = [65.4064, 69.2957, 73.4162, 77.7817, 82.4069, 87.3071, 92.4986,
                                97.9989, 103.8262, 110.0000, 116.5409, 123.4708]    
        # small = [130.8128, 138.5913, 146.8324, 155.5635, 164.8138, 174.6141, 
        #                       184.9972, 195.9977, 207.6523, 220.0000, 233.0819, 246.9417]
        # onelined = [261.6256, 277.1826, 293.6648, 311.1270, 329.6276, 349.2282, 369.9944, 
        #                       391.9954, 415.3047, 440.0000, 466.1638, 493.8833]
        # twolined = [523.2511, 554.3653, 587.3295, 622.254, 659.2551, 698.4565,
        #                        739.9888, 783.9909, 830.6094, 880.0, 932.3275, 987.7666]

        """
        'frequencies of the notes with the same name in two neighboring octaves are different by 2.'
        'The typical (six string) guitar normally plays pitches of great through two-lined octaves. E2, A2, D3, G3, B3, and E4 where 2 = great, 3 = small, 4 = onelined, 5 = twolined'
        """
        octaves = [1, 1, 2, 2, 2, 4]  ## narazie na sztywno, nie mam jeszcze pomyslu jak to obejsc dla innych, nietypowych gitar
        matching_index = next(sounds.index(elem) for elem in sounds if self.sound == elem)      
        return great[matching_index] * octaves[self.string_number]

    def _set_frequency(self):
        self.target_frequency = self._calculate_frequency()     

class StringSet(object):
    """
    StringSet builds string objects from user input (maps dictionary from GUI to objects). Provides several helper methods, I don't really know what for yet. 
    """
    def __init__(self, string_sound_dict=None):
        super(StringSet, self).__init__()
        
        if string_sound_dict != None:
            self.string_sound_dict = string_sound_dict
        else:
            self.string_sound_dict = self.default_tuning()

        self.string_objects = []
        self._instantiate_strings()

    def _instantiate_strings(self):
        for key, value in self.string_sound_dict.items():
            self.string_objects.append(String(key, value))

    def get_string_objects(self):
        """
        Just for clarity.
        """
        return self.string_objects

    def get_string_sounds(self):
        return self.string_sound_dict

    def get_target_frequencies(self):
        frequencies = {}
        for obj in self.string_objects:
            frequencies[obj.string_number] = (obj.sound, obj.target_frequency)
        return frequencies

    def set_new_tuning(self, string_sound_dict):
        self.string_objects = []
        self.string_sound_dict = string_sound_dict
        self._instantiate_strings()

    def default_tuning(self):
        default_tuning_dict = {0: 'D#', 1: 'G#', 2: 'C#', 3: 'F#', 4: 'A#', 5: 'D#'}
        return default_tuning_dict

class TuningHandler(object):
    """docstring for TuningHandler"""
    def __init__(self, string_set):
        super(TuningHandler, self).__init__()
        self.string_set = string_set
        self.stopped = True
        self.frequency_detector = frequency.Frequency()
        self.last_readings = []
        self.observers = []
        self.last_duty = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
        self.servo = GPIO.PWM(18, 50)
        self.servo.start(0)

        # self.pid_controller=pid.PID(3, 0.25, 1.5)
        #self.pid_controller=pid.PID(1.2, 0.25, 0.1)
        self.pid_controller=pid.PID(8, 0.25, 0)

    def stop(self):
        self.stopped = True
        self.frequency_detector.recorder.close()
        GPIO.cleanup()

    def start(self, *args):
        self.stopped = False
        if args:
            self.tune_one(args[0])
        else:
            self.tune_all()

    def add_observer(self, observer):
        self.observers.append(observer)
        print "added observer %s" % observer

    def del_observer(self, observer):
        self.observers.remove(observer)
        print "removed observer %s" % observer 

    def notify_string_tuned(self, string_number, finished):
        for obs in self.observers:
            obs.string_tuned(string_number, finished)

    def notify_pluck_string(self):
        for obs in self.observers:
            obs.pluck_string()

    def notify_highlight_string(self, string_number):
        for obs in self.observers:
            obs.highlight_string(string_number)

    def tune_all(self):
        target_frequencies = sorted(self.string_set.get_target_frequencies())
        iterations = 1
        
        for key in target_frequencies:
            if iterations == len(target_frequencies):
                self.tune_one(key)
            else:
                self.tune_one(key, False)

            iterations += 1

    def tune_one(self, string_number, finished_after=True):

        target_frequencies = self.string_set.get_target_frequencies()
        string_target_frequency = target_frequencies[string_number][1]

        self.notify_highlight_string(string_number)

        time.sleep(5)
        self.notify_pluck_string()

        self.frequency_detector.queue = []
        self.pid_controller.setPoint(string_target_frequency)

        x_table = []
        y_table = []
        start_time = time.time()
        
        last_frequency = False
        last_values = []

        while self.stopped == False:
            
            #!#!#! SPRAWDZIC JESZCZE RAZ TEN PATENT Z FREQUENCY CO ON BYL WCZESNIEJ, Z ODCH STD

            freq = self.frequency_detector.measure()
            #values_correct = string_target_frequency*0.5 < freq < string_target_frequency*1.4 # zabezpieczenie przed dziwnymi wartosciami

            if len(last_values) > 7:        
                last_values.pop(0)     
                last_values.append(freq)       
            else:     
                last_values.append(freq)            

            values_correct = np.std(last_values) < 15 and max(last_values) < 400

            if values_correct: 
                
                if last_frequency and abs(last_frequency - freq) < 15:

                    last_frequency = freq

                    string_tuned = self.check_one_tuned(string_number, string_target_frequency, freq)

                    measurement_time = time.time() - start_time
                    x_table.append(measurement_time)
                    y_table.append(freq)

                    if string_tuned == True:

                        self.notify_string_tuned(string_number, finished_after)

                        self._servo_update(7.5)  
                        print "TUNING TIME: %s" % (time.time() - start_time)
                        #print "STD: %s" % (np.std(self.last_readings))
                        offset = x_table[5]
                        for ind, elem in enumerate(x_table):
                            x_table[ind] = elem - offset

                        plt.plot(x_table[5:], y_table[5:])
                        plt.axhline(y=string_target_frequency)
                        plot_name = 'wykres_'+str(string_number)+'.png'
                        plt.savefig(os.path.join('/home/pi/Dyplom/', plot_name))                    
                        plt.clf()

                        break
           
                    pid_value = self.pid_controller.update(freq)

                    if round(pid_value, 1) > 0:
                        duty = round(self._map_values(pid_value, 0, 50, 7.5, 5.3), 1)
                    elif round(pid_value, 1) < 0:
                        duty = round(self._map_values(pid_value, 0, -50, 7.5, 8.9), 1)
                    else:
                        duty = 7.5                

                    print string_target_frequency, freq, duty, pid_value

                    self._servo_update(duty)

                else:
                    print "NOT TUNING: %s, %s" % (last_frequency, freq)
                    last_frequency = freq

            else:
                print "NOT TUNING VALUES NOT CORRENT: %s" % freq
                #self.pid_controller.setPoint(string_target_frequency)
                self._servo_update(7.5)

    def check_tuned(self):
        pass

    def check_one_tuned(self, string_number, string_target_frequency, freq):
        # if len(self.last_readings) > 15:
        #     self.last_readings.pop(0)
        #     self.last_readings.append(freq)
        # else:
        #     self.last_readings.append(freq)

        # standard_deviation = np.std(self.last_readings)

        # last_avg = sum(self.last_readings)/len(self.last_readings)

        # if string_target_frequency - 0.1 <= last_avg <= string_target_frequency + 0.1 and standard_deviation < 0.3:
        #     if string_target_frequency - 0.2 <= freq <= string_target_frequency + 0.2:
        #         print "TUNED: %s, %s, %s" % (string_target_frequency, freq, last_avg)
        #         print self.last_readings
        #         return True
        # else:
        #     return False

        if len(self.last_readings) > 7:
            self.last_readings.pop(0)
            self.last_readings.append(freq)

            standard_deviation = np.std(self.last_readings)

            last_avg = sum(self.last_readings)/len(self.last_readings)

            if string_target_frequency - 0.4 <= last_avg <= string_target_frequency + 0.4 and standard_deviation < 0.2:
                if string_target_frequency - 0.3 <= freq <= string_target_frequency + 0.3:
                    print "TUNED: %s, %s, %s, %s" % (string_target_frequency, freq, last_avg, standard_deviation)
                    print self.last_readings
                    return True
            else:
                return False
        else:
            self.last_readings.append(freq)
            return False

    def _map_values(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def _servo_update(self, duty):
        if self.last_duty != duty:
            self.servo.ChangeDutyCycle(duty)
    
        self.last_duty = duty