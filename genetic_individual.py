import random
import numpy
from action_network import ActionNetwork
from prediction_network import PredictionNetwork
import parameters as p
import queue

class GeneticIndividual:
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
                self.amountProxSensors = p.SENSOR_NUMBER
                self.amountAdditionalSensors = p.NUMBER_OF_ADDITIONAL_SENSORS
                self.amountActions = p.NUMBER_ACTIONS
                self.amountHiddenAction = p.AMOUNT_HIDDEN_ACTION
                self.amountHiddenPrediction = p.AMOUNT_HIDDEN_PREDICTION
                self.updatePredictionError = updatePredictionError

                if p.ACTIVATION_FUNCTION_ACTION == "tanh":
                        self.activationFunctionAction = tanh
                if p.ACTIVATION_FUNCTION_ACTION == "sigmoid":
                        self.activationFunctionAction = sigmoid

                if p.ACTIVATION_FUNCTION_PREDICTION == "tanh":
                        self.activationFunctionPrediction = tanh
                if p.ACTIVATION_FUNCTION_PREDICTION == "sigmoid":
                        self.activationFunctionPrediction = sigmoid

                self.actionNetwork = ActionNetwork((self.amountProxSensors + self.amountAdditionalSensors + p.NUMBER_ACTIONS), self.amountHiddenAction, self.amountActions, self.activationFunctionAction)
                self.predictionNetwork = PredictionNetwork((self.amountProxSensors + self.amountAdditionalSensors + p.NUMBER_ACTIONS), self.amountHiddenPrediction, p.AMOUNT_OUTPUT_PREDICTION, self.activationFunctionPrediction)

                self.reset()
                

        def reset(self):
                """ Reset indiviual for evaluation. Call before start new Simulation with this individual.
                    Reset all parameters for fitness computation.
                    Do not reset any network parameters (its part of recombination/mutation process)!!
                """
                self.error_sum = 0
                self.lastPrediction = numpy.random.random(p.AMOUNT_OUTPUT_PREDICTION)
                self.lastAction = numpy.random.random(self.amountActions)
                self.n = 0
                self.fitnessValue = -1
              

        def updateId(self, newId):
                """ updates individual id after generated the new offsprings. """
                self.id = newId


        def processSensorValues(self, actualProximitySensors, additionalSensors, boredomPunishment, robotIndex=None): #, boredom_turn_Punishment, boredom_pos_punishment):
                """ Method to be called by the simulation in each time step.
                Update the prediction error and perform new predictions.
                Returns next action and new predictions to simulation (prediction just for logging) """
                # update sum of prediction error
                #self._updatePredictionError(actualProximitySensors, additionalSensors[0], boredomPunishment) #, boredom_turn_Punishment, boredom_pos_punishment)
                self.error_sum, self.n = self.updatePredictionError(actualProximitySensors, 
                        additionalSensors[0], # actualLightSensor
                        boredomPunishment,
                        self.lastPrediction,
                        self.error_sum,
                        self.n,
                        additionalSensors[2] # battery level
                        )

                # create input for ANNs
                inputVector = numpy.concatenate((actualProximitySensors, additionalSensors), 0)
                self.lastAction = self._action(inputVector)
                self.lastPrediction = self._predict(inputVector)
                # return new actions
                return self.lastAction, self.lastPrediction


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


        

        def _predict(self, inputVector):
                """ inputs given vector to the prediction network and return proximity sensor prediction """
                input_with_actual_actions = numpy.concatenate((inputVector, self.lastAction), 0)  # lastAction: for prediction network used action computed in this time step
                predictionInput = numpy.array([input_with_actual_actions]).T  # shape size: (number_input x 1)  
                prediction =  self.predictionNetwork.input(predictionInput)
                return prediction.T[0] # returns a vector, not 2d matrix 


        def _action(self, inputVector):
                """ inputs given vector to the action network and returns network's output """
                input_with_last_actions = numpy.concatenate((inputVector, self.lastAction), 0)  # lastAction: for action network used action computed in last time step
                actionInput = numpy.array([input_with_last_actions]).T   # shape size: (number_input x 1)  
                actionOutput = self.actionNetwork.input(actionInput) # CALL WITH 2D MATRIX! Return 2D MATRIX
                return actionOutput.T[0] # return vector


        def evaluate(self):
                #self.fitnessValue = 1 - ((self.error_sum / self.n) /  p.NUMBER_ROBOTS)
                self.fitnessValue = (self.n - self.error_sum) /  (p.MAX_TIME_STEPS_REACHED * p.NUMBER_ROBOTS) 
                return self.fitnessValue


        def mutate(self, rate): 
                """ mutates a copy of this individual and returns it

                Arguments:
                rate -- a real number in [0,1) specifiying the probability for each number in genome to be mutated; should not be much greater than 0.3

                """
                genomeAction = self.actionNetwork.toGenome()
                genomePrediction = self.predictionNetwork.toGenome()

                # mutate
                genomeAction = [x if random.random()>=rate else x + random.uniform(-p.MUTATION_CHANGE, p.MUTATION_CHANGE) for x in genomeAction]
                genomePrediction = [x if random.random()>=rate else x + random.uniform(-p.MUTATION_CHANGE, p.MUTATION_CHANGE) for x in genomePrediction]

                self.actionNetwork.fromGenome(numpy.array(genomeAction))
                self.predictionNetwork.fromGenome(numpy.array(genomePrediction))
                
                # do not need a copy!
                #copy = GeneticIndividual(self.id)
                #copy.actionNetwork.fromGenome(numpy.array(genomeAction))
                #copy.predictionNetwork.fromGenome(numpy.array(genomePrediction))
                # return copy


def sigmoid(x):
    """ returns the value of the sigmoid function evaluated at all elements of x """
    return 1 / (1 + numpy.exp(-x))
    
    
def tanh(x):
    """ returns the value of the sigmoid function evaluated at all elements of x """
    return numpy.tanh(x)
