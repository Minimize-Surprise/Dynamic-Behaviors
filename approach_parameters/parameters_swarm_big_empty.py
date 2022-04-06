import time

###### SIMULATION ##################################
# x/y size in simulation (shouldn't be higher than OBJECT_IS_SIZE)

OBJECT_SIZE_BOX: int = 35 
OBJECT_SIZE_AGENT: int = 40
OBJECT_SIZE_LIGHT: int = 70 

# x/y number of pixels of original image
OBJECT_IS_SIZE:int  = 128   
OBJECT_IS_SIZE_BOX:int = 128 
OBJECT_IS_SIZE_LIGHT:int = 100 #128

#ARENA_LAYOUT_FOLDER:str = "simulation_objects/arena_layouts/"
#ARENA_LAYOUT_NAME:str = "arena_layout2"
ARENA_LAYOUT_FOLDER:str = "simulation_objects/big_arena/"
ARENA_LAYOUT_NAME:str = "arena_layout1_big_empty"

ARENA_LAYOUT_NAMES = ["arena_layout2", "arena_layout3", "arena_layout4", "arena_layout5", "arena_layout6"]
START_ARENA_LAYOUT_PATH:str = ARENA_LAYOUT_FOLDER + ARENA_LAYOUT_NAME

image_folder:str = "images/"
IMAGE_BOX:str = image_folder + "boxCrate_double.png"
IMAGE_LIGHT:str = image_folder + "sun.png"
IMAGE_AGENT:str = image_folder + "robo_01.png"

IMAGE_SENSOR:str = image_folder + "strich_256t.png"
OBJECT_IS_SIZE_SENSOR:int = 256

Test_Controller = False # ----------------------
DRAW_SIMULATION:bool = True # ------------------
UPDATE_RATE:float = 1./100  # ------------------
REAL_FPS:float = 60.

SCREEN_WIDTH:int = 1200 #1200 
SCREEN_HEIGHT:int = 600 #600 
SCREEN_TITLE:str = "Robot Simulation Master Thesis"

# Robot
NUMBER_ROBOTS = 5   # ----------------------
TOP_SPEED:int = 4
TOP_SPEED_TURN:int = 3
# Proximity sensors
SENSOR_NUMBER:int = 5  # number proximity sensors
SENSOR_LENGTH:int = 125
SENSOR_STEPS:int = 4   # defines the intensity of sensors 4 means: possible values: 0.0 0.25, 0.5, 0.75, 1.0
SENSOR_ARRANGEMENT:int = 180

# Additinal Sensors
CHECK_COMPASS:bool = True
CHECK_LIGHT_SENSOR:bool = True
CHECK_BATTERY:bool = True
NUMBER_OF_ADDITIONAL_SENSORS:int = 3 # compass, light intensity, battery level

###### EVOLUTION #############################
timestr = time.strftime("%Y%m%d-%H%M%S")
timestr = "___________Test________"  #---------------------------
APPROACH_NAME:str = "approach1-1"  # <-----------
APPROACH_NUMBER:int = int(APPROACH_NAME[8])
COMMENT:str = "_mutate04_dynEnvi"
COMMENT:str = "_TEST_" # ------------------------

ADAPT_FITNESS_FUNCTION:bool = False    # set True to test approach 2  # ---------------------
if APPROACH_NUMBER ==2:
    ADAPT_FITNESS_FUNCTION:bool = True 
QUADRATIC_FUNCTION:bool = False

SHARE_ENERGY = False

BOREDOM_SENSOR: bool = True
BOREDOM_TURN: bool = False
BOREDOM_POS: bool = False

BOREDOM_SENSOR_PARAMETER = 200
BOREDOM_SENSOR_OFFSET = 150

BOREDOM_TURN_PARAMETER = 200
BOREDOM_TURN_OFFSET = 50

BOREDOM_POS_PARAMETER = 400
# After *BOREDOM_POS_TIME* the robot should leave a radius of *BOREDOM_POS_RADIUS*   50 -> 130
BOREDOM_POS_TIME = 100  # defines the range of positions in past, that will be compared  
BOREDOM_POS_RADIUS = 100 # defines the radius in that the robot have to leave

BATTERY_CHARGE_PER_TS:float = 0.01 # 0.01
BATTERY_TS_LENGTH:int = 2000 # 0.0005
BATTERY_REDUCTION:float = float(1./BATTERY_TS_LENGTH) #0.0008 #0.003 #0.0008 # 0.001 
BATTERY_PENALTY_PER_TS:float = BATTERY_REDUCTION/1500.    #---------------------- approach5

#Population
POPULATION_SIZE = 50 #50 <------------------------------
MUTATION_RATE = 0.4  # Propability that it will be mutated
MUTATION_CHANGE = 0.4  # intervall of weights mutation (+-) if *MUTATION_RATE* true
RECOMBINATION_PROBABILITY = 0.0 # 0.0 #0.2
# Networks

AMOUNT_HIDDEN_ACTION = 7 
AMOUNT_HIDDEN_PREDICTION = 8 
NUMBER_ACTIONS:int = 2   # output actions
AMOUNT_OUTPUT_PREDICTION = SENSOR_NUMBER + 1 # + 1 lightsensor 
ACTIVATION_FUNCTION_ACTION = "sigmoid" # tanh, sigmoid
ACTIVATION_FUNCTION_PREDICTION = "sigmoid" # tanh, sigmoid

# Evo Termination
TERMINATION_PARA_FITNESS = 0.99 #TODO
MAX_GENERATION_REACHED = 150 #150  <---------------------

# Run termination
MAX_TIME_STEPS_REACHED = 3000 # 3000  <------------------------------
MIN_BATTERY_REACHED = 0 # end run if battery level reaches this threshold


EVOLUTION_PATH = "logs/"+APPROACH_NAME+"_evo"+timestr+COMMENT+"/"
