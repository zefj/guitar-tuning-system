Code for my engineer's thesis.

## HARDWARE AND SOFTWARE SYNTHESIS OF A STRINGED INSTRUMENTS TUNING SYSTEM
Filip Rec, 2016

### Abstract

Keeping a guitar in tune proves to be problematic for novice musicians around the world. A wide variety of electronic devices that indicate pitch is available on the market, however, properly using those implies certain knowledge of music theory, such as guitar tunings, and pitches that belong to them. The purpose of this research was to develop a prototype of an automated guitar tuning system, that would aid the user in this activity by estimating the pitch and rotating the guitar key appropriately. Using the Raspberry Pi and an algorithm with the autocorrelation method, it was possible to track the pitch of a captured audio sample with high precision. To achieve the goal, it was necessary for the frequency measurement to be conducted in near real-time, which required the instrument to be plugged into a sound card to allow constant data stream. Several tests confirmed that Raspberry Pi with Linux operating system handles simultaneous measurements and pulse-width modulation relatively well. Joined by a continuous rotation servomechanism and a PID regulator, the system is able to tune any string to the set point in a matter of seconds. In addition, the prototype was equipped with a touchscreen with graphical user interface, that allows easy control over the process and its basic settings, and guides the user by displaying notifications. Conducted tests confirmed that high accuracy and tuning speed were achieved no matter the instrument quality, and that any potential tuning error is mostly unnoticeable by an average guitarist.

