"""
2D Robot Simulation

"""
# ----- Bugfix for "pyglet.gl.ContextException: Unable to share contexts." Error ----
#from __future__ import absolute_import, division
# Fix pyglet 'shared environment' error
#import pyglet
#pyglet.options['shadow_window']=False
# -----------------------------------------------------------------------------------


import arcade
import numpy as np
import csv
import random
from simulation_objects.lightSource import LightSource
from simulation_objects.robot import Robot
import time
import parameters as p
from log_individual import LogIndividual
import copy



class Simulation(arcade.Window):
    """
    Main application class.
    """


    def __init__(self, title, ud_rate, population, generationNumber):
        self.arena_layout_file_name = p.ARENA_LAYOUT_NAME
        width, height = self.load_arena_layout(p.START_ARENA_LAYOUT_PATH, return_w_h=True)
        
        super().__init__(width, height, title, update_rate = ud_rate, antialiasing=False) #, antialiasing=False

        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.player_list = None
        self.wall_list = None
        self.light_list = None
        self.physics_list = None

        self.generationNumber = generationNumber
        self.population = iter(population)

        self.actual_best_fitness = -1.0
        self.best_results = None
        self.best_action_genome = None
        self.best_prediction_genome = None
        self.best_tracking = None
        self.best_sensors = None
        self.best_annOut = None


        
        
        # self.width = 700
        # self.height = 200

        #self.updateRateSetTo = ud_rate
        #self.set_vsync = False
        #self.set_visible = False
        #self.set_update_rate = p.UPDATE_RATE

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Global variables
        self.forwards = False
        self.backwards = False
        self.left = False
        self.right = False
        self.tmpCount = 0

        # self.time_endTS = time.time()
        # self.wait_betw_ts = []
        # self.get_data = []
        # self.comp_nets = []
        # self.prev_jump = []
        # self.sensor_update = []
        # self.recharge_update = []
        # self.log_data = []
        # self.check_termin = []

        # Create your sprites and sprite lists here
        self.agent_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.light_list = arcade.SpriteList(use_spatial_hash=True)
        self.physics_list = []
        # read arena layout from csv file
        self.arena_layout_file_name = p.ARENA_LAYOUT_NAME
        self.load_arena_layout(p.START_ARENA_LAYOUT_PATH)
        
    

        self.ts_for_change_layout = np.arange(0,p.MAX_TIME_STEPS_REACHED, p.MAX_TIME_STEPS_REACHED/len(p.ARENA_LAYOUT_NAMES))
        self.new_layout_names_generator = iter(p.ARENA_LAYOUT_NAMES)

        self.timestep = 0

        # init arrays to store/log data
        self.track_log_array = []
        self.sensor_log_array = []
        self.annOut_log_array = []
        self.time_spent_in_light_source = 0

        #self.set_update_rate(self.updateRateSetTo)
        try:
            self.indivi = next(self.population)
            self.indivi.reset()
        except StopIteration:
            self.end_of_simulation()
            #print("Whole population is evaluated!")
            self.close()
        
        x_position_of_agents = []
        y_position_of_agents = []
        agent_scaling = p.OBJECT_SIZE_AGENT/p.OBJECT_IS_SIZE
        for i in range(p.NUMBER_ROBOTS):
        
            rand_x_center = min( max(p.OBJECT_SIZE_BOX*5,np.random.randint(self.width/2)), self.width/2-p.OBJECT_SIZE_BOX*5)
            rand_y_center = min( max(p.OBJECT_SIZE_BOX*5,np.random.randint(self.height)), self.height-p.OBJECT_SIZE_BOX*7)
            self.agent_list.append(Robot(filename=p.IMAGE_AGENT, 
                                                scale=agent_scaling,
                                                center_x=rand_x_center,
                                                center_y=rand_y_center,
                                                start_angle=random.randint(0,360),
                                                robot_size=p.OBJECT_SIZE_AGENT,
                                                top_speed=p.TOP_SPEED,
                                                top_speed_turn=p.TOP_SPEED_TURN,
                                                sensor_number=p.SENSOR_NUMBER,
                                                sensor_image=p.IMAGE_SENSOR,
                                                sensor_image_size=p.OBJECT_IS_SIZE_SENSOR,
                                                sensor_length=p.SENSOR_LENGTH,
                                                sensor_steps=p.SENSOR_STEPS,
                                                sensor_arrangement=p.SENSOR_ARRANGEMENT,
                                                id=i       
                                                ))
            while(True):
                if len( self.agent_list[-1].check_for_collision_with_other_agents(self.agent_list) ) > 0 :
                    rand_x_center = min( max(p.OBJECT_SIZE_BOX*4,np.random.randint(self.width/2)), self.width/2-p.OBJECT_SIZE_BOX*1)
                    rand_y_center = min( max(p.OBJECT_SIZE_BOX*5,np.random.randint(self.height)), self.height-p.OBJECT_SIZE_BOX*5)
                    self.agent_list[-1].center_x, self.agent_list[-1].center_y  = rand_x_center, rand_y_center
                else:
                    break
        self.setup_arena_objects()
        # defines the pysics engine (for collision avoidance)
        #self.setup_collision_physics()
        
        
    def on_draw(self):
        """
        Renders the screen.
        """
        if p.DRAW_SIMULATION:
            arcade.start_render()  # This command should happen before we start drawing. It will clear the screen to the background color, and erase what we drew last frame.
            self.light_list.draw()
            for agent in self.agent_list:
                #for sensor_list in agent.sensor_list_steps:
                agent.sensor_list_steps[-1].draw()
                    #sensor_list.draw()
            self.wall_list.draw()
            self.agent_list.draw()
        else:
            pass
        

    def on_update(self, delta_time:float):
        """
        All the logic to move goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        # time_begin=time.time()
        # self.wait_betw_ts.append(time_begin-self.time_endTS)

        ########## CHECK FOR NEW ARENA LAYOUT ############
        if p.DYNAMIC_ENVIRONMENT:
            if self.timestep in self.ts_for_change_layout:
                
                self.arena_layout_file_name = next(self.new_layout_names_generator)
                new_layout_path = p.ARENA_LAYOUT_FOLDER + self.arena_layout_file_name
                self.load_arena_layout(new_layout_path)
                self.setup_arena_objects()

        self.timestep += 1
        ########### GET SENSOR VALUES SECTION #############
        proxSensors_of_robots = []
        addiSensors_of_robots = []
        for agent in self.agent_list:
            if p.NUMBER_ROBOTS > 1:
                prox_wall_sensors = agent.get_step_proximity_values(self.wall_list)
                prox_agent_sensors = agent.get_agents_proxitmity_values(self.agent_list)
                proxSensors_of_robots.append(np.maximum(prox_wall_sensors,prox_agent_sensors))
            else:
                proxSensors_of_robots.append( agent.get_step_proximity_values(self.wall_list) )

            addiSensors_of_robots.append([])
            if p.CHECK_LIGHT_SENSOR:
                if len(self.light_list)>0:
                    addiSensors_of_robots[-1].append( self.light_list[0].get_light_intensity_for_sprite(agent) )
                else:
                    addiSensors_of_robots[-1].append(0.0)
            if p.CHECK_COMPASS:
                addiSensors_of_robots[-1].append( agent.get_compass_value() )
            if p.CHECK_BATTERY:
                addiSensors_of_robots[-1].append( agent.battery )

        # time_get_all_data=time.time()
        # self.get_data.append(time_get_all_data-time_begin)

        #print("{0:15} {0:15}".format(round(addiSensors_of_robots[0][2],2), round(addiSensors_of_robots[1][2],2) ))
        #print(addiSensors_of_robots)
        
        ########### LOGIC SECTION #############################
        # Here:
            # Call *processSensorValues* of individuum with sensor data as parameter
            # Return speed and heading (of action network) and prediction values for logging

        # pass all sensors for each agent and get action and prediction of networks
        all_actions_of_robots = []
        all_predictions_of_robots = []
        
        for agent_idx, agent in enumerate(self.agent_list):
            # boredom_punishment = []
            # if p.BOREDOM_SENSOR:
            #     boredom_punishment.append(  agent.get_boredom_sensor_punishment(proxSensors_of_robots[agent_idx], p.BOREDOM_SENSOR_PARAMETER, p.BOREDOM_SENSOR_OFFSET)  )
            # if p.BOREDOM_POS:
            #     boredom_punishment.append(  agent.get_boredom_pos_punishment(p.BOREDOM_POS_PARAMETER, p.BOREDOM_POS_TIME, p.BOREDOM_POS_RADIUS)  )
            # if p.BOREDOM_TURN:
            #     boredom_punishment.append(  agent.boredom_turn_punishment_value  )
            # if not (p.BOREDOM_TURN or p.BOREDOM_POS or p.BOREDOM_SENSOR):
            #     boredom_punishment.append(0.0)
            if agent.isDead:
                boredom_value = 1.0
            else:
                boredom_value = 0.0
                if p.BOREDOM_SENSOR:
                    boredom_value = agent.get_boredom_sensor_punishment(proxSensors_of_robots[agent_idx], p.BOREDOM_SENSOR_PARAMETER, p.BOREDOM_SENSOR_OFFSET)
                if p.BOREDOM_TURN:
                    boredom_turn_value = agent.boredom_turn_punishment_value
                    boredom_value = max(boredom_value,boredom_turn_value)
                if p.BOREDOM_POS:
                    boredom_pos_value =   agent.get_boredom_pos_punishment(p.BOREDOM_POS_PARAMETER, p.BOREDOM_POS_TIME, p.BOREDOM_POS_RADIUS)  
                    boredom_value = max(boredom_value,boredom_pos_value)

            action, prediction = self.indivi.processSensorValues(proxSensors_of_robots[agent_idx], addiSensors_of_robots[agent_idx], boredom_value, agent_idx)#, agent.boredom_turn_punishment_value, boredom_pos_punishment)
            if p.BOREDOM_TURN:
                agent.update_boredom_turn_punishment(action[1], p.BOREDOM_TURN_PARAMETER, p.BOREDOM_TURN_OFFSET)
            #pass actions to robot sprites
            if not p.Test_Controller and not agent.isDead:
                agent.set_velocity_factor(action[0])
                agent.set_turn_factor(action[1])
                all_actions_of_robots.append(action)
                all_predictions_of_robots.append(prediction)
            elif agent.isDead:
                agent.set_velocity_factor(0)
                agent.set_turn_factor(0.5)
                all_actions_of_robots.append(np.array([-1]*len(action)))
                all_predictions_of_robots.append(np.array([-1]*len(prediction)))
            if p.Test_Controller:
                all_actions_of_robots.append(action)
                all_predictions_of_robots.append(prediction)
            #print(action,"\n")
            #print(prediction)
            

        # time_network=time.time()
        # self.comp_nets.append(time_network-time_get_all_data)

    # -------This is only for testing ---------------------
        # Velocity
        if p.Test_Controller:
            if self.forwards:
                self.agent_list[0].set_velocity_factor(1)
            elif self.backwards:
                self.agent_list[0].set_velocity_factor(-1)
            else:
                self.agent_list[0].set_velocity_factor(0)

            
            # Heading
            if self.right:
                self.agent_list[0].set_turn_factor(1)
                agent.update_boredom_turn_punishment(1, p.BOREDOM_TURN_PARAMETER, p.BOREDOM_TURN_OFFSET)
            elif self.left:
                self.agent_list[0].set_turn_factor(0)
                agent.update_boredom_turn_punishment(0, p.BOREDOM_TURN_PARAMETER, p.BOREDOM_TURN_OFFSET)
            else:
                self.agent_list[0].set_turn_factor(0.5)
                agent.update_boredom_turn_punishment(0.5, p.BOREDOM_TURN_PARAMETER, p.BOREDOM_TURN_OFFSET)

            # if not self.agent_list[1].isDead:
            #     self.agent_list[1].set_turn_factor(0.9)
            #     self.agent_list[1].set_velocity_factor(0.2)
            # else:
            #     self.agent_list[1].set_turn_factor(0.5)
            #     self.agent_list[1].set_velocity_factor(0)
    # -------------------------------------------------------
        ############# SIMULATION UPDATE SECTION ######################
        

        self.update_physics()
        
    

        # time_rausspringen=time.time()
        # self.prev_jump.append(time_rausspringen-time_network)
    
        # Update Sensor Position and Angle for each agent
        for agent in self.agent_list:
            for sensor_list in agent.sensor_list_steps:
                for sensor in sensor_list:    
                    sensor.follow_robot(agent)
                    sensor_list.update()

        # time_update_sensorposition=time.time()
        # self.sensor_update.append(time_update_sensorposition-time_rausspringen)

        # Update Battery of each Robot
        for agent in self.agent_list:
            if len(self.light_list)>0:
                agent.reduce_battery(p.BATTERY_REDUCTION, p.APPROACH_NUMBER,p.BATTERY_PENALTY, self.width, p.BATTERY_PENALTY_PER_TS, p.MIN_BATTERY_REACHED)
 
        
        # Check for light source collision and recharge if True
        for agent in self.agent_list:
            if len( arcade.check_for_collision_with_list(agent, self.light_list) ) > 0:  #and agent.battery <= p.THRESHOLD_BATTERY_RECHARGE:  
                self.time_spent_in_light_source += 1     
                agent.chargeBattery(p.BATTERY_CHARGE_PER_TS, p.BATTERY_REDUCTION)
                
        # time_recharge_stuff=time.time()
        # self.recharge_update.append(time_recharge_stuff-time_update_sensorposition)        
        
        
        
        ############ STORE DATA SECTION ##############################
   
        track_all_agents = []
        sensor_all_agents = []
        annOut_all_agents = []
        for agent_idx, agent in enumerate(self.agent_list):
            track_all_agents.extend([agent.angle,agent.center_x,agent.center_y,agent.battery])
            sensor_all_agents.extend(np.concatenate((proxSensors_of_robots[agent_idx], addiSensors_of_robots[agent_idx]), 0))
            annOut_all_agents.extend(  np.concatenate( (all_actions_of_robots[agent_idx], all_predictions_of_robots[agent_idx]),0 )  )
        track_all_agents.extend([self.arena_layout_file_name])
        self.track_log_array.append(track_all_agents)
        self.sensor_log_array.append(sensor_all_agents)
        self.annOut_log_array.append(annOut_all_agents)
        

        ## FOR DEBUGING ################
        #every_sec = 0.5
        #if self.timestep % int(p.UPDATE_RATE**(-1)*every_sec) == 0: 
        #    print(proxSensors_of_robots)
        #    print(addiSensors_of_robots)

        # time_log_data=time.time()
        # self.log_data.append(time_log_data-time_recharge_stuff)     


        #### CHECK FOR TERMINATION ##########################
        if self.timestep >= p.MAX_TIME_STEPS_REACHED:
            self.termination_of_run()


        # if not all agents are dead (no battery) than do not terminate!
        termination = True
        for agent in self.agent_list:
            if not agent.isDead:
                termination = False

            if p.APPROACH_NUMBER == 5 and p.TERMINATION_IN_RISK:
                if (not agent.isDead) and agent.center_x >= self.width/2. and np.random.random() < p.TERMINATION_PROB_IN_RISK:  # robot in risk zone and termination probability true
                    agent.battery = 0.0 
                     
        if termination:    
            self.termination_of_run()
        
             

        

        # time_check_for_termination=time.time()
        # self.check_termin.append(time_check_for_termination-time_log_data)   
        # self.time_endTS = time.time()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            #self.agent_list[0].forward(MOVEMENT_SPEED)
            self.forwards = True
            self.backwards = False
        elif key == arcade.key.DOWN:
            #self.agent_list[0].forward(-MOVEMENT_SPEED)
            self.forwards = False
            self.backwards = True
        if key == arcade.key.LEFT:
            self.left = True
            self.right = False
            #self.agent_list[0].set_turn_factor(-1)
        elif key == arcade.key.RIGHT:
            self.right = True
            self.left = False
            #self.agent_list[0].set_turn_factor(1)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.UP or key == arcade.key.DOWN:
           # self.agent_list[0].change_y = 0
            self.forwards = False
            self.backwards = False
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            #self.agent_list[0].set_turn_factor(0)
            self.right = False
            self.left = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass
    

    def load_arena_layout(self, arena_layout_path, return_w_h=False):
        """
            reads arena layout based on given path (csv file) and stores it in array (*self.arena_layout*)
        """
        with open(arena_layout_path+".csv", 'r') as f:
            data = csv.reader(f)
            data_lst = []
            for line in data:
                for l in line:
                    data_lst.append(str(l).split("\t"))
            data_lst = np.array(data_lst)
            data_lst[data_lst==''] = 0                
        self.arena_layout = np.array(data_lst, dtype=np.int8)
        if not return_w_h:
            self.width = (self.arena_layout.shape[1]+2) * p.OBJECT_SIZE_BOX
            self.height = (self.arena_layout.shape[0]+2) * p.OBJECT_SIZE_BOX
        else:
            return (self.arena_layout.shape[1]+2) * p.OBJECT_SIZE_BOX, (self.arena_layout.shape[0]+2) * p.OBJECT_SIZE_BOX

    def setup_arena_objects(self):
            self.wall_list = arcade.SpriteList(use_spatial_hash=True)
            self.light_list = arcade.SpriteList(use_spatial_hash=True)

            # Set start position of all objects related by arena layout
            # Box size defines interval of grid (arena layout)
            
            box_scaling = p.OBJECT_SIZE_BOX/p.OBJECT_IS_SIZE_BOX
            light_scaling = p.OBJECT_SIZE_LIGHT/p.OBJECT_IS_SIZE_LIGHT
            
            for y, line in enumerate(self.arena_layout):
                for x, value in enumerate(line):
                    # define center of object to be placed in grid
                    center_x = (x+1)*p.OBJECT_SIZE_BOX  + p.OBJECT_SIZE_BOX/2
                    center_y = (len(self.arena_layout)-y)*p.OBJECT_SIZE_BOX + p.OBJECT_SIZE_BOX/2
                    if value == 1:
                        wall = arcade.Sprite(p.IMAGE_BOX, box_scaling)
                        wall.center_x = center_x
                        wall.center_y = center_y
                        self.wall_list.append(wall)
                    elif value == 2: # position of light source
                        self.light_list.append(LightSource(filename=p.IMAGE_LIGHT, 
                                                    scale=light_scaling,
                                                    center_x=center_x,
                                                    center_y=center_y,
                                                    screen_width= self.width,
                                                    screen_height= self.height
                                                    ))
                    
            self.setup_collision_physics()
            
    def setup_collision_physics(self):
        self.physics_list = []
        for idx, agent in enumerate(self.agent_list):
            collision_list = arcade.SpriteList()
            #for idx_2, agent_2 in enumerate(self.agent_list):
                #if idx != idx_2:
                #    collision_list.append(agent_2)
            collision_list.extend(self.wall_list)     
            self.physics_list.append( arcade.PhysicsEngineSimple(agent, collision_list) )
                

    
    def update_physics(self):
        for idx, agent in enumerate(self.agent_list):
            #print(agent.check_for_collision_with_other_agents(self.agent_list))
            #while(True): # physics and prevent robot jumps out of the arena (occurs very raly)
            if not agent.isDead:
                before_center = (agent.center_x, agent.center_y)
                #if len(arcade.check_for_collision_with_list(agent, self.agent_list)) > 0:
                if p.NUMBER_ROBOTS > 1: 
                    collision_agent_list = agent.check_for_collision_with_other_agents(self.agent_list, in_next_ts = True)
                    if len(collision_agent_list)>0:
                        agent.change_x = 0
                        agent.change_y = 0
                        if p.NUMBER_ROBOTS > 1 and p.SHARE_ENERGY:
                            agent.share_engergy(collision_agent_list)

                self.physics_list[idx].update()  # update only for that agent
            
                after_center = (agent.center_x, agent.center_y)
                if abs(before_center[0]-after_center[0])<=5 and abs(before_center[1]-after_center[1]<=5):
                    #break
                    pass
                else:
                    if agent.angle <= 90 and agent.angle >= 270:
                        agent.center_x = before_center[0] + 1
                        agent.center_y = before_center[1] + 1
                    else:
                        agent.center_x = before_center[0] - 1
                        agent.center_y = before_center[1] - 1
            
        #self.physics_list[0].update()
        #for physic in self.physics_list:
         #   physic.update()
        
    
    def termination_of_run(self):
        """
            Called when termination criteria are reached.
             - Store Results (Final Fitness, Number of Time steps, Number of recharges of battery)
             - End Simulation
             - Go further in evolution
        """

        # time_begin_termi=time.time()
         

        self.indivi.evaluate() # compute fitness value
        if self.indivi.fitnessValue >= self.actual_best_fitness:
            self.actual_best_fitness = self.indivi.fitnessValue
            # Store results
            result_charges = round(float(self.time_spent_in_light_source)/float(p.NUMBER_ROBOTS),2)
 
            self.best_results = [ self.indivi.fitnessValue, self.timestep, result_charges ] 
            if p.NUMBER_ROBOTS == 1:
                self.best_action_genome =  self.indivi.actionNetwork.toGenome() 
                self.best_prediction_genome =  self.indivi.predictionNetwork.toGenome()  
            else:
                self.best_action_genome =  self.indivi.swarm_members[0].actionNetwork.toGenome() 
                self.best_prediction_genome =  self.indivi.swarm_members[0].predictionNetwork.toGenome() 
            self.best_tracking =  self.track_log_array 
            self.best_sensors =  self.sensor_log_array 
            self.best_annOut =  self.annOut_log_array 

        # time_end_termi=time.time()
        # time_end_termi_end = time_end_termi - time_begin_termi

        print(f"Run Done! Indivi Nr. {self.indivi.id} achieved a fitness of {self.indivi.fitnessValue}!")

        


        
        # ------------------------------------- RECORD TIME SECTION -----------------------
        # a = np.average(self.wait_betw_ts) * 10000
        # b = np.average(self.get_data) * 10000
        # c =np.average(self.comp_nets) * 10000
        # d =np.average(self.prev_jump) * 10000
        # e =np.average(self.sensor_update) * 10000
        # f =np.average(self.recharge_update) * 10000
        # g =np.average(self.log_data) * 10000
        # h =np.average(self.check_termin) * 10000
        # time_end_termi_end = (time_end_termi_end * 10000) 
        
        # print(f"wait_betw_ts: {a}")
        # print(f"get_data: {b}")
        # print(f"comp_nets: {c}")
        # print(f"prev_jump: {d}")
        # print(f"sensor_update: {e}")
        # print(f"recharge_update: {f}")
        # print(f"log_data: {g}")
        # print(f"check_termin: {h}")
        # print(f"termination_process: {time_end_termi_end}")
        # print(f"sum: {b+c+d+e+f+g+h+time_end_termi_end/2000}")
        # print("\n")
        # -----------------------------------------------------------------------------


        # restart Simulation with next individual
        self.setup()
        
        
    def end_of_simulation(self):
        """ All runs are evaluated. Now store/log data of best individual in kings folder!! """

        
        np.set_printoptions(suppress=True)

        # Store in Kings folder
        log = LogIndividual(self.generationNumber)
        
        # # Store results
        result_string = np.array2string(np.array(self.best_results), separator=',' )[1:-1].replace(' ','')
        result_string = result_string.replace('\n','') 
        log.storeResults(result_string, new=False, close=True)

        # Store genome
        log.storeActionGenome( self.best_action_genome )
        log.storePredictionGenome( self.best_prediction_genome )


        # Store tracking, sensors and ann outputs
        for i in range(len(self.best_tracking)):
            all_tracking = np.array2string(  np.array(self.best_tracking[i])    , separator=',' )[1:-1].replace(' ','')
            all_tracking = all_tracking.replace('\n','')
            all_tracking = all_tracking.replace('\'','')
            if i>=len(self.best_tracking)-1:
                log.tracking(all_tracking, new=False, close=True)
            else:
                log.tracking(all_tracking, new=False, close=False)

        for i in range(len(self.best_sensors)):
            all_sensors = np.array2string( np.array(self.best_sensors[i])     , separator=',' )[1:-1].replace(' ','')
            all_sensors = all_sensors.replace('\n','') 
            if i>=len(self.best_sensors)-1:
                log.storeSensorData(all_sensors, new=False, close=True)
            else:
                log.storeSensorData(all_sensors, new=False, close=False)
            

        for i in range(len(self.best_annOut)):
            all_annOutput = np.array2string(  np.array(self.best_annOut[i])  , separator=',' )[1:-1].replace(' ','')
            all_annOutput = all_annOutput.replace('\n','')
            if i>=len(self.best_annOut)-1:
                log.storeAnnOut(all_annOutput, new=False, close=True)
            else:
                log.storeAnnOut(all_annOutput, new=False, close=False)
            
        
        



"""
def main():
    from genetic_population import GeneticPopulation
    simulation = Simulation(self.width, self.height, p.SCREEN_TITLE, p.UPDATE_RATE, GeneticPopulation())
    simulation.setup()
    arcade.run()

    simulation = Simulation(self.width, self.height, p.SCREEN_TITLE, p.UPDATE_RATE, GeneticPopulation())
    simulation.setup()
    arcade.run()
       

if __name__ == "__main__":
    main()
"""
        
