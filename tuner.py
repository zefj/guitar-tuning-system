from multiprocessing import Process, Queue, Manager, Value
import numpy as np
import RPi.GPIO as GPIO
import sys
import frequency
import pid
import time


GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
servo = GPIO.PWM(18, 50)
servo.start(7.5)

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
        # string_sound_list: __dict__, string_number: 'sound'
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

    def default_tuning(self):
        default_tuning_dict = {0: 'D#', 1: 'G#', 2: 'C#', 3: 'F#', 4: 'A#', 5: 'D#'}
        return default_tuning_dict

class TuningHandler(object):
    """docstring for TuningHandler"""
    def __init__(self, string_set):
        super(TuningHandler, self).__init__()
        self.string_set = string_set

        manager = Manager()
        self.queue = manager.list()
        self.average_value = Value('f', 0)
        self.values_correct_flag = Value('I', 0)
       
        self.pid_controller=pid.PID(2.0, 0.0, 0.8)

    def start_process(self):
        self.frequency_detector = frequency.Frequency()
        self.frequency_detector_process = Process(target = self.frequency_detector.measure, args=(self.queue, self.values_correct_flag, self.average_value))
        self.frequency_detector_process.start()

    def stop_process(self):
        self.frequency_detector_process.terminate()
        self.frequency_detector_process.join()
        self.frequency_detector.recorder.close()
        del self.frequency_detector

    def tune_all(self):
        pass

    def tune_one(self, string_number):

        target_frequencies = self.string_set.get_target_frequencies()
        string_target_frequency = target_frequencies[string_number][1]

        self.start_process()

        while True:

            self.pid_controller.setPoint(string_target_frequency)

            if self.values_correct_flag.value == 1:
                # start = time.clock()
                # print "Start: %s" % start
                
                freq = self.queue[-1]
                pid_value = self.pid_controller.update(freq)
                if round(pid_value, 1) > 1:
                    duty = round(self._map_values(pid_value, 1, 30, 6.7, 4.0), 1)
                elif round(pid_value, 1) < -1:
                    duty = round(self._map_values(pid_value, -30, -1, 9.8, 7.7), 1)
                else:
                    duty = 7.5
                self._servo_update(duty)
                string_tuned = self.check_one_tuned(string_number)

                # end = time.clock()
                # print "End: %s" % end
                # print "Eval: %s" % (end-start)   

                if string_tuned == True:
                    self._servo_update(7.5)          
                    break
                else:
                    continue
            else:
                self._servo_update(7.5)

        self.stop_process()

    def check_tuned(self):
        pass

    def check_one_tuned(self, string_number):
        target_frequencies = self.string_set.get_target_frequencies()
        string_target_frequency = target_frequencies[string_number][1]

        if string_target_frequency - 0.2 <= self.average_value.value <= string_target_frequency + 0.2:
            self.average_value.value = 0
            return True

    def _map_values(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def _servo_update(self, duty):
        try:
            if duty >= 4 and duty <= 11.0:
                servo.ChangeDutyCycle(duty)
            else:
                servo.ChangeDutyCycle(7.5)
                print "Servo stop"
        except:
            pass

