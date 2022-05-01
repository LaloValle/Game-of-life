import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from Graphics import *
from Constant import *
from CellularAutomaton import *
from Layouts import *
import time
import warnings
warnings.filterwarnings('ignore') # Hides the warnings

# Delay in ms
DELAY_IN_MS = 1
# Number of elements by side in the grid
# the total number of cell is GRID_SIDE_SIZE^2
GRID_SIDE_ELEMENTS = 50
GRID_PADDING = 0
GRID_SIZE = 800
# Elements of the interface
SIDE_BAR_WIDTH = 250
BOTTOM_BAR_HEIGHT = 25
WINDOW_TITLE = 'Game of life'
# Statistical analysis
DENSITY = True
DENSITY_LOGARITHM = True
SHANNON_ENTROPY = True
# Use GPU for enhanced performance
GPU_ENHANCEMENT = True



# Global status variables
paused = True
reset = False
clear = False
actual_zoom = 1.0
game_graphics = None
cellular_automaton = None
second_start = 0

def play():
    global paused,second_start
    paused = False
    # second_start = time.time()

def stop():
    global paused
    paused = True

def restart():
    global reset
    reset = True

def cleared():
    global clear
    clear = True

def slider_move():
    SideBar.side_bar.move_drag_button(pygame.mouse.get_pos()[0])
    cellular_automaton.update_zeros_density(SideBar.side_bar.slider.value)

def plot_shannons_entropy():
    cellular_automaton.plot_shannons_entropy()

def set_actual_structure_glider():
    game_graphics.set_actual_structure(GLIDER)
    print('>> Change in actual structure')

def main():
    global paused,reset,clear
    global actual_zoom
    global cellular_automaton, game_graphics
    
    # Status variables
    done = False

    # Pygame configurations
    pygame.init()
    clock = pygame.time.Clock()
    
    # Window configuration
    window_display = 0
    window_size = (GRID_SIZE+SIDE_BAR_WIDTH,GRID_SIZE+BOTTOM_BAR_HEIGHT)
    window = pygame.display.set_mode(window_size,display=window_display)
    pygame.display.set_caption(WINDOW_TITLE)

    # Graphical elements
    # The grid for the interface cells gets created
    grid = Grid(window, (GRID_SIZE,GRID_SIZE), padding=GRID_PADDING, num_cols=GRID_SIDE_ELEMENTS, num_rows=GRID_SIDE_ELEMENTS) 
    side_bar = SideBar(DARK_BLACK,SIDE_BAR_WIDTH)
    bottom_bar = BottomBar(LIGHT_BLACK_1,BOTTOM_BAR_HEIGHT)
    game_graphics = GameGraphics.get_game_graphics(GRID_SIDE_ELEMENTS, grid, side_bar, bottom_bar)

    # Logical part of the program
    cellular_automaton = CellularAutomaton(GRID_SIDE_ELEMENTS,GPU_ENHANCEMENT)
    cellular_automaton.random_initial_config(game_graphics.get_cells())
    cellular_automaton.set_game_graphics(game_graphics)
    game_graphics.set_cellular_automaton(cellular_automaton)

    # Side bar functions to buttons
    side_bar.set_click_function(SideBar.PLAY_BUTTON,play)
    side_bar.set_click_function(SideBar.STOP_BUTTON,stop)
    side_bar.set_click_function(SideBar.RESTART_BUTTON,restart)
    side_bar.set_click_function(SideBar.CLEAR_BUTTON,cleared)
    side_bar.set_click_function(SideBar.DRAG_SLIDER_BUTTON,slider_move)
    side_bar.set_click_function(SideBar.DENSITY_BUTTON,cellular_automaton.plot_density)
    side_bar.set_click_function(SideBar.DENSITY_LOGARITHM_BUTTON,cellular_automaton.plot_density_logarithm)
    side_bar.set_click_function(SideBar.ENTROPY_BUTTON,cellular_automaton.plot_shannons_entropy)
    side_bar.set_click_function(SideBar.SAVE_BUTTON,cellular_automaton.save_evolution_space)
    side_bar.set_click_function(SideBar.UPLOAD_BUTTON,cellular_automaton.upload_evolution_space)
    side_bar.set_click_function(SideBar.GLIDER_BUTTON,set_actual_structure_glider)
    # Bottom bar space dimension and zoom
    bottom_bar.update_space_dimension_zoom(GRID_SIDE_ELEMENTS,actual_zoom)

    # Delay between each generation
    delay_start = time.time()

    # Main loop
    while not done:
        done = game_graphics.process_events()

        game_graphics.run_logic()

        game_graphics.display_frame(window)

        clock.tick(60)

        if reset:
            cellular_automaton.reset()
            game_graphics.reset()
            # Random configuration again
            cellular_automaton.random_initial_config(game_graphics.get_cells())
            reset = False

        if clear:
            cellular_automaton.reset()
            game_graphics.reset()
            clear = False

        if not paused:
            if (time.time()-delay_start)*1000 >= DELAY_IN_MS:
                # Next generation
                if DENSITY: cellular_automaton.density()
                if DENSITY_LOGARITHM: cellular_automaton.density_logarithm()
                if SHANNON_ENTROPY: cellular_automaton.shannon_entropy()
                cellular_automaton.compute_next_generation()
                # Restarts delay start time
                delay_start = time.time()
        else: delay_start = time.time()

        # if time.time()-second_start >= 1: paused = True
        # Changes de window size
        # if cuenta == 60: window = pygame.display.set_mode((500,500),display=window_display)
        # if cuenta == 120: window = pygame.display.set_mode((1200,1000),display=window_display)
        # https://www.pygame.org/docs/ref/display.html
    
    pygame.quit()

if __name__ == "__main__": main()