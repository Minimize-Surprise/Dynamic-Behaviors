import numpy as np
import parameters as p
import shutil
import os
import csv

class LogIndividual:
    """ creates folder and log for each individual  
        Logging:
        - trajectory (track)
        - sensor data
        - outputs of ANNs
        - genomes of action network
        - genomes of prediction network
        
        Provides methods for storing individuals permanetly in other folder
    """
        
# TODO
    def __init__(self, generationNumber):
        self.generationNumber = generationNumber
        self.evolution_path = p.EVOLUTION_PATH
        self.folderName = "gen" + str(generationNumber)
        self.folderPath = self.evolution_path + "kings/" +  self.folderName + "/"
        try:
            os.mkdir(self.folderPath)
        except FileExistsError:
            pass
            #print(f"Folder {self.folderPath} already existing!")
        
        
        
        string_track = ''
        string_sensorData = ''
        string_annOut = ''
        
        for agent_idx in range(p.NUMBER_ROBOTS):
            string_track += "headingAgent"+str(agent_idx)+",positionXAgent"+str(agent_idx)+",positionYAgent"+str(agent_idx)+ ",battery"+str(agent_idx)+","
            
            for i in range(p.NUMBER_ACTIONS):
                string_annOut += f"action{i}Agent{agent_idx},"

            for i in range(p.SENSOR_NUMBER):
                string_annOut += f"prediction{i}Agent{agent_idx},"
                string_sensorData += f"proxiS{i}Agent{agent_idx},"
            string_annOut += f"lightPredictionAgent{agent_idx},"   

            if p.CHECK_LIGHT_SENSOR:
                string_sensorData += f"lightSensorAgent{agent_idx},"
            if p.CHECK_COMPASS:
                string_sensorData += f"compassAgent{agent_idx},"
            if p.CHECK_BATTERY:
                string_sensorData += f"batteryAgent{agent_idx},"

        
        

        string_track = string_track + "layoutPath"
        self.tracking(string_track, True)
        self.storeSensorData(string_sensorData[:-1], True)
        self.storeAnnOut(string_annOut[:-1], True)
        self.storeResults(f"fitness,maxTimeStepReached,timeSpentInLightSource", True) 
        
       
    

    def tracking(self, line, new = False, close=False):
        """ writes the line to the tracking logfile """
        write_csv(self.folderPath+"track.csv" , line, new, close)

    def storeAnnOut(self, line, new = False, close=False):
        """ writes the line to the ann output logfile """
        write_csv(self.folderPath+"annOutputs.csv" , line, new, close)

    def storeSensorData(self, line, new = False, close=False):
        """ writes the line to the sensor data logfile """
        write_csv(self.folderPath+"sensorData.csv" , line, new, close)

    def storeActionGenome(self, genome): 
        """ stores action genome of individual """
        np.save(self.folderPath+"actionGenome.npy",genome)
    
    def storePredictionGenome(self, genome):
        """ stores prediction genome of individual """
        np.save(self.folderPath+"predictionGenome.npy",genome)
    
    def storeResults(self, line, new = False, close=False): 
        """ writes the line to the results logfile """
        write_csv(self.folderPath+"results.csv" , line, new, close)

    # def copyLogFileToGenerationKing(self, generation):
    #     """ copies best individuum to king folder to prevent its overwriting of logs """
    #     src_file = self.folderPath
    #     dst_file = self.evolution_path + "kings/gen" + str(generation)
    #     try:
    #         shutil.copytree(src_file, dst_file)
    #     except FileExistsError:
    #         pass
    #         #print(f"Folder {dst_file} already existing!")
        

def write_csv(filename, line, new = False, close=True):
    """ writes the given line to specified csv file

    Arguments:
    filename -- the file the line should be written to; the file ending '.csv' will be added within the method, so you should really omit '.csv' in filename ;)
    line -- the line to be written
    new -- create new csv file

    """
    if new:
        file = open(filename, "w")
    else:
        file = open(filename, "a")
    file.write(line + "\n")
    if close:
        file.close()
