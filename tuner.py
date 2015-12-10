from multiprocessing import Process, Queue
import RPi.GPIO as GPIO

import frequency

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
p = GPIO.PWM(18, 50)
p.start(7.5)

class String(object):
    """
    String class. Object representation of a single string. Also calculates target frequency based on string number and sound name input.

    Initialise with:

    string = String(string_number, sound)
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
        standard_pitch = [1, 1, 2, 2, 2, 4]  ## narazie na sztywno, nie mam jeszcze pomyslu jak to obejsc dla innych, nietypowych gitar
        matching_index = next(sounds.index(elem) for elem in sounds if self.sound == elem)      
        return great[matching_index] * standard_pitch[self.string_number - 1]

    def _set_frequency(self):
        self.target_frequency = self._calculate_frequency()     

class StringSet(object):
    """
    StringSet creates an object that maps string 
    """
    def __init__(self, string_sound_dict):
        super(StringSet, self).__init__()
        # string_sound_list: __dict__, string_number: 'sound'
        self.string_sound_dict = string_sound_dict
        self.instantiate_strings()

    def instantiate_strings(self):
        self.string_objects = []

        for key, value in self.string_sound_dict.items():
            self.string_objects.append(String(key, value))

class TuningHandler(object):
    """docstring for TuningHandler"""
    def __init__(self, string_set):
        super(TuningHandler, self).__init__()
        self.string_set = string_set
    
    def tune_all(self):
        """
        Tu w zamysle bedzie algorytm strojenia wszystkich strun po kolei, jedna petla, na koncu wywolanie check_tuned, i dostrajanie pojedynczo poprzez tune_one. Taki jest zamysl, pewnie sie zmieni.
        """
        frequency_detector = frequency.Frequency()
        q = Queue()
        self.frequency_detector_process = Process(target = frequency_detector.measure, args=(q,))
        self.frequency_detector_process.start()

        while True:
            freq = q.get()
            print freq
            duty = round(self.map(freq, 70, 360, 4.0, 11.0), 1)
            self.servo_update(duty)

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def tune_one(self, string_number):
        pass

    def check_tuned(self):
        pass

    def check_one_tuned(self, string_number):
        pass

    def servo_update(self, duty):
        try:
            if duty >= 4 and duty <= 11.0:
                print duty
                p.ChangeDutyCycle(duty)
            else:
                p.ChangeDutyCycle(7.5)
                print "Servo stop"
        except:
            pass

if __name__ == "__main__":

    string_dict = {0: 'E', 1: 'A', 2: 'D', 3: 'F#'}

    string_set = StringSet(string_dict)

    # for string in t.string_objects:
    #   print string.target_frequency, string.sound

    t = TuningHandler(string_set)

    try:
        t.tune_all()
    except KeyboardInterrupt:
        GPIO.cleanup()
        t.frequency_detector_process.terminate()