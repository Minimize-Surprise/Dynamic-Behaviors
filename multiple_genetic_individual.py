import random
import numpy
from action_network import ActionNetwork
from prediction_network import PredictionNetwork
from swarm_member import SwarmMember
import parameters as p
import queue

class MultipleGeneticIndividual:
        """ represents an individual in a genetic population

        The individual has both an action and a prediction network.

        Usage:

        Call *processSensorValues* with the current sensor values in order to get the calculated action values.
        The method updates the overall prediction error and prediction next proximity sensors for calculations in next time step.

        Note:

        Call *evaluate* after termination of the actual run, to get the final fitness value.
        """

        def __init__(self, indiv_id, updatePredictionError):
                #amountProxSensors, amountAdditionalSensors, amountActions, amountHiddenAction, amountHiddenPrediction, activationFunctionAction, activationFunctionPrediction
                """ creates a new individual with random weights

                An individual has an action network and a prediction network.
                The amount of input values for the action and prediction networks is the sum of all proximity sensors *amountProxSensors* and the additional sensors *amountAdditionalSensors* (compass, light intensity sensor, battery level).
                The amount of output values of the action network is the amount of actions.
                The amount of output values of the prediction values equals *amountSensors*.

                Arguments:
                id -- id of individual
                amountSensors -- the amount of sensors this individual has
                amountActions -- the amount of actions this individual should predict
                amountHiddenAction -- amount of hidden nodes in the action network
                amountHiddenPrediction -- amount of hidden nodes in the prediction network
                activationFunctionAction -- activation function used in the action network
                activationFunctionPrediction -- activation function used in the prediction network

                """
                self.id = indiv_id
                self.updatePredictionError = updatePredictionError
                self.swarm_members = []
                for member_index in range(p.NUMBER_ROBOTS):
                        self.swarm_members.append( SwarmMember(member_index) )
                
                # equalize weights of all swarm members after initialzation
                genomeAction =  self.swarm_members[0].actionNetwork.toGenome()
                genomePrediction =  self.swarm_members[0].predictionNetwork.toGenome()
                for swarm_member in self.swarm_members:
                        swarm_member.actionNetwork.fromGenome(numpy.array(genomeAction))
                        swarm_member.predictionNetwork.fromGenome(numpy.array(genomePrediction))

                self.reset()
                

        def reset(self):
                """ Reset indiviual for evaluation. Call before start new Simulation with this individual.
                    Reset all parameters for fitness computation.
                    Do not reset any network parameters (its part of recombination/mutation process)!!
                """
                self.error_sum = 0
                self.n = 0
                self.fitnessValue = -1
                for swarm_member in self.swarm_members:
                        swarm_member.reset() # reset lastPrediction and lastAction value
              

        def updateId(self, newId):
                """ updates individual id after generated the new offsprings. """
                self.id = newId


        def processSensorValues(self, actualProximitySensors, additionalSensors, boredomPunishment, memberId): #, boredom_turn_Punishment, boredom_pos_punishment):
                """ Method to be called by the simulation in each time step.
                Update the prediction error and perform new predictions.
                Returns next action and new predictions to simulation (prediction just for logging) """
                current_member = self.swarm_members[memberId]
                # update sum of prediction error
                #self._updatePredictionError(actualProximitySensors, additionalSensors[0], boredomPunishment) #, boredom_turn_Punishment, boredom_pos_punishment)
                self.error_sum, self.n = self.updatePredictionError(actualProximitySensors, 
                        additionalSensors[0], # actualLightSensor
                        boredomPunishment,
                        current_member.lastPrediction,
                        self.error_sum,
                        self.n,
                        additionalSensors[2] # battery level
                        )

                # create input for ANNs
                inputVector = numpy.concatenate((actualProximitySensors, additionalSensors), 0)
                next_action = current_member._action(inputVector)
                current_prediction = current_member._predict(inputVector)
                # return new actions and predictions
                return next_action, current_prediction


        # def _updatePredictionError(self, actualProximitySensors, actualLightSensor, boredomPunishment): #, boredom_turn_Punishment, boredom_pos_punishment):
        #         """ Compute error with last sensor prediction and actual proximity sensor values.
        #             Increment and number of observations """
        #         error_sensor_vector = [numpy.absolute((self.lastPrediction[i] - actualProximitySensors[i])) for i in range(self.amountProxSensors)]
        #         error_light_vector = [numpy.absolute((self.lastPrediction[-1] - actualLightSensor))]
        #         error_sensor_light_vector = numpy.concatenate( (error_sensor_vector,  error_light_vector) )
        #         error_value = (float(numpy.sum(error_sensor_light_vector)) / float(p.AMOUNT_OUTPUT_PREDICTION)) # 5 prox sensors + 1 light sensor

        #         #error_with_boredom = max(error_value,max(boredomPunishment))# boredom_turn_Punishment, boredom_sensor_value, boredom_pos_punishment, error_value)
        #         error_with_boredom = max(error_value,boredomPunishment)# boredom_turn_Punishment, boredom_sensor_value, boredom_pos_punishment, error_value)

        #         #print("{:<20} {:<20} {:<20} {:<20}".format(boredom_pos_punishment,boredom_turn_Punishment,boredom_sensor_value,error_value))
        #         #print("{:<20} {:<20}".format(boredomPunishment[1], error_value))
                
        #         self.error_sum += error_with_boredom
        #         self.n += 1




        def evaluate(self):
                #self.fitnessValue = 1 - ((self.error_sum / self.n) /  p.NUMBER_ROBOTS)
                self.fitnessValue = (self.n - self.error_sum) /  (p.MAX_TIME_STEPS_REACHED * p.NUMBER_ROBOTS) 
                return self.fitnessValue


        def mutate(self, rate): 
                """ mutates a copy of this individual and returns it

                Arguments:
                rate -- a real number in [0,1) specifiying the probability for each number in genome to be mutated; should not be much greater than 0.3

                """

                example_member = self.swarm_members[0]
                genomeAction = example_member.actionNetwork.toGenome()
                genomePrediction = example_member.predictionNetwork.toGenome()

                # mutate
                genomeAction = [x if random.random()>=rate else x + random.uniform(-p.MUTATION_CHANGE, p.MUTATION_CHANGE) for x in genomeAction]
                genomePrediction = [x if random.random()>=rate else x + random.uniform(-p.MUTATION_CHANGE, p.MUTATION_CHANGE) for x in genomePrediction]

                for swarm_member in self.swarm_members:
                        swarm_member.actionNetwork.fromGenome(numpy.array(genomeAction))
                        swarm_member.predictionNetwork.fromGenome(numpy.array(genomePrediction))
                
                # do not need a copy!
                #copy = GeneticIndividual(self.id)
                #copy.actionNetwork.fromGenome(numpy.array(genomeAction))
                #copy.predictionNetwork.fromGenome(numpy.array(genomePrediction))
                # return copy



