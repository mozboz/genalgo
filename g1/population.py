from g1.arithmeticgenome import ArithmeticGenome, Runner
from g1.individual import Individual

import random

class PopulationAndSelectionConfig(object):
    def __init__(self, populationSize, startingModifier, percentToCheckForStagnation, stagnationModifierMultiplier,
                 cullStartPercentage, cullEndPercentage, fittestSelectionStartPercentage, fittestSelectionEndPercentage,
                 mutateRandomGeneMutationSelectionWeight, mutateRandomCopyFromPartnerWithPartnerSelectionWeight, mutateStripeToSamePlaceSelectionWeight,
                 mutateStripeToRandomPlaceSelectionWeight, stagnationMargin, thresholdModifierScaler,
                 mutateRandomGeneMutationProbability, mutateRandomCopyFromPartnerProbability, mutateStripeToSamePlaceProbability,
                 mutateStripeToRandomPlaceProbability, newRandomWeight):

        # Working example:

        # populationConfig = PopulationAndSelectionConfig(60, 0.0001, 0.33, 2, 0.16, 0.32, 0.33, 1, 1, 1, 1, 1, 0, 1, 0.25, 0.25, 0.4, 0.5, 1)

        self.populationSize = populationSize # integer min/max, positive
        self.startingModifier = startingModifier # 0.0001  - float positive 0-1
        self.percentToCheckForStagnation = percentToCheckForStagnation # 33% - float 0-1
        self.stagnationModifierMultiplier = stagnationModifierMultiplier # 2 - float small (0-100?)
        self.cullStartPercentage = cullStartPercentage # 16% float 0-1
        self.cullEndPercentage = cullEndPercentage # 32% float 0-1
        self.fittestSelectionStartPercentage = fittestSelectionStartPercentage # 0% float 0-1
        self.fittestSelectionEndPercentage = fittestSelectionEndPercentage # 33% float 0-1
        # The weights that a given mutation method will be chosen
        self.mutateRandomGeneMutationSelectionWeight = mutateRandomGeneMutationSelectionWeight # 1 positive 0-1
        self.mutateRandomGeneMutationProbability = mutateRandomGeneMutationProbability # 0.25 float 0-1

        self.mutateRandomCopyFromPartnerSelectionWeight = mutateRandomCopyFromPartnerWithPartnerSelectionWeight # 1 positive 0-1
        self.mutateRandomCopyFromPartnerProbability = mutateRandomCopyFromPartnerProbability # 0.25 float 0-1

        self.newRandomWeight = newRandomWeight # 1 positive 0-1

        self.mutateStripeToSamePlaceSelectionWeight = mutateStripeToSamePlaceSelectionWeight # 1 positive 0-1
        self.mutateStripeToSamePlaceProbability = mutateStripeToSamePlaceProbability # 0.4 float 0-1

        self.mutateStripeToRandomPlaceSelectionWeight = mutateStripeToRandomPlaceSelectionWeight # 1 positive 0-1
        self.mutateStripeToRandomPlaceProbability = mutateStripeToRandomPlaceProbability # 0.5 float 0-1
        # The base probability of mutation in each method

        self.stagnationMargin = stagnationMargin # 0
        self.thresholdModifierScaler = thresholdModifierScaler # 1

        # **** IDEA: Introduce generational modifiers to things so that they can change throughout the population
        # lifecycle. For example, each mutation methodolgy may have a modifier like 1.01 or -1.01 so that it becomes
        # more or less applied during the population's life


class Population(object):

    def __init__(self, log, genomeType, genomeParams, fitnessFunction, populationAndSelectionConfig, population=None):
        self.populationAndSelectionConfig = populationAndSelectionConfig
        self.generation = 0
        self.genomeType = genomeType
        self.genomeParams = genomeParams
        self.populationSize = populationAndSelectionConfig.populationSize
        if population is None:
            self.population = [Individual(log, genomeType, self.generation, x, params=self.genomeParams) for x in range(1,self.populationSize)]
        else:
            self.population = population
        self.fitnessFunction = fitnessFunction
        self.avg_previous = 0
        self.thresholdModifier = populationAndSelectionConfig.startingModifier
        self.cullCount = 0

        self.log = log

    def iterateNoInput(self, iterations = 1, printIterations = True):

        for x in range(0,iterations):
            self.evaluateNoInput()

            if printIterations:
                print self.dump(10)

            if self.finished():
                return False

            self.newPopulation()

            # if x % 10 == 0:
            #     raw_input("Press Enter to continue...")

        return True

    def evaluateNoInput(self):

        r = Runner()

        for x in [x for x in self.population if x.result is None]:
            x.result = r.run(x.dna)
            x.fitness = self.fitness(x.result)

        self.population.sort()


    def iterateTestSet(self, testSet, iterations = 1, printIterations = True):

        for x in range(0,iterations):
            self.evaluateTestSet(testSet)

            if printIterations:
                print self.dump(10)

            if self.finished():
                return False

            self.newPopulation()

            # if x % 10 == 0:
            #     raw_input("Press Enter to continue...")

        return True


    def evaluateTestSet(self, testSet):

        r = Runner(self.genomeType)

        for i in self.population:
            fitness = 0
            for testValue in testSet:
                i.result = r.run(individual=i, startValue=testValue)
                fitness += self.fitness(i.result, testValue)

            i.fitness = fitness

        self.population.sort()




    def newPopulation(self):

        # Check stagnation

        # To overcome stagnation (where the population does not reach a solution, but gets so close that all individuals
        # are very fit but not able to evolve further), there are two methods:

        # 1) Increase the 'thresholdModifier' which modifies the chance that mutation will occur using any of the
        #    mutation strategies

        # 2) If the thresholdModifier keeps getting increased and the population is still stagnated, then kill off
        #    some/all of the population in the hope that that will introduce some new methodology/randomness

        numberToCheckForStagnation = int(len(self.population) * self.populationAndSelectionConfig.percentToCheckForStagnation)
        avg_now = self.avgFitness(numberToCheckForStagnation)

        self.log.debug("avg now {}, avg before {}, num to check {}, allowed difference {}".format(avg_now, self.avg_previous, numberToCheckForStagnation, self.populationAndSelectionConfig.stagnationMargin))

        if abs(avg_now - self.avg_previous) <= self.populationAndSelectionConfig.stagnationMargin:
            before = self.thresholdModifier
            self.thresholdModifier = min(1, self.thresholdModifier * self.populationAndSelectionConfig.stagnationModifierMultiplier)
            self.log.debug("Modifier Increase. Before {}, multiplier {}, after {}".format(before, self.populationAndSelectionConfig.stagnationModifierMultiplier, self.thresholdModifier))
        else:
            self.thresholdModifier = self.populationAndSelectionConfig.startingModifier
            self.avg_previous = avg_now

        # 1 is arbitrary value that modifier must reach for cull to take effect

        if self.thresholdModifier == 1:
            self.cullCount += 1

            cullStart = int(len(self.population) * self.populationAndSelectionConfig.cullStartPercentage)
            cullEnd = int(len(self.population) * self.populationAndSelectionConfig.cullEndPercentage)

            self.log.debug("Cull initiated @ gen {}. Pop size: {}. Cull start, end: {}, {}".format(self.generation, len(self.population), cullStart, cullEnd))

            self.population = self.population[cullStart:cullEnd]

            self.log.debug("Culled #{}. New pop size {}".format(self.cullCount, len(self.population)))
        else:

            fittestSelectionStart = int(len(self.population) * self.populationAndSelectionConfig.fittestSelectionStartPercentage)
            fittestSelectionEnd = int(len(self.population) * self.populationAndSelectionConfig.fittestSelectionEndPercentage)

            self.log.debug("Normal selection from {} to {}".format(fittestSelectionStart, fittestSelectionEnd))
            self.population = self.population[fittestSelectionStart:fittestSelectionEnd]


        #----Rebuild population to same level by weighted selection between strategies


        # scale the threshold modifier by some value to increase/decrease its effectiveness
        thresholdModification = self.thresholdModifier * self.populationAndSelectionConfig.thresholdModifierScaler

        # Add a new completely random individual
        def newRandom(parents):
            new = Individual(self.log, self.genomeType, self.generation, "", params=self.genomeParams)
            return (new.dna, [])

        # Define mutation functions

        genome = self.genomeType()

        mutationWeights = { 
            "R" : self.populationAndSelectionConfig.mutateRandomGeneMutationSelectionWeight,
            "S" : self.populationAndSelectionConfig.mutateRandomCopyFromPartnerSelectionWeight,
            "T" : self.populationAndSelectionConfig.mutateStripeToSamePlaceSelectionWeight,
            "M" : self.populationAndSelectionConfig.mutateStripeToRandomPlaceSelectionWeight,
            "N" : self.populationAndSelectionConfig.newRandomWeight
        }

        mutationProbabilities = {
            "R" : self.populationAndSelectionConfig.mutateRandomGeneMutationProbability + self.thresholdModifier,
            "S" : self.populationAndSelectionConfig.mutateRandomCopyFromPartnerProbability + self.thresholdModifier,
            "T" : self.populationAndSelectionConfig.mutateStripeToSamePlaceProbability + self.thresholdModifier,
            "M" : self.populationAndSelectionConfig.mutateStripeToRandomPlaceProbability + self.thresholdModifier,
            "N" : 0  # this value not used
        }


        idCounter = 1

        while(len(self.population) < self.populationAndSelectionConfig.populationSize):

            parents = random.sample(self.population, 2)
            newDna, parentsUsed, methodUsed = genome.newIndividualByRandomMutation(mutationWeights, mutationProbabilities, self.genomeParams, parents)
            parentString = ",".join([p.identifier for p in parents])
            parentString = parentString[:250]
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=newDna, parentId=parentString, method=methodUsed)
            self.population.append(new)
            idCounter += 1

        assert len(self.population) == self.populationSize

        self.log.debug("end of gen " + str(self.generation))

        self.generation += 1

    def fitness(self, actual, input=0):
        return abs(self.fitnessFunction(input) - actual)

    def dump(self, top = None):
        if top is None:
            top = len(self.population)

        msg = ""
        for x in self.population[0:top]:
            msg += "DNA: {}, Output: {}, Fitness: {}, Age: {}, Id: {}".format("".join(x.dna), x.result, x.fitness, self.generation - x.generationBorn, x.identifier)
            msg += "\n"

        msg += "Avg top 10: {} Gen {}".format(self.avgFitness(10), self.generation) + "\n"

        return msg

    # assumes group is sorted
    def finished(self):
        return self.population[0].fitness == 0

    def avgFitness(self, n):
        i = [p.fitness for p in self.population[0:n]]
        return sum(i) / n

    def avgAge(self, n):
        i = [self.generation - p.generationBorn for p in self.population[0:n]]
        return sum(i) / n

