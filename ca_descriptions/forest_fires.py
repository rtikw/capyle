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


def transition_func(grid, neighbourstates, neighbourcounts, fire_types, fire_stages):
	# unpack state counts for burnt
    burnt = neighbourcounts[0]
    burning = neighbourcounts[5]

    #define basic ignition rule
    ignite = np.logical_and(grid == 1, burning >= 1)

    #define fire stage for ignition
    fire_stages[ignite] = 5

    #check for burning in fire_stages
    is_burning = fire_stages > 0

    #if it is burning, decrease it by 1
    fire_stages[is_burning] -= 1

    #if fire stage reaches zero, it burns out
    grid[fire_stages == 1] = 0

    print(fire_stages)

    #burns if ignite is satisfied
    grid[ignite] = 5

    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    config.dimensions = 2

    config.title = "Forest Fires (Charlie)"

    # States:
    # 0: Burnt out, 1: Chaparral, 2: Lake, 3: Canyon, 4: Forest
    # 5: Burning
    config.states = range(6)
    config.state_colors = [(0,0,0),(0,1,0),(0,0,1),(0.3,0,0),(0,0.3,0),
    (1,0,0)]

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

    fire_types = np.zeros((10,10))
    fire_stages = np.zeros((10,10))
    fire_stages[0,0] = 4
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