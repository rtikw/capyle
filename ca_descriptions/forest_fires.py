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

terrain_numbers = np.full([50,50], 1)
terrain_numbers[0,0] = 5
terrain_numbers[10:15, 5:15] = 2
terrain_numbers[5:35, 32:35] = 3
terrain_numbers[30:40, 15:25] = 4


def transition_func(grid, neighbourstates, neighbourcounts, fire_types, fire_stages):
	# unpack state counts for burnt
    burnt = neighbourcounts[0]
    burning = neighbourcounts[5]

    #define general ignition rule
    burnable = np.logical_and(grid != 0, grid != 5)
    burnable_terrain = np.logical_and(burnable, grid != 2)
    ignite = np.logical_and(burnable_terrain, burning >= 1)

    #ignition rule for chaparral
    chaparral_ignite = np.logical_and(ignite, grid == 1)
    fire_stages[chaparral_ignite] = 30
    #ignition rule for canyon
    canyon_ignite = np.logical_and(ignite, grid == 3)
    fire_stages[canyon_ignite] = 3
    #ignition rule for forest
    forest_ignite = np.logical_and(ignite, grid == 4)
    fire_stages[forest_ignite] = 180

    #check for burning in fire_stages
    is_burning = fire_stages > 0

    #if it is burning, decrease it by 1
    fire_stages[is_burning] -= 1

    #if fire stage reaches zero, it burns out
    grid[fire_stages == 1] = 0

    #burns if ignite is satisfied
    grid[ignite] = 5

    print(fire_stages[30,33])

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
    config.state_colors = [(0.2,0,0),(0.5,1,0.4),(0.4,0.8,1),(0.8,0.8,0.8),
    (0,0.3,0),(1,0.4,0.4)]

    config.num_generations = 300
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

    fire_types = np.zeros((50,50))
    fire_stages = np.zeros((50,50))
    fire_stages[0,0] = 29
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
