import math

import pygame

# display settings
# WIDTH, HEIGHT = 160, 90
# WIDTH, HEIGHT = 192, 108
WIDTH, HEIGHT = 320, 180
# WIDTH, HEIGHT = 640, 360
DISPLAY_FLAGS = pygame.SCALED

# time settings
FPS = 60
FRAME_CONSTANT = 60

# tile settings
TILE_SIZE = 16

# map settings (info more like)
MAP_WIDTH, MAP_HEIGHT = 40, 20

# shadow settings
MAX_RAY_DISTANCE = math.ceil(math.sqrt(WIDTH ** 2 + HEIGHT ** 2))
