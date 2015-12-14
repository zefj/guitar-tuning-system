import time
import sys
import tuner

class UI(object):
    """docstring for UI"""
    def __init__(self):
        super(UI, self).__init__()
        self.options = {}
        self.string_set = tuner.StringSet()
        self.base()

    def base(self):
        while True:
            print "\n"
            print 10*"=" + "Main menu" + 10*"="
            print "Choose what you want to do:"
            print "1. Tune a string"
            print "2. Set options"      
            print "3. Display options"  
            choice = raw_input("> ")

            if choice == "1":

                t = tuner.TuningHandler(self.string_set)
                self.tuning(t)

            elif choice == "2":
                print "Jumping to options."
                self.set_sounds()

            elif choice == "3":
                print "Your options: %s" % self.string_set.get_target_frequencies()

            else:
                print "Choose correct option"

    def set_sounds(self):
        print 10*"=" + "Tuning options" + 10*"="
        print "Set sounds for each particular string."
        print "Choose one for each string from:"
        print "['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']"

        accepted_values = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.options = {}

        for i in range(0,6):
            while True:
                print 30*"-"
                choice = str(raw_input("Choose sound for string %s: " % str(i+1)))

                if choice not in accepted_values:
                    print "Choose correct sound!"
                else:
                    self.options[i] = choice
                    break

        self.string_set = tuner.StringSet(self.options)
        print "Options set."

    def get_sounds(self):
        return self.options

    def tuning(self, t):
        while True:
            print "\n"
            print 10*"=" + "Tuning sub-menu" + 10*"="
            print "Choose an action:"
            print "1. Tune all"
            print "2. Tune one string"
            choice = raw_input("> ")

            if choice == "1":
                print "Tune all not implemented yet."

            elif choice == "2":
                print "Choose which string to tune (1-6):"
                choice = raw_input("> ")

                if int(choice) in range(1, 7):
                    
                    parsed_choice = int(choice)-1
                    target_frequencies = self.string_set.get_target_frequencies()
                    print "\nTuning the string to sound %s, frequency %s Hz" % (target_frequencies.get(parsed_choice)[0], target_frequencies.get(parsed_choice)[1])

                    t.tune_one(parsed_choice)
                    print "\nString tuned!"
                else:
                    print "Enter correct string number!"

if __name__ == "__main__":

    try:
        ui = UI()
    except (KeyboardInterrupt, SystemExit):
        print "\nBye!"
        tuner.GPIO.cleanup()
        sys.exit(0)
