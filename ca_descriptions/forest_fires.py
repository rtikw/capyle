# Name: Conway's game of life
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

terrain_numbers = np.full([10,10], 1)
terrain_numbers[0,0] = 5

terrain_letters = np.array([
        [ ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ' ],
        [ ' ', ' ', ' ', ' ', ' ', ' ', 'c', ' ', ' ', ' ' ],
        [ ' ', 'l', 'l', ' ', ' ', ' ', 'c', ' ', ' ', ' ' ],
        [ ' ', ' ', ' ', ' ', ' ', ' ', 'c', ' ', ' ', ' ' ],
        [ ' ', ' ', ' ', ' ', ' ', ' ', 'c', ' ', ' ', ' ' ],
        [ ' ', ' ', ' ', ' ', ' ', ' ', 'c', ' ', ' ', ' ' ],
        [ ' ', ' ', ' ', 'f', 'f', ' ', 'c', ' ', ' ', ' ' ],
        [ ' ', ' ', ' ', 'f', 'f', ' ', ' ', ' ', ' ', ' ' ],
        [ ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ' ],
        [ ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ' ]
    ])

fuel_dict = {
        ' ' : 3, # chaparral (empty)
        'l' : 0, # lake
        'c' : 3, # canyon
        'f' : 5  # forest
    }
fuel_coef = np.vectorize(fuel_dict.get)(terrain_letters)

ignition_dict = {
        ' ' : 0.2, # chaparral (empty)
        'l' : 0.0, # lake
        'c' : 0.7, # canyon
        'f' : 0.5  # forest
    }
ignition_coef = np.vectorize(ignition_dict.get)(terrain_letters)


def transition_func(grid, neighbourstates, neighbourcounts, fire_types, fire_stages):
	# unpack state counts for burnt and unburnt
    burnt, unburnt = neighbourcounts[0:2]
	# unpack state counts for burning states
    burning = np.sum(neighbourcounts[2:])

    # unpack neighbour state arrays
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    # light new fires
    # ignite = np.full([10,10], False)
    # ignite[grid == 1] = burning * ignition_coef < np.random.rand()
    # ignite = np.logical_and(burning * ignition_coef > np.random.rand(), grid == 1)
    # grid = np.where(ignite, fuel_coef, grid)
    ignite = np.logical_and(grid == 1, burning >= 1)


    grid[grid == 2] = 0 # burn out
    grid[grid > 2] -= 1 # burn down
    grid[ignite] = 5


    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    config.dimensions = 2

    config.title = "Forest Fires (Charlie)"

    # States: burnt, unburn, burning...
    config.states = range(6)
    config.state_colors = [(0,0,0),(0,1,0),(1,0,0),(1,0,0),(1,0,0),(1,0,0)]

    config.num_generations = 50
    config.grid_dims = (10,10)
    config.initial_grid = terrain_numbers
    config.wrap = False

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    fire_types = np.zeros((50,50))
    fire_stages = np.zeros((50,50))
    # Create grid object
    grid = Grid2D(config, (transition_func, fire_types, fire_stages))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
