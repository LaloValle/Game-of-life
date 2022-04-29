import time
from numpy import *
from numba import cuda
from Constant import MATRIX_BIN_TO_DEC

#
#   Kernels and CUDA functions
#
@cuda.jit(device=True)
def cuda_define_cell_status(alive_neighbours, anchor_cell, rule):
    if not anchor_cell: # Dead cell
        if alive_neighbours >= rule[2] and alive_neighbours <= rule[3]:
            return 1 # A cell borns
        else:
            return 0 # The cell keeps as dead

    # Alive cell
    if anchor_cell:
        if alive_neighbours < rule[0]: # Undepopulation
            return 0 # The cell dies in the next generation
        if alive_neighbours > rule[1]: # Overpopulation
            return 0 # The cell dies in the next generation
        else: 
            return 1 # The cell lives

@cuda.jit(device=True)
def cuda_count_neighbours(window):
    count = 0
    for y in range(3):
        for x in range(3):
            count += window[y,x]
    # If count greater than 0, gets the anchor cell value substracted
    if count > 0: count -= window[1,1]
    return count

@cuda.jit
def cuda_next_generation(space,out_space,alive_cells,changes_space,rule):
    x = cuda.threadIdx.x
    y = cuda.blockIdx.x
    # If its not the last 2 rows/columns
    if (x < space.shape[0]-2) and (y < space.shape[0]-2):
        # Clears whichever the past result was in the changes_space array
        changes_space[y+1,x+1] = 0
        # Count of neighbours
        alive_neighbours = cuda_count_neighbours(space[y:y+3,x:x+3])
        # Assigns the new value of the cell
        anchor_cell = space[y+1,x+1]; new_cell_value = cuda_define_cell_status(alive_neighbours,anchor_cell,rule)
        out_space[y+1,x+1] =  new_cell_value
        # When the status of the cell changed
        if new_cell_value != anchor_cell:
            # Puts 1 if the status of the cell changed
            changes_space[y+1,x+1] = 1
            # Updates the alive cells
            cuda.atomic.add(alive_cells, 0, 1 if new_cell_value == 1 else -1)

@cuda.jit
def cuda_update_results(space,out_space):
    x = cuda.threadIdx.x
    y = cuda.blockIdx.x
    # Evaluating if the coordinates correspond to those at the padding
    # and change it to copy the values of the borders to achieve the
    # toroid array
    x_index = -2 if x == 0 else (1 if x == (space.shape[0]-1) else x)
    y_index = -2 if y == 0 else (1 if y == (space.shape[0]-1) else y)
    space[y,x] = out_space[y_index,x_index]

@cuda.jit
def cuda_shannons_probability(space,neighbourhood_frecuency,conversion_matrix):
    x = cuda.threadIdx.x
    y = cuda.blockIdx.x
    # If its not the last 2 rows/columns
    if (x < space.shape[0]-2) and (y < space.shape[0]-2):
        neighbourhood_number = 0
        # Loops through the windows of the neighbourhood and adds to the
        # neighbhourhood_number variable the powers of 2 that corresponds
        # to a live cell. This allows to convert the neighbourhood into
        # a decimal number to be identified
        for y_nn in range(y,y+3):
            for x_nn in range(x,x+3):
                if space[y_nn,x_nn]: neighbourhood_number += conversion_matrix[y_nn-y,x_nn-x]
        # Increments the neighbourhood frecuency
        cuda.atomic.add(neighbourhood_frecuency ,neighbourhood_number, 1)

@cuda.jit
def cuda_change_cell(position,space,alive_cells):
    space[position[1],position[0]] = int(not space[position[1],position[0]])
    # Updates the alive cells
    cuda.atomic.add(alive_cells, 0, 1 if space[position[1],position[0]] else -1)

@cuda.jit
def cuda_clear_space(space,out_space):
    x = cuda.threadIdx.x
    y = cuda.blockIdx.x
    space[y,x] = 0
    out_space[y,x] = 0

class CUDACellularAutomaton():

    def __init__(self,space,dimensions):
        # Gets the shape of the space in only 2 dimensions
        self.dimensions = (0,0)
        self.alive_cells = array([0],int32)

        # Arrays in memory of the GPU
        self.space_rule = None
        self.space_device = None
        self.out_space_device = None
        self.alive_cells_device = None
        self.changes_space_device = None # Used to indicate which cells have changed after the generation function

    #
    # Class methods
    #
    def initial_configuration(self,space,alive_cells,rule):
        self.dimensions = space.shape
        # Restarts any memory reserved before
        self.space_device = None
        self.out_space_device = None
        self.alive_cells_device = None
        self.changes_space_device = None
        # Assigns the memory for the arrays
        self.space_rule = cuda.to_device(copy(rule))
        self.space_device = cuda.device_array_like(copy(space))
        self.out_space_device = cuda.to_device(copy(space))
        self.alive_cells_device = cuda.to_device(array([alive_cells],uint32))
        self.changes_space_device = cuda.device_array_like(copy(space))
        self.conversion_matrix = cuda.to_device(copy(MATRIX_BIN_TO_DEC))
        # Calls the kernel to update the new arrays and perform the toroidal padding assignments
        start_time = time.time()
        cuda_update_results[self.dimensions[0],self.dimensions[1]](self.space_device, self.out_space_device)
        end_time = time.time()
        print('<--- Initial configuration update ({:.6f}s) --->'.format(end_time-start_time))

    def clear(self):
        start_time = time.time()
        cuda_clear_space[self.dimensions[0],self.dimensions[1]](self.space_device,self.out_space_device)
        end_time = time.time()
        print('<--- Clear of space ({:.6f}s) --->'.format(end_time-start_time))
        # Easier to delete the existing array in the GPU memory with the alive cells count and assign a new one
        self.alive_cells_device = None
        self.alive_cells_device = cuda.to_device(self.alive_cells)

    def change_cell(self,index):
        index = array(index,int16)

        start_time = time.time()
        cuda_change_cell[1,1](index,self.space_device,self.alive_cells_device)
        end_time = time.time()
        print('<--- Change of value in cell[{},{}] ({:.6f}s) --->'.format(index[0], index[1], end_time-start_time))
        # print('GPU alive cells >> ', self.alive_cells_device.copy_to_host())

    def next_generation(self):
        # print(self.space_device.copy_to_host())
        start_time = time.time()
        cuda_next_generation[self.dimensions[0],self.dimensions[1]](self.space_device,self.out_space_device,self.alive_cells_device,self.changes_space_device,self.space_rule)
        cuda_update_results[self.dimensions[0],self.dimensions[1]](self.space_device, self.out_space_device)
        changes_space = self.changes_space_device.copy_to_host()
        end_time = time.time()
        print('<--- Next generation ({:.6f}s) --->'.format(end_time-start_time))
        return changes_space

    def shannon_entropy(self):
        neighbourhood_frecuency_space = cuda.to_device(array([0 for i in range(512)]))
        cuda_shannons_probability[self.dimensions[0],self.dimensions[1]](self.space_device,neighbourhood_frecuency_space,self.conversion_matrix)
        return neighbourhood_frecuency_space.copy_to_host()

    #
    # Getters and setters
    #
    def get_alive_cells(self):
        return self.alive_cells_device.copy_to_host()[0]

    def get_space(self):
        return self.space_device.copy_to_host()