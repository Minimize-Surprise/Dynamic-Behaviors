
from genetic_population import GeneticPopulation
import parameters as p
import os
from log_evolution import LogEvolution
import copy
import numpy as np
from post_evaluation.plotFitness import PlotFitness
from post_evaluation.plotData import PlotData
import sys



def updatePredictionError(actualProximitySensors, 
                        actualLightSensor, 
                        boredomPunishment,
                        lastPrediction,
                        error_sum,
                        n,
                        battery_level=None):
    """ Compute error with last sensor prediction and actual proximity sensor values.
                    Increment and number of observations """
    error_sensor_vector = [np.absolute((lastPrediction[i] - actualProximitySensors[i])) for i in range(p.SENSOR_NUMBER)]
    error_light_vector = [np.absolute((lastPrediction[-1] - actualLightSensor))]
    error_sensor_light_vector = np.concatenate( (error_sensor_vector,  error_light_vector) )
    error_value = (float(np.sum(error_sensor_light_vector)) / float(p.AMOUNT_OUTPUT_PREDICTION)) # 5 prox sensors + 1 light sensor

    #error_with_boredom = max(error_value,max(boredomPunishment))# boredom_turn_Punishment, boredom_sensor_value, boredom_pos_punishment, error_value)
    error_with_boredom = max(error_value,boredomPunishment)# boredom_turn_Punishment, boredom_sensor_value, boredom_pos_punishment, error_value)

    #print("{:<20} {:<20} {:<20} {:<20}".format(boredom_pos_punishment,boredom_turn_Punishment,boredom_sensor_value,error_value))
    
    new_error_sum = error_sum + error_with_boredom
    new_n = n + 1
    #print("{:<20} {:<20} {:<20} {:<20}".format(boredomPunishment, error_value, new_error_sum, new_n))
    return new_error_sum, new_n

def updatePredictionAndLightIntensityError(actualProximitySensors, 
                        actualLightSensor, 
                        boredomPunishment,
                        lastPrediction,
                        error_sum,
                        n,
                        battery_level):
    """ Compute error with last sensor prediction and actual proximity sensor values.
                    Increment and number of observations """
    error_sensor_vector = [np.absolute((lastPrediction[i] - actualProximitySensors[i])) for i in range(p.SENSOR_NUMBER)]
    error_light_vector = [np.absolute((lastPrediction[-1] - actualLightSensor))]
    error_sensor_light_vector = np.concatenate( (error_sensor_vector,  error_light_vector) )
    error_value_prediction = (float(np.sum(error_sensor_light_vector)) / float(p.AMOUNT_OUTPUT_PREDICTION)) # 5 prox sensors + 1 light sensor
    #1-(1-battery_level)**2
    if not p.QUADRATIC_FUNCTION:
        error_value = battery_level * error_value_prediction   +   (1-battery_level) * (1-actualLightSensor) # 1-lightintensity -> here we compute the error: battery low -> error high if far away from lightsource 
    else:
        error_value = (1-(1-battery_level)**2) * error_value_prediction   +   ((1-battery_level)**2) * (1-actualLightSensor) # 1-lightintensity -> here we compute the error: battery low -> error high if far away from lightsource 

    #error_with_boredom = max(error_value,max(boredomPunishment))# boredom_turn_Punishment, boredom_sensor_value, boredom_pos_punishment, error_value)
    error_with_boredom = max(error_value,boredomPunishment)# boredom_turn_Punishment, boredom_sensor_value, boredom_pos_punishment, error_value)

    new_error_sum = error_sum + error_with_boredom
    new_n = n + 1
    #print("{:<20} {:<20} {:<20} {:<20}".format(error_value_prediction, actualLightSensor, error_value, battery_level))
    #print("{:<20}".format(1-(error_with_boredom)))
    return new_error_sum, new_n
    


class Evolution:

    def __init__(self):

        # create logs and folders for evolution
        self.log_evolution = LogEvolution()

        # create new population with specific fitness function
        self.popu = GeneticPopulation(0) # init population with generation number 0

        print(f"Approach {p.APPROACH_NUMBER} with adaptive fitness function {p.ADAPT_FITNESS_FUNCTION}:")
        if p.ADAPT_FITNESS_FUNCTION:
            self.popu.initStartPopulation(updatePredictionAndLightIntensityError)
        else:
            self.popu.initStartPopulation(updatePredictionError)

        if p.ADAPT_FITNESS_FUNCTION and p.APPROACH_NUMBER == 1:
            print("[Warning] adaptive fitness function is set to True but approach 1 is running!")
        if  not p.ADAPT_FITNESS_FUNCTION and p.APPROACH_NUMBER == 2:
            print("[Warning] adaptive fitness function is set to False but approach 2 is running!")
            
        
        self.kings = []

        self.generationNumber = 0
        

    def startEvolutionProcess(self):
        """ starts the evolution process: 
                1. Init random Population (Done in __init__), call *GeneticPopulation()*
                2. Evaluate Population (Run Simulation), call *evaluate*
                3. Find best individual in population *selectKing*
       
                5. Check termination condition *checkForTermination*
                5.1 Log king fitness for all generations
                5.2 Create plots with kings fitness

                6. Perform offspring selection:
                    6.1 Copy actual king to Offspring Population (OP)
                    6.2 Loop until population is filled:
                        6.2.1 Select Individual with proportinate Selection (PS)
                        6.2.2 According to recombination propability:
                            6.2.2.1 If True: Select second individual (with PS), use recombination -> Get two new offspring individuals
                        6.2.3 Mutate both individuals if 6.2.2 True, else mutate the single individual (selected in 6.2.1)
                        6.2.4 Add mutated individual(s) 
                        6.2.5 GOTO 6.2
                    6.3 If number of new offspring > actual population: Delete the last added individual (needed if only one indiviual is needed but because of recoombination two are produced)

                7. Offspring Population is now new parent populatuion
                8. Increase generation number 
                9. GOTO 2. (Evaluate Popuation)
                
        """
        
        while(True): # 1.

            self.popu.evaluate() # 2.

            king = self.popu.selectKing() # 3. 
            print(f" -> King fitness of Generation {self.generationNumber} is: {king.fitnessValue}")
            # deep copy, otherwise king will be updated in self.kings afterwards, because of pythons strange memory management (see mutable, immutable)
            self.kings.append(copy.deepcopy(king)) 


            if self.popu.checkForTermination(): # 5.
                self._storeKingFitnessValues() # 5.1
                self._createFitnessPlots() # 5.2
                break
            
            # --------- Offspring selection 6. ---------------
            self.generationNumber +=1
            # Build new Offspring for next generation
            offspringPopulation = GeneticPopulation(self.generationNumber) # init offspring population (next generation)
            offspringPopulation.addIndividual(king) # add king to offspring population

            while( len(offspringPopulation) < p.POPULATION_SIZE ): # fill OP
                firstIndividual = self.popu.proportionateSelection()  # copy/select individual
                
                if np.random.rand() < p.RECOMBINATION_PROBABILITY:
                    secondIndividual = self.popu.proportionateSelection() # copy/select second individual
                    self._recombine(firstIndividual, secondIndividual)  # recombine them
                    secondIndividual.mutate(p.MUTATION_RATE)  # mutate second
                    offspringPopulation.addIndividual(secondIndividual) # add second to OP
                
                if len(offspringPopulation) < p.POPULATION_SIZE: # if population size already reached, do not add the first individual 6.3
                    
                    firstIndividual.mutate(p.MUTATION_RATE) # mutate first
                    offspringPopulation.addIndividual(firstIndividual) # add fist to OP
           
            
            # ---------- End Offspring selection------------

            self.popu = offspringPopulation # 7.

            #print(f"Generation {self.generationNumber} Done!")


    def _recombine(self, firstIndividual, secondIndividual):
        """ recombines two individuals: change genomes of prediction network """
        
        firstGenomePrediction = firstIndividual.predictionNetwork.toGenome()   
        secondGenomePrediction = secondIndividual.predictionNetwork.toGenome()

        firstIndividual.predictionNetwork.fromGenome(np.array(secondGenomePrediction))
        secondIndividual.predictionNetwork.fromGenome(np.array(firstGenomePrediction))

    def _storeKingFitnessValues(self):
        """ logs fitness of king for each generation"""
    
        self.log_evolution.storeFitnessKings(f"fitnessKingOfGenX", True)
        for nextKing in self.kings:
            self.log_evolution.storeFitnessKings(str(nextKing.fitnessValue)) 
        
    def _createFitnessPlots(self):
        """ create a plot of fitness values of kings over all generations and stores it in the folder """
        self.plotFitness = PlotFitness()
        self.plotData = PlotData()
        fitnessDataForPlotting = np.array([ [nextKing.fitnessValue for nextKing in self.kings] ]) # needs to be a 2d array
        self.plotFitness.plotData(fitnessDataForPlotting, saveFig=p.EVOLUTION_PATH+"ResultKingsFitness", showPlot=False)
        self.plotData.plotFitnessRechargePosition(p.EVOLUTION_PATH, saveFig=p.EVOLUTION_PATH+"ResultKingsFitnessWithPosition", showPlot=False)
        self.plotData.plotPositionHistogramm(p.EVOLUTION_PATH, saveFig=p.EVOLUTION_PATH+"ResultKingsHeatmap", showPlot=False)

def main():
    evolution = Evolution()
    evolution.startEvolutionProcess()
       

if __name__ == "__main__":
    main()



