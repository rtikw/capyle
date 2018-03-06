# Name: Forest Fire Simulation
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np

water_x = 33
water_y = 31
water_x_end = water_x + 10
water_y_end = water_y + 10

terrain_numbers = np.full([50,50], 1)
terrain_numbers[10:15, 5:15] = 2
terrain_numbers[5:35, 32:35] = 3
terrain_numbers[30:40, 15:25] = 4
terrain_numbers[water_x : water_x_end, water_y : water_y_end] = 2

#Fuel resource level for each terrain type i.e. chaparral burns for 48 steps (4 days)
terrain_fuel_level = {1:48,2:0,3:4,4:252}
#Ignition threshold needed to start fire for each terrain type
terrain_ignition_threshold = {1:2,2:np.inf,3:1,4:5}

wind_directions = {'NW':0,'N':1,'NE':2,'E':3,'SE':4,'S':5,'SW':6,'W':7}

#neighbourstate indexes in clockwiwe order (rather than from left to right)
neighbour_clockwise = [0,1,2,4,7,6,5,3]

#Set wind direction according to wind_directions dictionary
wind_direction_index = wind_directions['S']
#Find index of direction opposing the wind
zero_deg_index = [(wind_direction_index + 4)%8]
#Find indexes of directions closest to opposing direction
one_deg_index = [(zero_deg_index[0] - 1)%8,(zero_deg_index[0] + 1)%8]
#Find indexes of the other directions
two_plus_deg_index = list(set([i for i in range(8)])-set(zero_deg_index)-set(one_deg_index))

#Convert indexes for use in neighbourstates
zero_deg_index_neighbour = [neighbour_clockwise[i] for i in zero_deg_index]
one_deg_index_neighbour = [neighbour_clockwise[i] for i in one_deg_index]
two_plus_deg_index_neighbour = [neighbour_clockwise[i] for i in two_plus_deg_index]




def transition_func(grid, neighbourstates, neighbourcounts, ignition_level, fuel_level):
    #Each step is 2 hours
    #Burning cells
    burning = (grid == 5)

    ignition_incr = np.zeros((50,50))
    #Find states with a neighbouring burning state in the direction opposing the wind
    zero_deg = (neighbourstates[zero_deg_index_neighbour[0]] == 5)
    one_deg = [(neighbourstates[i] ==5) for i in one_deg_index_neighbour]
    two_plus_deg = [(neighbourstates[i] ==5) for i in two_plus_deg_index_neighbour]

    #Increase ignition values by varying amounts depending on direction of wind
    ignition_incr[zero_deg] += 2
    for i in one_deg:
        ignition_incr[i] += 1.5

    for i in two_plus_deg:
        ignition_incr[i] += 1


    #Calculate ignition values for unburnt cells
    ignition_level -= 0.4*ignition_incr
    #If ignition threshold is reached, ignite cell
    ignite = (ignition_level <= 0) & (grid != 5) & (grid != 0)

    #Decrease fuel level of burning states
    fuel_level[burning] -= 1

    #If fuel level reaches zero, it burns out
    grid[fuel_level == 1] = 0

    #burns if ignite is satisfied
    grid[ignite] = 5

    #todo
    #Fine-tune ignition thresholds and the effect of the number of neighbours on the ignition value
    #Implement corner neighbours having less effect on ignition values
    #Implement wind affecting ignition values X
    #Implement wind strength?
    #Implement regrowth of terrain?
    #Implement gradient affecting ignition values?
    #Implement short and long-term interventions

    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    config.dimensions = 2

    config.title = "Forest Fire Simulation"

    # States:
    # 0: Burnt out, 1: Chaparral, 2: Lake, 3: Canyon, 4: Forest, # 5: Burning
    config.states = range(6)
    config.state_colors = [(0,0,0),(215/255,211/255,15/255),(15/255,171/255,223/255),
        (87/255,113/255,122/255),(11/255,154/255,10/255),(207/255,43/255,8/255)]

    config.num_generations = 400
    config.grid_dims = (50,50)
    config.initial_grid = terrain_numbers
    config.wrap = False

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    ignition_level = np.zeros((50,50))
    fuel_level = np.zeros((50,50))

    #Set fuel resource for each cell based on terrain
    fuel_level = np.vectorize(terrain_fuel_level.get)(terrain_numbers)

    #Set ignition Threshold for each cell based on terrain
    ignition_level = np.vectorize(terrain_ignition_threshold.get,
        otypes=['float64'])(terrain_numbers)

    #Set starting point of fire
    terrain_numbers[0,0] = 5

    # Create grid object
    grid = Grid2D(config, (transition_func, ignition_level, fuel_level))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
