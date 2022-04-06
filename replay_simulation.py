"""
2D Robot Replay

"""
import arcade
import numpy as np
import csv
import random
from simulation_objects.lightSource import LightSource
from simulation_objects.robot import Robot
import time
import tkinter as tk
from tkinter import filedialog
import sys
import csv
import os
from pathlib import Path
from post_evaluation.plotFitness import PlotFitness



# ---- Import Parameters of replay folder --------
root = tk.Tk()
root.withdraw()

filePath = filedialog.askopenfilename()
trackPath = filePath
absoluteProjectPath = filePath[:filePath.find("/kings/")]



sys.path.insert(1,absoluteProjectPath)

import parameters_run as p 
# ------------------------------------------------


class ReplaySimulation(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """


    def __init__(self, width, height, title, ud_rate, trackPath):
        self.arena_layout_path = p.START_ARENA_LAYOUT_PATH
        width, height = self.load_arena_layout(return_w_h=True)
        super().__init__(width, height, title, update_rate = ud_rate)

        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.player_list = None
        self.wall_list = None
        self.obstacle_list = None
        self.light_list = None

        self.currentUpdateRate = ud_rate
        self.trackPath = trackPath
        self.annPath = trackPath[:trackPath.find("/track.csv")]+"/annOutputs.csv"
        
 
    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Global variables
        self.simulationRun = True    
        self.updateRateDec = False   
        self.updateRateInc = False
        self.incTimeSteps = False
        self.decTimeSteps = False

        self.plotFitness = PlotFitness()
        #dataPath = absoluteProjectPath+"/kingsFitness.csv"
        #self.fitnessData = self.plotFitness.getData([dataPath]) 
        

        # Create your sprites and sprite lists here
        self.agent_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.obstacle_list = arcade.SpriteList(use_spatial_hash=True)
        self.light_list = arcade.SpriteList(use_spatial_hash=True)
                
        # read arena layout from csv file
        
        self.arena_layout_file_name = p.ARENA_LAYOUT_NAME
        self.load_arena_layout()

        self.loadTrackingDataOfCsvFile()
        self.loadAnnDataOfCsvFile()

        self.timestep = 0
        
        self.timeStepIncreasement = 1
        
        # Set start position of all objects related by arena layout
        # Box size defines interval of grid (arena layout)
        agent_scaling = p.OBJECT_SIZE_AGENT/p.OBJECT_IS_SIZE
        box_scaling = p.OBJECT_SIZE_BOX/p.OBJECT_IS_SIZE_BOX
        light_scaling = p.OBJECT_SIZE_LIGHT/p.OBJECT_IS_SIZE_LIGHT
        count_robot = 0
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
                                                center_y=center_y
                                                ))
        #         elif value == 3: # start position for new robot 
        #             self.agent_list.append(Robot(filename=p.IMAGE_AGENT, 
        #                                         scale=agent_scaling,
        #                                         center_x=center_x,
        #                                         center_y=center_y,
        #                                         start_angle=0,#random.randint(0,360)
        #                                         robot_size=p.OBJECT_SIZE_AGENT,
        #                                         top_speed=p.TOP_SPEED,
        #                                         top_speed_turn=p.TOP_SPEED_TURN,
        #                                         sensor_number=p.SENSOR_NUMBER,
        #                                         sensor_image=p.IMAGE_SENSOR,
        #                                         sensor_image_size=p.OBJECT_IS_SIZE_SENSOR,
        #                                         sensor_length=p.SENSOR_LENGTH,
        #                                         sensor_steps=p.SENSOR_STEPS,
        #                                         sensor_arrangement=p.SENSOR_ARRANGEMENT,
        #                                         id=count_robot
        #                                         ))
        #             count_robot += 1
        # if count_robot != p.NUMBER_ROBOTS:
        #     print(f"[Error] number of robot spawns ({count_robot}) and number of robots to be created ({p.NUMBER_ROBOTS}) unequal!")
        #     self.close()

        for i in range(p.NUMBER_ROBOTS):
        
            rand_x_center = min( max(p.OBJECT_SIZE_BOX*5,np.random.randint(p.SCREEN_WIDTH)), p.SCREEN_WIDTH-p.OBJECT_SIZE_BOX*5)
            rand_y_center = min( max(p.OBJECT_SIZE_BOX*5,np.random.randint(p.SCREEN_HEIGHT)), p.SCREEN_HEIGHT-p.OBJECT_SIZE_BOX*7)
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

        # defines the pysics engine (for collision avoidance)
        self.physics_engine = arcade.PhysicsEngineSimple(self.agent_list[0], self.wall_list)




    def on_draw(self):
        """
        Render the screen.
        """
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()
        self.light_list.draw()
        for agent in self.agent_list:
            #for sensor_list in agent.sensor_list_steps:
            agent.sensor_list_steps[-1].draw()
                #sensor_list.draw()
        self.wall_list.draw()
        self.obstacle_list.draw()
        self.agent_list.draw()

        # Draw Label
        batterie_string = "Battery Level: "
        for agent in self.agent_list:
            batterie_string += str(round(agent.battery,2))+", "
        arcade.draw_text(batterie_string[:-2],
                         5, 0, arcade.color.BLACK, 14)
        
        playbackspeed = round( ((1./self.currentUpdateRate)*float(self.timeStepIncreasement))/p.REAL_FPS ,1)
        arcade.draw_text(f"Time Step: {self.timestep} of {len(self.headingPerTsPerRobot[0])},  Update Rate: {round(1/self.currentUpdateRate,1)} [1/s],  Playback Speed: {playbackspeed}x",
                         5, self.height-20, arcade.color.BLACK, 14)
        #if len(self.predictionPerTs) > self.timestep:
        #    rounded_predictions = [round(num,2) for num in self.predictionPerTs[self.timestep]]
        #    arcade.draw_text(f"Predictions: {rounded_predictions}",
        #                    5, self.height-35, arcade.color.BLACK, 14)
     
     



    def on_update(self, delta_time:float):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
      
        ########### CONTROL SECTION #########################
        if self.incTimeSteps:
            self.changeTimeSteps(50)
        elif self.decTimeSteps:
            self.changeTimeSteps(-50)
        if self.updateRateInc:
            self.changeUpdateRate(2)
        elif self.updateRateDec:
            self.changeUpdateRate(-2)



        # Check of end of Simulation
        if self.timestep >= len(self.headingPerTsPerRobot[0]):
            return
        #print(self.timestep)

        ########### LOGIC SECTION #############################
        # for each robot do:
        for idx, robot in enumerate(self.agent_list):
            # get tracking data of track file (heading, xposition, yposition, battery and layout_path)
            heading = self.headingPerTsPerRobot[idx][self.timestep]
            xyPosition = self.positionPerTsPerRobot[idx][self.timestep]
            batteryLevel = self.batteryPerTsPerRobot[idx][self.timestep]
            # set variables
            robot.center_x = xyPosition[0]
            robot.center_y = xyPosition[1]
            robot.angle = heading
            robot.battery = batteryLevel
       

        # check for new arena layout
        for idx, (changes, layoutFileName) in enumerate(self.layoutChangeIndex):
            if idx != len(self.layoutChangeIndex)-1 :
                next_change = self.layoutChangeIndex[idx+1][0]
            else:
                next_change = 999999999999
            if self.timestep >= changes and self.timestep < next_change: # check for changes
                self.initialNewArenaLayout(layoutFileName)

    

        ############# SIMULATION UPDATE SECTION ######################
        #
        # Update Sensor Position and Angle for each agent
        for agent in self.agent_list:
            for sensor_list in agent.sensor_list_steps:
                for sensor in sensor_list:    
                    sensor.follow_robot(agent)
                    sensor_list.update()
        

        #self.agent_list.update()
        #self.physics_engine.update()
        self.timestep += self.timeStepIncreasement
        



    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        # TODO springen mit pfeiltasten (time step updaten)
        # TODO vorspulen mit anderen Tasten self.set_update_rate(...)
        # TODO Post evaluation bis zu diesem Zeitschritt
        
        if key == arcade.key.UP:
            self.updateRateInc = True
        elif key == arcade.key.DOWN:
            self.updateRateDec = True
        if key == arcade.key.LEFT:
            self.decTimeSteps = True
        elif key == arcade.key.RIGHT:
            self.incTimeSteps = True
        if key == arcade.key.SPACE: # Pausieren/Start mit Leertaste
            if self.simulationRun:
                self.set_update_rate(0)
                self.simulationRun = False
            else:
                self.set_update_rate(self.currentUpdateRate)
                self.simulationRun = True
        if key == arcade.key.KEY_1:
            self.setTimestepIncreasement(1)
        elif key == arcade.key.KEY_2:
            self.setTimestepIncreasement(2)
        elif key == arcade.key.KEY_3:
            self.setTimestepIncreasement(3)
        elif key == arcade.key.KEY_4:
            self.setTimestepIncreasement(4)
        elif key == arcade.key.KEY_5:
            self.setTimestepIncreasement(5)
        elif key == arcade.key.KEY_6:
            self.setTimestepIncreasement(6)
        elif key == arcade.key.KEY_7:
            self.setTimestepIncreasement(7)
        elif key == arcade.key.KEY_8:
            self.setTimestepIncreasement(8)
        elif key == arcade.key.KEY_9:
            self.setTimestepIncreasement(9)
        elif key == arcade.key.KEY_0:
            self.setTimestepIncreasement(30)
        if key == arcade.key.M: # Pausieren/Start mit Leertaste
            self.set_update_rate(0)
            self.simulationRun = False
            #self.plotFitness.plotData(self.fitnessData)


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.UP or key == arcade.key.DOWN:
           self.updateRateInc = False
           self.updateRateDec = False
           
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.incTimeSteps = False
            self.decTimeSteps = False

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
    

    def setTimestepIncreasement(self, change):
        """ set increasement of timesteps for skipping timesteps to discard some informations to speed up the run """
        self.timeStepIncreasement = change


    def changeUpdateRate(self, change):
        """ changes update rate with a factor or *change* """
        fps = self.currentUpdateRate**(-1)
        newFps = fps + (float(change))
        if newFps <= float(1.):
            newFps = float(1.)
        elif newFps >= float(60.):
            newFps = float(60.)
        
        self.currentUpdateRate = float(1./newFps)
        self.set_update_rate(self.currentUpdateRate)

    def changeTimeSteps(self, change):
        """ changes time step with a factor or *change* """
        newTimeStep = self.timestep + change
        if newTimeStep < 0:
            newTimeStep = 0
        elif newTimeStep >= len(self.positionPerTsPerRobot[0]):
            newTimeStep = len(self.positionPerTsPerRobot[0])-1
        self.timestep = newTimeStep


    def load_arena_layout(self, return_w_h=False):
        with open(self.arena_layout_path+".csv", 'r') as f:
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

    def loadTrackingDataOfCsvFile(self):
        """ reads whole csv tracking file and split heading, positions, battery level and the time step index + layout name of changing arena layouts in various arrays  """
        self.headingPerTsPerRobot = []
        self.positionPerTsPerRobot = [] # x and y coordinates
        self.batteryPerTsPerRobot = []
        self.layoutChangeIndex = []
        self.layoutChangeIndex.append((0, self.arena_layout_file_name))
        for idxRobot in range(p.NUMBER_ROBOTS):
            self.headingPerTsPerRobot.append([])
            self.positionPerTsPerRobot.append([])
            self.batteryPerTsPerRobot.append([])

        with open(self.trackPath, 'r') as f:
            csv_reader = csv.reader(f ,delimiter=',')
            #rows = list(csv_reader)
            header = next(csv_reader)
            lastLayout = p.ARENA_LAYOUT_NAME
            lineCounter = 0
            for row in csv_reader:
                for idxRobot in range(p.NUMBER_ROBOTS):
                    self.headingPerTsPerRobot[idxRobot].append(float(row[0+ 4*idxRobot]))
                    self.positionPerTsPerRobot[idxRobot].append((float(row[1+ 4*idxRobot]),float(row[2+ 4*idxRobot])))
                    self.batteryPerTsPerRobot[idxRobot].append(float(row[3+ 4*idxRobot]))
                if lastLayout != row[-1]: # layout changed
                    self.layoutChangeIndex.append((lineCounter, row[-1]))
                    lastLayout = row[-1]
                lineCounter += 1    

    def loadAnnDataOfCsvFile(self):
        """ reads whole csv tracking file and split heading, positions, battery level and the time step index + layout name of changing arena layouts in various arrays  """
        self.predictionPerTs = []

        with open(self.annPath, 'r') as f:
            csv_reader = csv.reader(f ,delimiter=',')
            #rows = list(csv_reader)
            header = next(csv_reader)
            lineCounter = 0
            for row in csv_reader:
                
                self.predictionPerTs.append([float(i) for i in row[2:]])
                

    def initialNewArenaLayout(self, layoutFileName):
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.obstacle_list = arcade.SpriteList(use_spatial_hash=True)
        self.light_list = arcade.SpriteList(use_spatial_hash=True)

        self.arena_layout_path = p.ARENA_LAYOUT_FOLDER+"/"+layoutFileName
        self.load_arena_layout()
        # Set start position of all objects related by arena layout
        # Box size defines interval of grid (arena layout)
        agent_scaling = p.OBJECT_SIZE_AGENT/p.OBJECT_IS_SIZE
        box_scaling = p.OBJECT_SIZE_BOX/p.OBJECT_IS_SIZE_BOX
        light_scaling = p.OBJECT_SIZE_LIGHT/p.OBJECT_IS_SIZE_LIGHT
        count_robot = 0
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
                                                center_y=center_y
                                                ))
                
    


def main():
    
    #sys.path.insert(1,"../") #TODO hier nochmal schauen ob bessere loesung (um nicht den absoluten path zu nutzen)
    # TODO parameter selection path von parameter datei suchen und laden
    # TODO path von evolution ordner uebergeben
    simulation = ReplaySimulation(p.SCREEN_WIDTH, p.SCREEN_HEIGHT, p.SCREEN_TITLE, 1./60., trackPath)
    simulation.setup()
    arcade.run()
       

if __name__ == "__main__":
    main()

        