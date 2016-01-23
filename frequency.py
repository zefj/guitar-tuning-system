# -*- coding: utf-8 -*-
import numpy as np
from numpy.fft import rfft
import analyse
from scipy.signal import blackmanharris, fftconvolve
np.set_printoptions(threshold='nan')

import alsaaudio, struct

class Frequency(object):
    """docstring for Frequency"""
    def __init__(self):
        super(Frequency, self).__init__()
        # constants
        self.CHANNELS    = 1
        self.INFORMAT    = alsaaudio.PCM_FORMAT_S16_LE
        self.RATE        = 44100
        self.PERIODSIZE   = 2048
        self.CARD = 1

        # set up audio input
        self.recorder=alsaaudio.PCM(alsaaudio.PCM_CAPTURE, cardindex=self.CARD)
        self.recorder.setchannels(self.CHANNELS)
        self.recorder.setrate(self.RATE)
        self.recorder.setformat(self.INFORMAT)
        self.recorder.setperiodsize(self.PERIODSIZE)

    def parabolic(self, f, x):
        xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
        yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
        return (xv, yv)

    def find(self, condition):
        "Return the indices where ravel(condition) is true"
        res, = np.nonzero(np.ravel(condition))
        return res

    def measure(self):

        try:
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

            return freq

        except (IndexError, ValueError):
            return None, None
        
        except:
            self.recorder.close()
