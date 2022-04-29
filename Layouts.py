from turtle import width
import pygame
import numpy as np
from Constant import *
import Graphics as grph
from GraphicalComponents import *


class Grid():
    """Class that defines a grid given a position, number of columns, rows and a padding
    Helps to locate easilly a list of elements in a grid layout

    Methods
    -------
    get_element_size(self) : self.element_size
        Getter for the size of the elements in the grid
    
    calculate_element_size(self) :
        Method that computes the size of each element depending on the number of columns
        and padding specified when creating the grid
    
    locale_elements(self,list_elements) :
        Locates the elements provided in the grid from left to right, and top to bottom
    """

    def __init__(self, window, size:tuple, coord:tuple=(0,0), num_cols:int=2, num_rows:int=2, padding:int=5):
        self.window = window
        self.size = np.array(size,np.uint16)
        self.coord = coord
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.padding = padding
        self.element_size = self.calculate_element_size()

    def get_element_size(self):
        return self.element_size

    def calculate_element_size(self):
        # Compute of the size of each element
        return tuple(np.around( 
                        (self.size - np.array([self.padding*(self.num_cols+1),self.padding*(self.num_rows+1)],np.uint16)) /  # The original size of the grid gets substracted the number of paddins by row and column
                        np.array([self.num_cols,self.num_rows],np.uint16)) # The resultant array gets divided between the number of columns and rows respectively
                ) 

    def locate_elements(self,list_elements):
        y_pos = self.padding+self.coord[1] # Initial position with just the padding added to the original y
        # Loop in number of rows
        for row in range(self.num_rows):
            x_pos = self.padding+self.coord[0] # Initial position with just the padding added to the oiriginal x
            # Loop in number of columns
            for column in range(self.num_cols):
                index = row*self.num_cols+column
                if index < len(list_elements): list_elements[index].move((int(x_pos),int(y_pos)))
                x_pos += self.padding+self.element_size[0] # The next element must be placed in the x position with added padding and width of the previous element
            y_pos += self.padding+self.element_size[1] # The next row of elements must be placed in the y position with added padding and width of the previous elements


class SideBar():
    """Simple rectangle used as side bar

    Methods
    -------
    draw(self,window) :
        Draws a rectagle at the right side with a given width and background color
    """

    # Singleton Class
    side_bar = None

    PLAY_BUTTON = 0
    STOP_BUTTON = 1
    RESTART_BUTTON = 2
    CLEAR_BUTTON = 3
    DRAG_SLIDER_BUTTON = 4
    DENSITY_BUTTON = 5
    DENSITY_LOGARITHM_BUTTON = 6
    ENTROPY_BUTTON = 7
    ALIVE_COLOR_INPUT = 8
    DEAD_COLOR_INPUT = 9
    SAVE_BUTTON = 10
    UPLOAD_BUTTON = 11

    def __init__(self,color_background:tuple,width:int=250,bottom_margin:int=0):
        # The only instance is the first created in the main
        SideBar.side_bar = self
        
        self.color_background = color_background
        self.width = width
        self.bottom_margin = bottom_margin
        self.padding = 15

        # The position and size gets define according to the windows size
        window_size = pygame.display.get_window_size()
        self.rectangle = pygame.Rect(
            ( window_size[0]-width, 0 ),
            ( width, window_size[1]-bottom_margin )
        )

        # Graphical elements inside the bar
        self.graphical_elements = []
        self.slider = self.set_slider()
        self.graphical_elements.append(self.slider)
        # Sections
        self.plot_section = Section(self.rectangle.x,180,self.rectangle.width,self.padding,'PLOTTING')
        self.colors_section = Section(self.rectangle.x,285+self.padding,self.rectangle.width,self.padding,'COLORS')
        self.graphical_elements.append(self.plot_section)
        self.graphical_elements.append(self.colors_section)
        # Graphical sprites inside the bar
        self.graphical_sprites = pygame.sprite.Group()
        self.graphical_sprites.add(self.set_play_button())
        self.graphical_sprites.add(self.set_stop_button())
        self.graphical_sprites.add(self.set_restart_button())
        self.graphical_sprites.add(self.set_clear_button())
        self.graphical_sprites.add(self.slider.get_drag_button())
        self.graphical_sprites.add(self.set_density_button())
        self.graphical_sprites.add(self.set_logarithm_button())
        self.graphical_sprites.add(self.set_entropy_button())
        self.graphical_sprites.add(self.set_alive_color_input())
        self.graphical_sprites.add(self.set_dead_color_input())
        self.graphical_sprites.add(self.set_save_button())
        self.graphical_sprites.add(self.set_upload_button())


    def set_click_function(self,button,function):
        self.graphical_sprites.sprites()[button].click_function = function

    def set_play_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 20
        image_size = 25
        # The position in the center horizontally and at the top
        x = window_size[0] - self.width/2 - radius
        y = self.padding + radius + 5

        return CircularButton(x,y,radius,image_size,image_path='./images/play_w.png')

    def set_stop_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 20
        image_size = 15
        x = window_size[0] - self.width/2 - 2*radius - 15*2
        y = self.padding + radius + 5

        return CircularButton(x,y,radius,image_size,image_path='./images/stop_w.png')

    def set_restart_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 20
        image_size = 20
        x = window_size[0] - self.width/2 + 1.5*radius
        y = self.padding + radius + 5

        return CircularButton(x,y,radius,image_size,image_path='./images/restart_w.png')

    def set_clear_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 18
        image_size = 13
        x = window_size[0] - 2*radius - self.padding
        y = self.rectangle.height - 2*radius - 2*self.padding
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/clear_w.png')
    
    def set_density_button(self):
        # Size of the button
        radius = 30
        image_size = 30
        x = self.rectangle.x + self.padding
        y = 180 + 30 + self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/density_w.png')

    def set_logarithm_button(self):
        # Size of the button
        radius = 30
        image_size = 30
        x = self.rectangle.x + self.padding + 8 + 2*radius
        y = 180 + 30 + self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/logarithm_w.png')
    
    def set_entropy_button(self):
        # Size of the button
        radius = 30
        image_size = 30
        x = self.rectangle.x + self.padding + 16 + 4*radius
        y = 180 + 30 + self.padding
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/entropy_w.png')

    def set_slider(self):
        width = self.rectangle.width - 2*self.padding - 10
        x = self.rectangle.x + self.padding + 5
        y = 100

        return Slider(x,y,width)

    def set_alive_color_input(self):
        x = self.rectangle.x + self.padding + 5
        y = self.colors_section.header_rect.y + 30 + self.padding
        background_color = grph.GameGraphics.cells_colors[1]
        input = Input(x,y,45,label='Alive',width=FONT.size('Alive')[0]+50,allow_focus=False,background_color=background_color)
        input.set_click_function(self.change_alive_cell_color)
        return input

    def set_dead_color_input(self):
        x = self.rectangle.x + 2*self.padding + 5 + 95
        y = self.colors_section.header_rect.y + 30 + self.padding
        background_color = grph.GameGraphics.cells_colors[0]
        input = Input(x,y,45,label='Dead',width=FONT.size('Dead')[0]+50,allow_focus=False,background_color=background_color)
        input.set_click_function(self.change_dead_cell_color)
        return input

    def set_save_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 18
        image_size = 13
        x = window_size[0] - 4*radius - 8 - self.padding
        y = self.rectangle.height - 2*radius - 2*self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/save_w.png')

    def set_upload_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 18
        image_size = 13
        x = window_size[0] - 6*radius - 16 - self.padding
        y = self.rectangle.height - 2*radius - 2*self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/upload_w.png')

    # Functions when colors of cells clicked
    def change_dead_cell_color(self):
        input = self.graphical_sprites.sprites()[SideBar.DEAD_COLOR_INPUT]
        index_color_actual = COLORS_LIST.index(input.background_color)
        new_color = COLORS_LIST[index_color_actual+1 if index_color_actual < len(COLORS_LIST)-1 else 0] 
        grph.GameGraphics.cells_colors[0] = new_color
        input.background_color = new_color
        grph.GameGraphics.game_graphics.group_cells.update()
    
    def change_alive_cell_color(self):
        input = self.graphical_sprites.sprites()[SideBar.ALIVE_COLOR_INPUT]
        index_color_actual = COLORS_LIST.index(input.background_color)
        new_color = COLORS_LIST[index_color_actual+1 if index_color_actual < len(COLORS_LIST)-1 else 0] 
        grph.GameGraphics.cells_colors[1] = new_color
        input.background_color = new_color
        grph.GameGraphics.game_graphics.group_cells.update()

    def move_drag_button(self,x):
        self.slider.move_drag_button(x)

    def stop_button_pressed(self,button):
        self.graphical_sprites.sprites()[button].pressed_once = False

    def draw(self,window):
        pygame.draw.rect(window,self.color_background,self.rectangle)
        # All the sprite elements get draw
        for element in self.graphical_elements:
            element.draw(window)
        self.graphical_sprites.draw(window)
        # Inputs cells colors
        self.graphical_sprites.sprites()[SideBar.DEAD_COLOR_INPUT].draw(window)
        self.graphical_sprites.sprites()[SideBar.ALIVE_COLOR_INPUT].draw(window)

    def get_graphical_sprites(self):
        return self.graphical_sprites


class BottomBar():
    """Simple rectangle used as bottom bar

    Methods
    -------
    draw(self,window) :
        Draws a rectagle at the bottom with a given height and background color
    """

    # Singleton Class
    bottom_bar = None

    def __init__(self,color_background:tuple,height:int=35):
        BottomBar.bottom_bar = self
        
        self.color_background = color_background
        self.height = height

        # The position and size gets define according to the windows size
        window_size = pygame.display.get_window_size()
        self.rectangle = pygame.Rect(
            ( 0, window_size[1]-height ),
            ( window_size[0], height )
        )

        # Creation of texts
        self.texts = []
        self.generations_text = Text((10,3+self.rectangle.y),'Generations:')
        self.alive_cells_text = Text((self.rectangle.width-30-FONT.size('Alive Cells: 0')[0], 3+self.rectangle.y),'Alive Cells: 0')
        self.space_dimension_zoom_text = Text((self.rectangle.width/2-FONT.size('100x100(1.0)')[0], 3+self.rectangle.y),'100x100(1.0)')
        self.texts.append(self.generations_text)
        self.texts.append(self.alive_cells_text)
        self.texts.append(self.space_dimension_zoom_text)
        
    def draw(self,window):
        pygame.draw.rect(window,self.color_background,self.rectangle)

        for txt in self.texts:
            txt.print(window)

    def update_generations(self,generations):
        self.generations_text.update('Generations:'+str(generations))

    def update_alive_cells(self,alive_cells):
        self.alive_cells_text.update('Alive Cells: '+str(alive_cells))

    def update_space_dimension_zoom(self,space_dimension,zoom):
        self.space_dimension_zoom_text.update('{}x{}({}%)'.format(space_dimension,space_dimension,zoom))