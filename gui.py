import pygame, sys, os
from pygame.locals import *
from evdev import InputDevice, categorize, ecodes

def map_values(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

os.environ["SDL_FBDEV"] = "/dev/fb1"
# Uncomment if you have a touch panel and find the X value for your device
#os.environ["SDL_MOUSEDRV"] = "python-evdev"
#os.environ["SDL_MOUSEDEV"] = "/dev/input/event1"
pygame.display.init()

# set up the window
DISPLAYSURF = pygame.display.set_mode((0, 0))
pygame.display.set_caption('Drawing')

# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

# draw on the surface object
DISPLAYSURF.fill(WHITE)

def handle_pos(code, value):
	global input_position
	if code == 0:
		mapped_value = map_values(value, 75, 1905, 0, 479)
		input_position[0] = mapped_value
	elif code == 1:
		mapped_value = map_values(value, 100, 1988, 0, 319)
		input_position[1] = mapped_value
	if input_position[0] and input_position[1]:
		pygame.mouse.set_pos(input_position)
		input_position = [None, None]

dev = InputDevice('/dev/input/event1')
input_position = [None, None]

# run the game loop
while True:
	event = dev.read_one()
	if event and  event.type == ecodes.EV_ABS:
		handle_pos(event.code, event.value)
		print event.value, event.type, event.code

	pygame.display.update()
