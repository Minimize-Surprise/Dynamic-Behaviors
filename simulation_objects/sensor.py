import arcade
import os
import random
import numpy as np
import math



class Sensor(arcade.Sprite):
    """ Main Sensor class. """
    def __init__(self,
                filename: str = None,
                scale: float = 1,
                image_x: float = 0, image_y: float = 0,
                image_width: float = 0, image_height: float = 0,
                center_x: float = 0, center_y: float = 0,
                repeat_count_x: int = 1, repeat_count_y: int = 1,
                start_angle: int = 0
                #color = None
                ):

        super().__init__(filename=filename,scale=scale,
        image_x=image_x,image_y=image_y,image_width=image_width, image_height=image_height,
        center_x=center_x, center_y=center_y, repeat_count_x=repeat_count_x, repeat_count_y=repeat_count_y)
       
        self.start_angle = start_angle
        self.angle = self.start_angle
        #self.color = color

    def follow_robot(self, robot: arcade.Sprite):
        '''
         # update angle and position of all sensor sprites, after robot update (with engine) is done
         # Should be executed after engine update
        '''
        # update angle
        self.angle = self.start_angle + robot.angle
        # update position
        self.center_x = robot.center_x
        self.center_y = robot.center_y
    
    #def check_distance_to_sprite(self, target_sprite):
    #    return np.linalg.norm(np.array([self.center_x,self.center_y])-
    #                   np.array([target_sprite.center_x, target_sprite.center_y]))
    
 
    
    
    
 

        
