import arcade
import os
import random
import numpy as np
import math
from .sensor import Sensor




class Robot(arcade.Sprite):
    """ Main Robo class. """
    def __init__(self,
                filename: str = None,
                scale: float = 1,
                image_x: float = 0, image_y: float = 0,
                image_width: float = 0, image_height: float = 0,
                center_x: float = 0, center_y: float = 0,
                repeat_count_x: int = 1, repeat_count_y: int = 1,
                start_angle: int = 0,
                robot_size: int = 40,
                top_speed: int = 2,
                top_speed_turn: int = 3,
                sensor_number: int = 8,
                sensor_image: str = None,
                sensor_image_size: int = 256,
                sensor_length=60,
                sensor_steps: int = 4,
                sensor_arrangement: int = 360,
                id: int = None
                
                ):

        super().__init__(filename=filename,scale=scale,
        image_x=image_x,image_y=image_y,image_width=image_width, image_height=image_height,
        center_x=center_x, center_y=center_y, repeat_count_x=repeat_count_x, repeat_count_y=repeat_count_y)
        
        
        
        self.size = robot_size # in px
        self.angle = start_angle 
        self.top_speed = top_speed # max speed reachable
        self.top_speed_turn = top_speed_turn # max speed while turning reachable
        
        self.id = id   # robot id
        self.battery = 1.  # battery level
        

        # boredom position based
        self.posHist = []
        self.boredom_pos_counter = 0
  
        # boredom turn based
        self.boredom_turn_counter = 0
        self.boredom_turn_punishment_value = 0
        self.lastTurn = 0.5

        # boredom sensor based
        self.lastSensor = np.random.random(sensor_number)
        self.boredom_sensor_counter = 0

        # adaptive battery reduction
        self.risk_zone_counter = 0

        # sensor parameter
        self.sensor_number = sensor_number # number of sensors around the robot
        self.sensor_image = sensor_image # path of image of sensor 
        self.sensor_imgae_size = sensor_image_size # px size of image (for scaling computation)
        self.sensor_length = sensor_length # max length of proximity sensor
        self.sensor_steps = sensor_steps # how precise the sensor is
        self.sensor_list_steps = [] # List for storing all data for each step (Sprite List)
        self.sensor_arrangement=sensor_arrangement # arrangement of sensor around the robot

        # agent proximity computations
        robot_r = self.size/2
        self.check_radius = self.sensor_length - 2 * robot_r
        max_distance = self.sensor_length - 2 * robot_r
        min_distance = 2 * robot_r  # radius of source robot + radius of target robot
        step = float(max_distance-min_distance)/float(self.sensor_steps)
        self.step_limits = np.arange(min_distance,max_distance+step, step)
    
        self._setup_sensor_sprites()

        self.isDead = False

    def _setup_sensor_sprites(self):
        arrengement_sensor_step = self.sensor_arrangement/(self.sensor_number-1) # arrengement for sensor position around the robot
        sensor_length_step = (self.sensor_length-self.size)/self.sensor_steps # step size for sensor precision process
        for sensor_length_step_i in np.arange(sensor_length_step+self.size, self.sensor_length+sensor_length_step, sensor_length_step): # (sensor_length_step, 2*sensor_length_step, 3*sensor_length_step...)
            self.sensor_list_steps.append( arcade.SpriteList() )
            sensor_scaling = (sensor_length_step_i)/self.sensor_imgae_size # scaling of image with specific sensor length
            for start_angle in np.arange(0, -self.sensor_arrangement-arrengement_sensor_step, -arrengement_sensor_step):
                self.sensor_list_steps[-1].append( Sensor(filename=self.sensor_image, 
                                                scale=sensor_scaling, 
                                                center_x=self.center_x,
                                                center_y=self.center_y,
                                                start_angle = start_angle
                                                #color=arcade.make_transparent_color(color=(255,255,255),transparency=0.5) 
                                                ))
        self.sensor_list_steps_transposed = np.array(self.sensor_list_steps).T


    def set_velocity_factor(self, factor):
        """
        # Set positions of robot based on heading and speed factor for next time step update
        Param:
            factor (between 0 and 1) defines velocity value (1 for max speed)
        """
        self.change_x = math.cos(self.radians) * factor * self.top_speed
        self.change_y = math.sin(self.radians) * factor * self.top_speed
        

    def set_turn_factor(self, factor):
        """
        # Setter of robot rotation (1/0 for max turn speed) for next time step update
        Param:
            - factor between 0.5 and 1 -> right rotation (1 max speed)
            - factor between 0 and 0.5 -> left rotation (0 max speed)
            - 0.5: go straight (no turn)
        """
        #self.change_angle = -factor * self.top_speed_turn #
        factor = factor * 2 -1 # maping factor between 1 and -1
        self.angle += -factor * self.top_speed_turn

        # Angle always between 0 and 360 (compass requirement)
        if self.angle > 359:
            self.angle = 0 + self.angle - 359
        elif self.angle < 0:
            self.angle = 360 - self.angle * (-1)

    def get_compass_value(self):
        """
        Coding:
        North = 0.25
        East = 0
        South = 0.75
        West = 0.5
        """
        # angle = 0 -> East
        # angle = 90 -> North
        # angle = 180 -> West
        # angle = 270 -> South
        return self.angle/360

    #def get_binary_proximity_values(self, list_of_sprite_lists):
    #    prox = np.zeros(self.sensor_number)
    #    for test_object_list in list_of_sprite_lists:
    #        for idx, sensor in enumerate(self.sensor_list):
    #            if prox[idx] != 1: # Sensor still 1. Don't waste unnessesary compution power!!
    #                if len(arcade.check_for_collision_with_list(sensor, test_object_list)) > 0:
    #                    prox[idx] = 1
    #    return prox

    def get_step_proximity_values(self, test_objects):
        
        prox = np.zeros(self.sensor_number)
       
        for sensor_idx, sensor_i in enumerate(self.sensor_list_steps_transposed): 

            if self.lastSensor[sensor_idx] < 0.25: # if last sensor detected obstacle far away, than first check long sensor
                for value, sensor_sprite in enumerate(reversed(sensor_i)):  # value 0: longest sensors 
                        collision_true = False
                        if value == 0:  #  for the longest sensors: check all obstacles
                            collisions = arcade.check_for_collision_with_list(sensor_sprite, test_objects)
                            if len(collisions) > 0:
                                collision_true = True
                        else: # check only obstacles that the longest sensors already detected
                            for coll in collisions:
                                if arcade.check_for_collision(sensor_sprite, coll):
                                    collision_true = True
                                    break
                        if collision_true: # if sensors detect something, change sensor value with specific value, based on sensor length
                            prox[sensor_idx] = value+1 # shorter sensor range higher sensor value
            else: # check first short sensor
                for value, sensor_sprite in enumerate(sensor_i):
                    if len(arcade.check_for_collision_with_list(sensor_sprite, test_objects)) > 0:
                        prox[sensor_idx] = self.sensor_steps-value
                        break
                            

        return prox/self.sensor_steps

     
    def reduce_battery(self, decrementation_value, APPROACH_NUMBER, BATTERY_PENALTY ,SCREEN_WIDTH, BATTERY_PENALTY_PER_TS, MIN_BATTERY_REACHED):
        """
            Decrement the battery level with a specific value in each time step.
        """
        if APPROACH_NUMBER == 5 and BATTERY_PENALTY:
            if self.center_x >= SCREEN_WIDTH/2.:  # robot in risk zone
                self.risk_zone_counter += 1
            else:
                self.risk_zone_counter = 0

            self.battery -= (decrementation_value  +  BATTERY_PENALTY_PER_TS * self.risk_zone_counter)  
        else:
            self.battery -= decrementation_value
        if self.battery <= MIN_BATTERY_REACHED:
            self.isDead = True
            self.battery = MIN_BATTERY_REACHED
        elif self.isDead and self.battery > MIN_BATTERY_REACHED:
            self.isDead = False
        


    def chargeBattery(self, battery_charge_per_ts, battery_reduction): 
        """ Calls if Robot collides with light source.
            In each time step increase battery with charge parameter and leave out battery reduction """
        self.battery = min(self.battery + battery_charge_per_ts + battery_reduction, 1.0) 
        

    def get_boredom_pos_punishment(self,boredom_parameter, boredom_pos_time, boredom_pos_radius):
        """ Computes a boredom based on the last positions of robot.
            After *BOREDOM_POS_TIME* the robot should leave a radius of *BOREDOM_POS_RADIUS*.
            Otherwise increase the counter. The higher the counter the higher the boredom punishment.
            The longer the robot changes his position the stronger the punishment will be.
            """
        actualPosValues = [self.center_x, self.center_y]
        if len(self.posHist) == boredom_pos_time: # posHist has enough entries!
            lastIn = self.posHist.pop(0) # remove element from list and compare with actual value
            if abs(lastIn[0]-actualPosValues[0])<=boredom_pos_radius and abs(lastIn[1]-actualPosValues[1])<=boredom_pos_radius: # if change of x and y value <= threshold: inc counter
                self.boredom_pos_counter = min(self.boredom_pos_counter+1, boredom_parameter) # increase counter until it reaches maximum value
            else: # if robot leaves radius set counter to 0 and therefore omit boredom punishment 
                self.boredom_pos_counter = 0
        self.posHist.append(actualPosValues) # add actual position values to history
        return float(self.boredom_pos_counter)/float(boredom_parameter)
        


    def update_boredom_turn_punishment(self, turn_factor, boredom_turn_parameter, boredom_turn_offset):
        """ updates boredom turn parameter in each timestep """
        if (self.lastTurn>0.5 and turn_factor>0.5) or (self.lastTurn<0.5 and turn_factor<0.5): # if change of x and y value <= threshold: inc counter
            self.boredom_turn_counter = min(self.boredom_turn_counter+1, boredom_turn_parameter + boredom_turn_offset) # increase counter until it reaches maximum value
        else: # if robot leaves radius set counter to 0 and therefore omit boredom punishment 
            self.boredom_turn_counter = 0
        self.lastTurn = turn_factor
        self.boredom_turn_punishment_value =  float( max(self.boredom_turn_counter,boredom_turn_offset)-boredom_turn_offset )/float(boredom_turn_parameter)


    def get_boredom_sensor_punishment(self, actualProximitySensors, boredom_sensor_parameter, boredom_sensor_offset):
            """ computes the influence of boredom on the fitness, based on the variance of proximity sensor values """
            if (self.lastSensor==actualProximitySensors).all(): # and not (actualProximitySensors==numpy.zeros(self.amountProxSensors)).all():  
                    self.boredom_sensor_counter = min(self.boredom_sensor_counter+1, boredom_sensor_parameter + boredom_sensor_offset)
            else:
                    self.boredom_sensor_counter = 0 
            
            self.lastSensor = actualProximitySensors
            return float( max(self.boredom_sensor_counter,boredom_sensor_offset)-boredom_sensor_offset )/ float(boredom_sensor_parameter)   # with offset: if boredomCounter >= offset

    #def check_distance_to_sprite(self, target_sprite):
    #    return np.linalg.norm(np.array([self.center_x,self.center_y])-
    #                   np.array([target_sprite.center_x, target_sprite.center_y]))
    

    def check_for_collision_with_other_agents(self, agent_list, in_next_ts=False, get_distance=False):
        """checks collision with other agents

        Args:
            agent_list (Sprite_list): check this list of agent
            in_next_ts (bool, optional): check position in the next timestep. Defaults to False.
            get_distance (bool, optional): return distance values. Defaults to False.

        Returns:
            list: list of agents that collide with self  
        """
        x,y  = self.center_x, self.center_y
        if in_next_ts:
            x += self.change_x * 2
            y += self.change_y * 2
        collisions = []
        distance_all = []
        for agent in agent_list:
            if agent.id is not self.id:
                target_x, target_y = agent.center_x, agent.center_y
                #if in_next_ts:
                #    target_x += agent.change_x  
                #    target_y += agent.change_y
            
                distance = np.linalg.norm(np.array([x,y]) - np.array([target_x, target_y])) - self.size 
                #distance = np.sqrt( abs(target_x-x)**2 + abs(target_y-y)**2 ) - self.size
                if get_distance:
                    distance_all.append(distance_all)
                else:
                    if distance <= 2:
                        collisions.append(agent)
        if get_distance:
            return distance_all
        return collisions

    def get_agents_proxitmity_values(self, agent_list):

        robot_x, robot_y = self.center_x, self.center_y
        robot_angle = self.angle

        prox_values = np.zeros(self.sensor_number)
        sensor_list = self.sensor_list_steps[-1]  # get array of longest sensors 

        for agent_idx, agent in enumerate(agent_list):
            if agent.id != self.id:
                target_x, target_y = agent.center_x , agent.center_y
                distance_to_robot = np.linalg.norm( np.array([robot_x,robot_y]) - np.array([target_x, target_y]) )
                if distance_to_robot > self.check_radius:  # Robot not in range to other robot
                    pass
                else:
                    for sensor_idx, sensor in enumerate(sensor_list):
                        if arcade.check_for_collision(sensor, agent):
                            for i in range(self.sensor_steps):
                                if self.step_limits[i] <= distance_to_robot < self.step_limits[i+1] :
                                    prox_values[sensor_idx] = 1-(i/self.sensor_steps)
                                    break
        return prox_values


    def share_engergy(self, collision_agent_list):
        """Agent shares the energy with all other agents that collide with it

        Args:
            collision_agent_list ([type]): [description]
        """
        
        sum_energy = 0
        sum_energy += self.battery
        for agent in collision_agent_list:
            
            sum_energy += agent.battery
        
        change_bat = float(sum_energy)/(len(collision_agent_list)+1)
        self.battery = change_bat
        for agent in collision_agent_list:
            agent.battery = change_bat
        
