# Name: Forest Fire Simulation
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
import math

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

#Test conditions
grid_axis = 100

power_plant = False
incinerator = True

drop_water = False
extend_forest = False
#Forest coordinates (x1,y1,x2,y2)
forest_coor = (5,20,15,30)

#Terrain placements
offset = 25

terrain_numbers = np.full([grid_axis,grid_axis], 1)
terrain_numbers[10+offset:15+offset, 5+offset:15+offset] = 2
terrain_numbers[5+offset:35+offset, 32+offset:35+offset] = 3
terrain_numbers[30+offset:40+offset, 15+offset:25+offset] = 4
# Add the town
terrain_numbers[50+offset, 0+offset] = 3

if extend_forest:
    (ef_x1,ef_y1,ef_x2,ef_y2) = forest_coor
    terrain_numbers[ef_y1:ef_y2,ef_x1:ef_x2] = 4

#Fuel resource level for each terrain type i.e. chaparral burns for 48 steps (4 days)
terrain_fuel_level = {1:48,2:0,3:10,4:252}
#Ignition threshold needed to start fire for each terrain type
terrain_ignition_threshold = {1:10,2:np.inf,3:1,4:100}

#neighbourstate indexes in clockwiwe order (rather than from left to right)
neighbour_clockwise = [0,1,2,4,7,6,5,3]


def get_transition_func(wind_x, wind_y):

    # Wind
    wind_speed = math.sqrt( (wind_x ** 2) + (wind_y ** 2) )
    # Get angle from y-axis
    try: wind_angle = - np.arctan2(wind_y, wind_x) + (0.5 * math.pi)
    except ZeroDivisionError: wind_angle = 0
    print("Wind: (" + str(wind_x)+", "+str(wind_y) + ")"
            + "\n -> speed: " + str(wind_speed)
            + "\n -> angle: " + str(wind_angle / math.pi) + "pi")
    def wind_strength_fn(angle):
        return wind_speed * math.cos(wind_angle - math.radians(angle))
    # wind strength to match "neighbourstates" - in directions NE,N,NW,E,W,SE,S,SW
    wind_strengths = [wind_strength_fn(a + 180) for a in [-45,0,45,-90,90,-135,180,135]]


    def transition_func(grid, neighbourstates, neighbourcounts, ignition_level, fuel_level, water_drops, timestep):
        #Each step is 2 hours
        if drop_water:
            for water_drop in water_drops:
                #Extract drop location coordinates and time
                (dr_x1,dr_y1,dr_x2,dr_y2), drop_start, drop_end  = water_drop
                if timestep[0] >= drop_start and timestep[0] < drop_end:
                    grid[dr_y1:dr_y2,dr_x1:dr_x2] = 2
                    ignition_level[dr_y1:dr_y2, dr_x1:dr_x2] = np.inf

                if (timestep[0] == drop_end):
                    grid[dr_y1:dr_y2, dr_x1:dr_x2] = terrain_numbers[dr_y1:dr_y2, dr_x1:dr_x2]
                    ignition_level[dr_y1:dr_y2, dr_x1:dr_x2] = np.vectorize(terrain_ignition_threshold.get,
                        otypes=['float64'])(terrain_numbers[dr_y1:dr_y2, dr_x1:dr_x2])

        # Which cells will catch fire during this time step
        ignition_incr = np.zeros((grid_axis,grid_axis))
        # burning adjacent cells
        side_burn = np.zeros((grid_axis,grid_axis))
        for i in range(1,8,2):
            side_burn[neighbourstates[neighbour_clockwise[i]] == 5] += 1
        ignition_incr += side_burn
        # burning cells at the corners
        corner_burn = np.zeros((grid_axis,grid_axis))
        for i in range(0,7,2):
            corner_burn[neighbourstates[neighbour_clockwise[i]] == 5] += 1
        ignition_incr += corner_burn * 0.5
        # wind burning effect
        for i in range(0,8):
            ignition_incr[neighbourstates[i] == 5] += wind_strengths[i]

        #Calculate ignition values for unburnt cells
        ignition_level -= ignition_incr
        #If ignition threshold is reached, ignite cell
        ignite = (ignition_level <= 0) & (grid != 5) & (grid != 0)

        burning = (grid == 5)
        #Decrease fuel level of burning states
        fuel_level[burning] -= 1 + (wind_speed*0.5)
        #If fuel level reaches zero, it burns out
        grid[(fuel_level <= 0) & (burning)] = 0
        #burns if ignite is satisfied
        grid[ignite] = 5

        timestep[0] += 1

        #todo
        #Fine-tune ignition thresholds and the effect of the number of neighbours on the ignition value X
        #Implement corner neighbours having less effect on ignition values X
        #Implement wind affecting ignition values X
        #Implement wind strength? X
        #Implement regrowth of terrain?
        #Implement gradient affecting ignition values?
        #Implement short and long-term interventions X


        # If the town has caught fire, print the time-step
        if (grid[50+offset, 0+offset] == 5):
            print("Town on fire: " + str(timestep))

        return grid
    return transition_func


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

    config.num_generations = 1000
    config.grid_dims = (grid_axis,grid_axis)
    config.initial_grid = terrain_numbers
    config.wrap = False

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():

    # NOTE: set the wind here if doing it programatically
    # Default: light prevaling wind southward
    wind_x = 0.0
    wind_y = -0.2
    # if passed extra command-line args, assumed it's for custom wind
    if (len(sys.argv) == 4):
        wind_x = float(sys.argv[2])
        wind_y = float(sys.argv[3])


    # Open the config object
    config = setup(sys.argv[1:])

    ignition_level = np.zeros((grid_axis,grid_axis))
    fuel_level = np.zeros((grid_axis,grid_axis))

    #Set fuel resource for each cell based on terrain
    fuel_level = np.vectorize(terrain_fuel_level.get,otypes=['float64'])(terrain_numbers)

    #Set ignition Threshold for each cell based on terrain
    ignition_level = np.vectorize(terrain_ignition_threshold.get,
        otypes=['float64'])(terrain_numbers)

    #Set starting point of fire
    if power_plant: terrain_numbers[0+offset,0+offset] = 5
    if incinerator: terrain_numbers [0+offset,49+offset] = 5

    #Setup water water drop params ((x1,y1,x2,y2), start_timestep, end_timestep)
    water_drops = [((5+offset,0+offset,15+offset,8+offset),97, 107),((20+offset,10+offset,25+offset,20+offset),230, 240)]
    timestep = np.array([0])

    # Create grid object
    grid = Grid2D(config, (get_transition_func(wind_x, wind_y), ignition_level, fuel_level, water_drops, timestep))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
