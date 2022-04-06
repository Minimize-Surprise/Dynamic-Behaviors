import arcade
import os
import random
import numpy as np


class LightSource(arcade.Sprite):
    """ Sprite LightSource class. """

    def __init__(self,
                filename: str = None,
                scale: float = 1,
                image_x: float = 0, image_y: float = 0,
                image_width: float = 0, image_height: float = 0,
                center_x: float = 0, center_y: float = 0,
                repeat_count_x: int = 1, repeat_count_y: int = 1, this_color = (255,255,255) , 
                screen_width: int = 500, screen_height: int = 500):

        super().__init__(filename=filename,scale=scale,
        image_x=image_x,image_y=image_y,image_width=image_width, image_height=image_height,
        center_x=center_x, center_y=center_y, repeat_count_x=repeat_count_x, repeat_count_y=repeat_count_y)
        self.set_color(this_color)
        self.screen_width = screen_width
        self.screen_height = screen_height

    def set_color(self, rgb_tripel):
        self.color = rgb_tripel

    
    def set_position(self, ch_x, ch_y):
        """
        # Forward Kinematics for Differential Drive Robots
        # In: Wheel velocities, Out: Position and Heading
        """
        self.center_x = ch_x
        self.center_y = ch_y

    #def check_distance_to_sprite(self, sprite1, sprite2):
    #    return np.linalg.norm(np.array([sprite1.center_x,sprite1.center_y])-
    #                   np.array([sprite2.center_x, sprite2.center_y]))
    #    pass 

    def get_light_intensity_for_sprite(self, target_sprite): 
        """
        Get light intensity for a specific sprite.
        Interval between 0 and 1.
        """
        distance =  np.linalg.norm(np.array([self.center_x,self.center_y])-
                       np.array([target_sprite.center_x, target_sprite.center_y]))
        return ((self.screen_width-190)-distance)**2/(self.screen_width-190)**2  # TODO
 
    
    
    
 

        
