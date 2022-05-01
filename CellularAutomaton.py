"""
=====================================================================================
author: Luis Eduardo Valle Martinez
date: March 14th of 2022
subject: Complex Systems
=====================================================================================
"""

import math
import time
from math import log10
from numpy import *
from random import random
from Constant import MATRIX_BIN_TO_DEC,R_Life,R_2
from matplotlib import pyplot as plt

from CUDACellularAutomaton import *
from Graphics import GameGraphics
from Layouts import BottomBar

class CellularAutomaton():
    """Class that represents the parameters and elements of the Conway's Game of Life
    The behavior of each cell in the space is addressed by the 4 main essential rules:
        1. Any live cell with fewer than two live neighbours dies(underpopulation)
        2. Any live cell with two or three live neighbours lives on to the next generation
        3. Any live cell with more than three live neighbours dies(overpopulation)
        4. Any dead cell with exactly three live neighbours borns as a live cell(reproduction)

    Attributes
    ----------
    dimensions : tuple
        Tuple of the dimensions of the grid
    
    grid : array
        2D array of the grid space

    states : dict
        The 2 possible states [0,1] used as keys, for a tuple value that represents
        first: The top limit of the probability of generation for the random initial
        configuration, and second: The color used to depict the cell state
    
    generation : int
        Number of the actual generation. By default starts with the value 0

    alive_cells
    newly_born_cells
    newly_deceased_cells
    
    Methods
    -------
    random_initial_config():
        Creates a random initial configuration taking in count the probability of each
        state for its assingment
    """

    def __init__(self,size,use_gpu,rule:tuple=R_Life):

        self.dimensions = (size,size,2)
        self.number_cells = size*size
        self.actual_rule = rule
        # Grid of 3 dimensions
        # Mimicking the rows and columns respectively, the first 2 dimensions
        # are the same, meanwhile the 3rd has 2 elements being the first used
        # for the actual cell grid states, and the 2nd element to calculate
        # the new grid for the next generation 
        self.space = zeros(self.dimensions,ubyte)
        # The padding at the first and last rows and columns is needed for the
        # window of 3x3, used to count the number of neigbours of the anchor element
        self.add_padding()
        # States
        self.zeros_density = 0.5
        # Dynamic variables through the process
        self.generations = 0
        self.alive_cells = 0
        # Graphics connection
        self.game_graphics = None

        # Record of statistical analysis
        self.density_record = []
        self.density_logarithm_record = []
        self.shannon_entropy_record = []

        # If enhancement of GPU
        self.ca_gpu = None
        self.gpu_enhancement = use_gpu
        if use_gpu:
            print('<--- Enhancement by GPU active --->')
            self.ca_gpu = CUDACellularAutomaton(self.space,self.dimensions)

    #
    # Configuration functions
    #
    def reset(self):
        # Common actions for GPU and CPU implementations
        self.update_alive_cells(self.alive_cells*-1)
        self.update_generations(self.generations*-1)
        self.density_record.clear()
        self.density_logarithm_record.clear()
        self.shannon_entropy_record.clear()
        self.space = zeros(self.dimensions,byte)
        self.add_padding()
        # GPU actions
        if self.gpu_enhancement:
            self.ca_gpu.clear()

    def set_game_graphics(self, game_graphics:GameGraphics):
        self.game_graphics = game_graphics

    def add_padding(self):
        rows_padding = zeros((self.dimensions[0],1,2),ubyte) # 1 row with the same number of columns and shape, except for the 2nd dimension that's only 1
        columns_padding = zeros((1,self.dimensions[1]+2,2),ubyte) # 1 column at the first dimension with same number of rows+2 and same elements in 3rd dimension
        self.space = concatenate((rows_padding,self.space,rows_padding),axis=1)
        self.space = concatenate((columns_padding,self.space,columns_padding),axis=0)
        self.toroid_padding()

    def random_initial_config(self, graphic_cells) -> array:
        # Loop that runs all the space elements and generates randomly an alive or dead cell
        for y in range(1,self.dimensions[1]+1):
            for x in range(1,self.dimensions[0]+1):
                if  self.zeros_density > random.random(): # Probability of an alive cell is the complement of the state 0
                    self.update_alive_cells(1)
                    self.space[y,x,0] = 1
                    graphic_cells[(y-1)*self.dimensions[0]+(x-1)].set_status(True)

        # GPU actions
        if self.gpu_enhancement:
            self.ca_gpu.initial_configuration(self.space[:,:,0],self.alive_cells,self.actual_rule)

    #
    # Update of dynamic variables and the texts showed in the interface
    #
    def update_alive_cells(self,added_cells:int):
        self.alive_cells += added_cells
        BottomBar.bottom_bar.update_alive_cells(self.alive_cells)

    def update_generations(self,added_generations:int):
        self.generations += added_generations
        BottomBar.bottom_bar.update_generations(self.generations)

    def update_zeros_density(self,density):
        self.zeros_density = density

    #
    # Functions while running the cellular automaton
    #
    def define_cell_status(self,alive_neighbours, anchor_cell):
        # Substracts the anchor cell value because the method
        # recives the alive_neighbours count before taking in 
        # count the value of the anchor cell
        alive_neighbours -= anchor_cell

        if not anchor_cell: # Dead cell
            if alive_neighbours >= self.actual_rule[2] and alive_neighbours <= self.actual_rule[3]:
                return 1 # A cell borns
            else:
                return 0 # The cell keeps as dead

        # Alive cell
        if anchor_cell:
            if alive_neighbours < self.actual_rule[0]: # Undepopulation
                return -1 # The cell dies in the next generation
            if alive_neighbours > self.actual_rule[1]: # Overpopulation
                return -1 # The cell dies in the next generation
            else: 
                return 0 # The cell lives

    def toroid_padding(self):
        self.space[0] = self.space[-2] # The first padding row is the last row with valid cells
        self.space[-1] = self.space[1] # The last padding row is the first row with valid cells
        self.space[:,0] = self.space[:,-2] # The first padding column is the last column with valid cells
        self.space[:,-1] = self.space[:,1] # The last padding column is the first column with valid cells

    def compute_next_generation(self):
        time_start = time.time()
        # CPU process
        if not self.gpu_enhancement:
            self.toroid_padding()
            for y in range(self.dimensions[1]):
                for x in range(self.dimensions[0]):
                    window = copy(self.space[y:y+3,x:x+3,0])
                    alive_neighbours = window.sum()
                    new_status_cell = self.define_cell_status(alive_neighbours, copy(self.space[y+1,x+1,0]))
                    # The alive cells counter gets updated
                    self.update_alive_cells(new_status_cell)
                    # The new status of the cell gets saved in the second column of the 3rd dimension
                    self.space[y+1,x+1,1] = new_status_cell
                    # Only when the new_status cell changes then 
                    if new_status_cell != 0: self.game_graphics.update_cell_status(new_status_cell,(y,x))
            # Once the new states have been calculated, the new changes are applied
            self.space[:,:,0] = self.space.sum(axis=2)
            self.space[:,:,1] -= self.space[:,:,1] # The second columns returns to zeros
        # GPU process
        else:
            changed_cells = copy(self.ca_gpu.next_generation())
            # Look for the cell changed so that it can be show in the interface
            for y in range(1,self.dimensions[1]+1):
                for x in range(1,self.dimensions[0]+1):
                    if changed_cells[y,x] == 1:
                        self.game_graphics.update_cell_status(True,(y-1,x-1),invert=True)
            # Updates the alive cells
            self.update_alive_cells(self.ca_gpu.get_alive_cells() - self.alive_cells)
    
        # Increments the generations
        self.update_generations(1)

        print('>> Time for compute_next_generation({}): {:.3f}s'.format(self.generations,time.time()-time_start))
        

    #
    # Communication with external methods
    #
    def get_generations(self):
        return self.generations

    def change_cell(self,index,alive:bool):
        # The alive cells counter and graphical elements gets updated
        self.update_alive_cells(1 if alive else -1)
        
        # CPU actions
        if not self.gpu_enhancement:
            self.space[index[1],index[0],0] = int(alive)
            if (1 in index) or (self.dimensions[0] in index): self.toroid_padding()
        
        # GPU actions
        else:
            self.ca_gpu.change_cell(index)
    
    #
    # Statistical analysis
    #
    def density(self):
        self.density_record.append(int(self.alive_cells))

    def density_logarithm(self):
        self.density_logarithm_record.append(log10(self.alive_cells))
    
    def shannon_entropy(self):
        entropy = 0
        neighbourhood_frecuency = [ 0 for i in range(512) ]

        # CPU actions
        if not self.gpu_enhancement:
            for y in range(self.dimensions[1]):
                for x in range(self.dimensions[0]):
                    window = copy(self.space[y:y+3,x:x+3,0])
                    neighbourhood_number = (window*MATRIX_BIN_TO_DEC).sum()
                    neighbourhood_frecuency[neighbourhood_number] += 1
        # GPU actions
        else:
            neighbourhood_frecuency = self.ca_gpu.shannon_entropy()

        probability = 0.0
        for frecuency in neighbourhood_frecuency:
            if frecuency: # Different of 0
                probability = frecuency/self.number_cells
                entropy -= probability*math.log2(probability)

        self.shannon_entropy_record.append(entropy)

    def plot_density(self):
        if not self.density_record:
            print('<!!! No density of cells has been recorded !!!>')
            return False

        fig = plt.figure()
        ax = plt.axes()

        ax.set( xlabel = 'Generations',
                ylabel = 'Density',
                title = 'Alive Cells Density'
            )
        ax.grid()

        data = list(self.density_record)
        data = array(list(enumerate(list(data))))
        ax.scatter(data[:,0],data[:,1])
        ax.plot(data[:,0],data[:,1])

        plt.show()

    def plot_density_logarithm(self):
        if not self.density_logarithm_record:
            print('<!!! No logarithm density of cells has been recorded !!!>')
            return False

        fig = plt.figure()
        ax = plt.axes()

        ax.set( xlabel = 'Generations',
                ylabel = 'Density Logarithm',
                title = 'Logarithm Alive Cells Density'
            )
        ax.grid()

        data = list(self.density_logarithm_record)
        data = array(list(enumerate(list(data))))
        ax.scatter(data[:,0],data[:,1])
        ax.plot(data[:,0],data[:,1])

        plt.show()

    def plot_shannons_entropy(self):
        if not self.shannon_entropy_record:
            print('<!!! No shannons entropy has been recorded !!!>')
            return False

        fig = plt.figure()
        ax = plt.axes()

        ax.set( xlabel = 'Generations',
                ylabel = 'Entropy',
                title = 'Shannons Entropy'
            )
        ax.grid()

        data = list(self.shannon_entropy_record)
        data = array(list(enumerate(list(data))))
        ax.scatter(data[:,0],data[:,1])
        ax.plot(data[:,0],data[:,1])

        plt.show()
    
    #
    # Save and upload of generations
    #
    def save_evolution_space(self):
        filename = './saves/CA_generation_{}.csv'.format(self.generations)
        if self.gpu_enhancement: self.space[:,:,0] = self.ca_gpu.get_space()
        savetxt(
            filename,
            copy(self.space[1:-1,1:-1,0]),
            delimiter = ', ',
            fmt = '% s'
            )
        print('<--- File successfully saved as \"'+filename+'\" --->')

    def upload_evolution_space(self):
        aux_array = genfromtxt("./saves/upload.csv",delimiter=', '); aux_shape = aux_array.shape
        if (self.dimensions[0]-aux_shape[0] < 0) or (self.dimensions[1]-aux_shape[1] < 0):
            print('!!! The actual evolution space is smaller than the intended upload file !!!')
        # The upload array gets loaded in the programm
        else:
            # First the space gets cleaned
            self.reset()
            self.game_graphics.reset()
            if self.gpu_enhancement: self.ca_gpu.clear()
            initial_column = 1 + int((self.dimensions[1]-aux_shape[1])/2); initial_row = 1 + int((self.dimensions[0]-aux_shape[0])/2)
            # The new array gets saved in the saving_space and the evolution_space arrays
            self.space[initial_row:initial_row+aux_shape[0],initial_column:initial_column+aux_shape[1],0] = aux_array
            self.toroid_padding()
            # The graphical cells gets updated with the value of the new array
            for y in range(initial_row,initial_row+aux_shape[0]):
                for x in range(initial_column,initial_column+aux_shape[1]):
                    self.game_graphics.update_cell_status(bool(self.space[y,x,0]),[(y-1),(x-1)])
            # Dynamic variables
            self.alive_cells = int(aux_array.sum())
            self.generations = 0
            if self.gpu_enhancement: self.ca_gpu.initial_configuration(self.space[:,:,0],self.alive_cells,self.actual_rule)
            print('<--- New configuration successfully uploaded --->')
