# -*- coding: utf-8 -*-
import numpy as np
from numpy.fft import rfft
import analyse
from scipy.signal import blackmanharris, fftconvolve
np.set_printoptions(threshold='nan')

# to calkiem dziala, czasem daje wartosc odpowiednia, potem duzo noisu i harmonicsow.
import alsaaudio, struct
# from aubio.task import *
import time
class Frequency(object):
    """docstring for Frequency"""
    def __init__(self):
        super(Frequency, self).__init__()

        # constants
        self.CHANNELS    = 1
        self.INFORMAT    = alsaaudio.PCM_FORMAT_S16_LE
        self.RATE        = 44100
        self.FRAMESIZE   = 2048
        # self.PITCHALG    = aubio_pitch_yin
        # self.PITCHOUT    = aubio_pitchm_freq
        self.CARD = 1

        # set up audio input
        self.recorder=alsaaudio.PCM(alsaaudio.PCM_CAPTURE, cardindex=self.CARD)
        self.recorder.setchannels(self.CHANNELS)
        self.recorder.setrate(self.RATE)
        self.recorder.setformat(self.INFORMAT)
        self.recorder.setperiodsize(self.FRAMESIZE)

    def parabolic(self, f, x):
        xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
        yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
        return (xv, yv)

    def find(self, condition):
        "Return the indices where ravel(condition) is true"
        res, = np.nonzero(np.ravel(condition))
        return res

    def append_to_queue(self, freq, queue, values_correct_flag, average_value):
        """
        Hacky implementation of limited length list.
        """
        if len(queue) > 9:
            queue.pop(0)
            queue.append(freq)
            self.validate_values(queue, values_correct_flag, average_value)
        else:
            values_correct_flag.value = 0
            queue.append(freq)
            
    def validate_values(self, queue, values_correct_flag, average_value):
        """
        Value validation based on two criterion: standard deviation of last 10 values and maximum expected frequency. Sets a shared flag for tuning handler. 
        """
        standard_deviation = np.std(queue)

        if standard_deviation < 3 and max(queue) < 600:
            values_correct_flag.value = 1
            self.calculate_average(queue, average_value)
        else:
            values_correct_flag.value = 0

    def calculate_average(self, queue, average_value):
        average_value.value = sum(queue)/len(queue)

    def measure(self, queue, values_correct_flag, average_value):

        while True:
            try:
                start_time = time.clock()
                #print "Start: %s" % start_time

                [length, data] = self.recorder.read()
                signal = np.fromstring(data, dtype=np.int16)

                corr = fftconvolve(signal, signal[::-1], mode='full')
                corr = corr[len(corr)/2:]

                # Find the first low point
                d = np.diff(corr)

            
                start = self.find(d > 0)[0]
                # Find the next peak after the low point (other than 0 lag).  This bit is
                # not reliable for long signals, due to the desired peak occurring between
                # samples, and other peaks appearing higher.
                # Should use a weighting function to de-emphasize the peaks at longer lags.
                peak = np.argmax(corr[start:]) + start
                px, py = self.parabolic(corr, peak)
                freq = self.RATE/px
                self.append_to_queue(freq, queue, values_correct_flag, average_value)
                print freq

                end_time = time.clock()
                #print "End: %s" % end_time
                print "Eval: %s" % (end_time-start_time) 

            except (IndexError, ValueError):
                pass
                
            except (KeyboardInterrupt, SystemExit):
                self.recorder.close()


