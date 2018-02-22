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



terrain = np.array([
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
fuel_coef = np.vectorize(fuel_dict.get)(terrain)

ignition_dict = {
        ' ' : 0.2, # chaparral (empty)
        'l' : 0.0, # lake
        'c' : 0.7, # canyon
        'f' : 0.5  # forest
    }
ignition_coef = np.vectorize(ignition_dict.get)(terrain)


def transition_func(grid, neighbourstates, neighbourcounts):
    burnt, unburnt = neighbourcounts[0:2]
    burning = np.sum(neighbourcounts[2:])
    
    # light new fires
    ignite = np.full([10,10], False)
#    ignite[grid == 1] = burning * ignition_coef < np.random.rand()
    ignite = np.logical_and(burning * ignition_coef > np.random.rand(), grid == 1)
    grid = np.where(ignite, fuel_coef, grid)


    grid[grid == 2] = 0 # burn out
    grid[grid > 2] -= 1 # burn down


    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    config.dimensions = 2

    config.title = "Forest Fires (Nick)"

    # States: burnt, unburn, burning...
    config.states = range(6)
    config.state_colors = [(0,0,0),(0,1,0),(1,0,0),(1,0,0),(1,0,0),(1,0,0)]
    
    config.num_generations = 5
    config.grid_dims = (10,10)

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    # Create grid object
    grid = Grid2D(config, transition_func)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
