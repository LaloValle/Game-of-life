import pygame
from numpy import array

# Colors
DARK_BLACK = (28,29,32)
LIGHT_BLACK_1 = (40,44,52)
LIGHT_BLACK_2 = (53,61,76)
# Gray pair
WHITE = (192,203,221)
GRAY = (162,170,185)
# Blue pair
BLUE = (17,192,186)
LIGHT_BLUE = (168,234,232)
# LIGHT_BLUE = (79,189,186)
# Yellow pair
YELLOW = (234,194,76)
LIGHT_YELLOW = (234,213,150)
# Red pair
RED = (196,39,73)
LIGHT_RED = (234,159,175)
# Green pair
GREEN = (0,161,157)
LIGHT_GREEN = (79,189,186)

COLORS_LIST = [DARK_BLACK,LIGHT_BLACK_1,LIGHT_BLACK_2,WHITE,GRAY,BLUE,LIGHT_BLUE,YELLOW,LIGHT_YELLOW,RED,LIGHT_RED,GREEN,LIGHT_GREEN]


# Fonts
pygame.font.init()
FONT = pygame.font.SysFont('Silka',15,False,False)
SMALL_FONT = pygame.font.SysFont('Silka',12,False,False)

# Wighted matrix for binary to decimal conversion
MATRIX_BIN_TO_DEC = array([
    [1 ,  2 ,   4],
    [8 ,  16 ,  32],
    [64 , 128 , 256],
])

# Rules
R_Life = (2, 3, 3, 3)
R_2 = (7, 7, 2, 2)