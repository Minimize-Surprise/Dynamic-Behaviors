import random
import numpy
from action_network import ActionNetwork
from prediction_network import PredictionNetwork
import parameters as p
import queue



class SwarmMember:



    def __init__(self, member_id):

        self.id = member_id
        self.amountProxSensors = p.SENSOR_NUMBER
        self.amountAdditionalSensors = p.NUMBER_OF_ADDITIONAL_SENSORS
        self.amountActions = p.NUMBER_ACTIONS
        self.amountHiddenAction = p.AMOUNT_HIDDEN_ACTION
        self.amountHiddenPrediction = p.AMOUNT_HIDDEN_PREDICTION


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
        self.lastPrediction = numpy.random.random(p.AMOUNT_OUTPUT_PREDICTION)
        self.lastAction = numpy.random.random(self.amountActions)

    

    def _predict(self, inputVector):
        """ inputs given vector to the prediction network and return proximity sensor prediction """
        input_with_actual_actions = numpy.concatenate((inputVector, self.lastAction), 0)  # lastAction: for prediction network used action computed in this time step
        predictionInput = numpy.array([input_with_actual_actions]).T  # shape size: (number_input x 1)  
        prediction =  self.predictionNetwork.input(predictionInput)
        self.lastPrediction = prediction.T[0]
        return self.lastPrediction  # returns a vector, not 2d matrix 


    def _action(self, inputVector):
        """ inputs given vector to the action network and returns network's output """
        input_with_last_actions = numpy.concatenate((inputVector, self.lastAction), 0)  # lastAction: for action network used action computed in last time step
        actionInput = numpy.array([input_with_last_actions]).T   # shape size: (number_input x 1)  
        actionOutput = self.actionNetwork.input(actionInput) # CALL WITH 2D MATRIX! Return 2D MATRIX
        self.lastAction = actionOutput.T[0]
        return self.lastAction # return vector


def sigmoid(x):
    """ returns the value of the sigmoid function evaluated at all elements of x """
    return 1 / (1 + numpy.exp(-x))
    
    
def tanh(x):
    """ returns the value of the sigmoid function evaluated at all elements of x """
    return numpy.tanh(x)

















