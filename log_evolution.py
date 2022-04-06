
import numpy as np
import parameters as p
import shutil
import os
from log_individual import write_csv
import parameters as p
import shutil


class LogEvolution:
    """ creates folder and log for the general evolution structure 
        - Logs all parameters used in this setup
        - Logs fitness values of all kings
    """
    def __init__(self):
        self.evolution_path = p.EVOLUTION_PATH
        self.folderPath = self.evolution_path
        # Create Folders
        makedir(p.EVOLUTION_PATH)
        makedir(p.EVOLUTION_PATH+"kings/")
        self._copyParameterFile()

    def _copyParameterFile(self):
        """ copy parameter file to evolution logs 
            Is used for the replay
        """
        src_file = "parameters.py"
        dst_file = self.evolution_path + "parameters_run.py"
        #try:
        shutil.copyfile(src_file, dst_file)
        #except FileExistsError:
        #    print(f"File {dst_file} already existing!")


    def storeFitnessKings(self, line, new = False):
        """ writes the line to the king fitness logfile """
        write_csv(self.folderPath+"kingsFitness.csv" , line, new)

def makedir(path):
    try:
        os.mkdir(path)  
    except FileExistsError:
        pass
        #print(f"Folder {path} already exists!")