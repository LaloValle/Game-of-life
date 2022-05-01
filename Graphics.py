import pygame
import numpy as np
from Constant import *
from Layouts import *


class GameGraphics():

    game_graphics = None
    cells_colors = [WHITE,LIGHT_BLACK_2]

    # Singleton Class
    def get_game_graphics(number_columns:int=0 ,grid:Grid=None, side_bar:SideBar=None, bottom_bar:BottomBar=None):
        if GameGraphics.game_graphics == None: GameGraphics.game_graphics = GameGraphics(number_columns=number_columns, grid=grid, side_bar=side_bar, bottom_bar=bottom_bar)
        return GameGraphics.game_graphics

    def __init__(self, number_columns, grid:Grid, side_bar:SideBar=None, bottom_bar:BottomBar=None):
        # Interface drawable sprite elements
        self.drawable_elements = []
        self.collidable_elements = pygame.sprite.Group()
        
        # Grid for the cells
        self.grid = grid

        # Array of cells
        self.cells = []
        self.group_cells = pygame.sprite.Group()
        self.space_side_number_elements = number_columns
        self.create_cells(self.grid.get_element_size())

        # Mouse button states
        self.click_pressed = False
        self.changed_cells = []
        self.actual_structure = array([]) # Array for placing pre-defined structures in the evolution space
        self.structure_just_printed = False

        # Logical Game of Life instance
        self.cellular_automaton = None

        # Collapsable pointer
        self.pointer = MousePointer((1,1))

        # Graphical elements
        self.side_bar = side_bar
        self.bottom_bar = bottom_bar
        self.add_graphical_element( self.side_bar )
        self.add_graphical_element( self.bottom_bar )
        self.collidable_elements.add(self.side_bar.get_graphical_sprites())
        # Set of the elements that must be executed their respective exit function
        self.next_exit_elements = set()
        self.next_stop_pressed = set()
        
    def reset(self):
        # Mouse button states
        self.click_pressed = False
        self.changed_cells = []
        # Set of the elements that must be executed their respective exit function
        self.next_exit_elements = set()
        self.next_stop_pressed = set()
        # kills all the cells
        for cell in self.cells:
            cell.alive = False
            cell.color_cell()


    # PyGame loop related methods
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    self.click_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # Left click
                    self.click_pressed = False
                    self.structure_just_printed = False
                    # The 'status_changed_click' variable in the cells returns to False
                    while self.changed_cells: self.changed_cells.pop().status_changed_click = False
                if event.button == 3: # Right click
                    if self.actual_structure.size: # There's an structure waiting to be located in the evolution space
                        self.actual_structure = np.rot90(self.actual_structure)
            if event.type == pygame.MOUSEWHEEL:
                print(event)
            # Looks for key press
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n: 
                    self.cellular_automaton.compute_next_generation()
                    # Statistical analysis
                    self.cellular_automaton.density()
                    self.cellular_automaton.density_logarithm()
                    self.cellular_automaton.shannon_entropy()
                    print('<--- Next Generation --->')
        return False

    def run_logic(self):
        self.pointer.update()
        self.collidable_elements.update()

        # Verifies if a collapsible element of the UI collided
        collaided_elements = pygame.sprite.spritecollide(self.pointer,self.collidable_elements,False)
        

        # If the click is pressed then the cells collapsed change status
        if self.click_pressed: 
            self.change_cells_status()
        # if stop clicking
        else:
            # If there's elements that where pressed
            if self.next_stop_pressed:
                for element in self.next_stop_pressed:
                    element.pressed_once = False
                    element.stop_click()
                self.next_stop_pressed.clear()
            # If there's elements that collided while not clicked
            elif self.collidable_elements and self.next_exit_elements:
                remove_element = None
                for element in self.next_exit_elements:
                    # Identifies if the element no longer collides with the pointer
                    if element not in collaided_elements:
                        element.exit()
                        remove_element = element
                # The elements get removed from the set
                if remove_element != None:
                    self.next_exit_elements.remove(remove_element)
        
        # Verifies the state of those elements collided
        for element in collaided_elements:
            if self.click_pressed:
                element.click()
                self.next_stop_pressed.add(element)
            elif not self.click_pressed:
                element.hover(); self.next_exit_elements.add(element)
        
    def display_frame(self,window):

        window.fill(LIGHT_BLACK_2)

        self.group_cells.draw(window)
        for graphical_element in self.drawable_elements:
            graphical_element.draw(window)

        pygame.display.flip()

    # Auxiliar methods
    def add_graphical_element(self,element):
        self.drawable_elements.append(element)

    def create_cells(self,cell_size):
        # The number of cells gets created
        for row in range(self.space_side_number_elements):
            for column in range(self.space_side_number_elements):
                cell_aux = Cell(cell_size,(column+1,row+1)) # The columns and rows gets added 1 to compensate the padding of the logic array
                self.cells.append(cell_aux)
                self.group_cells.add(cell_aux)
        # The cells get located in the grid
        self.grid.locate_elements(self.cells)

    def change_cells_status(self):
        for cell in pygame.sprite.spritecollide(self.pointer, self.group_cells, False):
            # If there's an structure then it's printed
            if self.actual_structure.size:
                self.print_structure(cell.index)
            # If the cell changed it's status
            if not self.structure_just_printed:
                if cell.change_status():
                    self.changed_cells.append(cell)
                    # The kill/born of the cell get's also changed in the logic
                    self.cellular_automaton.change_cell(cell.index,cell.alive)

    def print_structure(self,index_start_cell):
        if index_start_cell[0] <= (self.grid.num_cols - 2):
            print('Index:',index_start_cell, self.grid.num_cols)
            for row in range(3):
                for column in range(3):
                    new_status = bool(self.actual_structure[row,column])
                    aux_cell = self.cells[(row+index_start_cell[1]-1)*self.grid.num_cols+index_start_cell[0]-1+column]
                    aux_cell.alive = new_status
                    aux_cell.update()
                    if new_status: self.cellular_automaton.change_cell(aux_cell.index,True)
                    self.structure_just_printed = True
        self.actual_structure = np.array([])

    # External communications methods
    def set_cellular_automaton(self,cellular_automaton):
        self.cellular_automaton = cellular_automaton
    
    def set_actual_structure(self,structure):
        self.actual_structure = np.copy(structure)

    def get_cells(self):
        return self.cells

    def update_cell_status(self,status,cell_position,invert:bool=False):
        cell_aux = self.cells[ cell_position[0]*self.space_side_number_elements + cell_position[1]]
        # When invert active changes the state of the cell to the contrary of the current cell state
        if invert: cell_aux.set_status(not cell_aux.alive)
        # Specifies an specific status for the cell
        else: self.cells[ cell_position[0]*self.space_side_number_elements + cell_position[1]].set_status(True if status == 1 else False)






class Cell(pygame.sprite.Sprite):

    def __init__(self, size:tuple, index:tuple, alive:bool=False):
        super().__init__()

        self.status_changed_click = False
        self.alive = alive
        # Index of the cell in the general grid
        self.index = index
        # The cell and the rect inside gets defined
        self.image = pygame.Surface(size)
        self.image.fill(GameGraphics.cells_colors[int(self.alive)])
        # The rect of the cell is asigned so in 
        # further methods can be used to move it
        self.rect = self.image.get_rect()

    def update(self):
        # Updates the background color of the cell
        self.image.fill(GameGraphics.cells_colors[int(self.alive)])

    def resize(self,size:tuple):
        self.rect.width, self.rect.height = size

    def move(self,coord:tuple):
        self.rect.x = coord[0]
        self.rect.y = coord[1]

    def color_cell(self):
        self.image.fill(GameGraphics.cells_colors[int(self.alive)])

    def set_status(self,status):
        self.alive = status
        self.color_cell()

    def change_status(self):
        if not self.status_changed_click:
            self.alive = not self.alive
            self.color_cell()
            self.status_changed_click = True
            return True
        return False