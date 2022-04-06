import numpy as np
import random
from genetic_individual import GeneticIndividual
from multiple_genetic_individual import MultipleGeneticIndividual
import parameters as p
from simulation import Simulation
import arcade
import copy

class GeneticPopulation(list):
    """ represents a population in terms of evolution """

    def __init__(self, generationNumber):#,amountProxSensors, amountAdditionalSensors, amountActions, amountHiddenAction, amountHiddenPrediction, activationFunctionAction, activationFunctionPrediction):
        """ initializes a population """
        self.generation = generationNumber

    def initStartPopulation(self, updatePredictionError):
        for indivId in range(p.POPULATION_SIZE):
            if p.NUMBER_ROBOTS == 1:
                self.append( GeneticIndividual(indivId, updatePredictionError) )
            else:
                self.append( MultipleGeneticIndividual(indivId, updatePredictionError) )

    def selectKing(self):
        """ selects individuum with best fitness and remove this from population (just for recombination) """
        king = self[0]
        for indiv in self:
            if indiv.fitnessValue >= king.fitnessValue:
                king = indiv
        #self.remove(king)
        return copy.deepcopy(king) # deep copy, otherwise king will be changed in actual population afterwards, because of pythons strange memory management (see mutable, immutable)

    def proportionateSelection(self):
        """ selects one individual of actual population with a proportional selection (roulette wheel) based on fitness values.
            Selection probability proportioonal to individuals fitness values.
            Returns a copy of that selected individual to not change the individual in actual population """
        _max = sum([individual.fitnessValue for individual in self])
        selection_probs = [individual.fitnessValue/_max for individual in self]
        return copy.deepcopy(self[np.random.choice(len(self), p=selection_probs)]) # deep copy, otherwise king will be changed in actual population afterwards, because of pythons strange memory management (see mutable, immutable)


    def evaluate(self):
        """ Run simulation for each individual in population """
        
        simulation = Simulation(p.SCREEN_TITLE, p.UPDATE_RATE, self, self.generation)
        simulation.setup()
        arcade.run()
        
    def addIndividual(self, indiv):
        """ add individual to population with the new id """
        indiv.updateId(len(self))
        self.append(indiv)

    def checkForTermination(self):
        """ checks if evolution reached termination conditions """
        for indiv in self:
            if indiv.fitnessValue >= p.TERMINATION_PARA_FITNESS or self.generation >= p.MAX_GENERATION_REACHED:
                return True
        return False





