from g1.arithmeticgenome import ArithmeticGenome, Runner
import random

class PopulationAndSelectionConfig(object):
    def __init__(self, populationSize, startingModifier, percentToCheckForStagnation, stagnationModifierMultiplier,
                 cullStartPercentage, cullEndPercentage, fittestSelectionStartPercentage, fittestSelectionEndPercentage,
                 mutateRandomSelectionWeight, mutateRandomWithPartnerSelectionWeight, mutateRandomStripeWithPartnerSelectionWeight,
                 mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight, stagnationMargin, thresholdModifierScaler,
                 mutateRandomProbability, mutateRandomWithPartnerProbability, mutateBreedWithPartnerCopyRandomStripeToSamePlace,
                 mutateMoveStripeToRandomPlaceWithPartnerProbability, newRandomWeight):

        self.populationSize = populationSize # integer min/max, positive
        self.startingModifier = startingModifier # 0.0001  - float positive 0-1
        self.percentToCheckForStagnation = percentToCheckForStagnation # 33% - float 0-1
        self.stagnationModifierMultiplier = stagnationModifierMultiplier # 2 - float small (0-100?)
        self.cullStartPercentage = cullStartPercentage # 16% float 0-1
        self.cullEndPercentage = cullEndPercentage # 32% float 0-1
        self.fittestSelectionStartPercentage = fittestSelectionStartPercentage # 0% float 0-1
        self.fittestSelectionEndPercentage = fittestSelectionEndPercentage # 33% float 0-1
        # The weights that a given mutation method will be chosen
        self.mutateRandomSelectionWeight = mutateRandomSelectionWeight # 1 positive 0-1
        self.mutateRandomWithPartnerSelectionWeight = mutateRandomWithPartnerSelectionWeight # 1 positive 0-1
        self.mutateRandomStripeWithPartnerSelectionWeight = mutateRandomStripeWithPartnerSelectionWeight # 1 positive 0-1
        self.mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight = mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight # 1 positive 0-1
        self.newRandomWeight = newRandomWeight # 1 positive 0-1
        # The base probability of mutation in each method
        self.mutateRandomProbability = mutateRandomProbability # 0.25 float 0-1
        self.mutateRandomWithPartnerProbability = mutateRandomWithPartnerProbability # 0.25 float 0-1
        self.mutateBreedWithPartnerCopyRandomStripeToSamePlace = mutateBreedWithPartnerCopyRandomStripeToSamePlace # 0.4 float 0-1
        self.mutateMoveStripeToRandomPlaceWithPartnerProbability = mutateMoveStripeToRandomPlaceWithPartnerProbability # 0.5 float 0-1
        
        self.stagnationMargin = stagnationMargin # 0
        self.thresholdModifierScaler = thresholdModifierScaler # 1

        # **** IDEA: Introduce generational modifiers to things so that they can change throughout the population
        # lifecycle. For example, each mutation methodolgy may have a modifier like 1.01 or -1.01 so that it becomes
        # more or less applied during the population's life


class Population(object):

    def __init__(self, log, genomeType, genomeParams, fitnessFunction, populationAndSelectionConfig):
        self.populationAndSelectionConfig = populationAndSelectionConfig
        self.generation = 0
        self.genomeType = genomeType
        self.genomeParams = genomeParams
        self.populationSize = populationAndSelectionConfig.populationSize
        self.population = [Individual(log, genomeType, self.generation, x, params=self.genomeParams) for x in range(1,self.populationSize)]
        self.fitnessFunction = fitnessFunction
        self.avg_previous = 0
        self.thresholdModifier = populationAndSelectionConfig.startingModifier
        self.cullCount = 0

        self.log = log

    def iterate(self, iterations = 1, printIterations = True):

        for x in range(0,iterations):
            self.evaluate()

            if printIterations:
                print self.dump(10)

            if self.finished():
                return False

            self.newPopulation()

            # if x % 10 == 0:
            #     raw_input("Press Enter to continue...")

        return True

    def evaluate(self):

        r = Runner(self.genomeType)

        for x in [x for x in self.population if x.result is None]:
            x.result = r.run(x.dna)
            x.fitness = self.fitness(x.result)

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
        def newRandom(id):
            new = Individual(self.log, self.genomeType, self.generation, id, params = self.genomeParams, method="N")
            self.population.append(new)
            self.log.debug("New random added ({})".format(id))

        # Define mutation functions

        genome = self.genomeType()

        def mutateRandom(id):
            mates = random.sample(self.population, 1)
            newDna = genome.mutateRandomMutation(mates[0].dna, self.populationAndSelectionConfig.mutateRandomProbability + self.thresholdModifier)
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=newDna, parentId=mates[0].identifier, method="R")
            self.population.append(new)
            self.log.debug("Mutation R with prob {} ({})".format(self.populationAndSelectionConfig.mutateRandomProbability + self.thresholdModifier, id))

        # All of these are concerned with breeding two individuals together with different strategies

        def mutateRandomWithPartner(id):
            mates = random.sample(self.population, 2)
            newDna = genome.mutateBreedWithPartnerRandomSymbol(mates[0].dna, mates[1].dna, self.populationAndSelectionConfig.mutateRandomWithPartnerProbability + thresholdModification)
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=newDna, parentId=mates[0].identifier, method="S")
            self.population.append(new)
            self.log.debug("Mutation S with prob {} ({})".format(self.populationAndSelectionConfig.mutateRandomWithPartnerProbability + self.thresholdModifier, id))

        def mutateRandomStripeWithPartner(id):
            mates = random.sample(self.population, 2)
            newDna = genome.mutateBreedWithPartnerCopyRandomStripeToSamePlace(mates[0].dna, mates[1].dna, self.populationAndSelectionConfig.mutateBreedWithPartnerCopyRandomStripeToSamePlace + thresholdModification)
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=newDna, parentId=mates[0].identifier, method="T")
            self.population.append(new)
            self.log.debug("Mutation T with prob {} ({})".format(self.populationAndSelectionConfig.mutateBreedWithPartnerCopyRandomStripeToSamePlace + self.thresholdModifier, id))

        def mutateMoveStripeToRandomPlaceWithPartner(id):
            mates = random.sample(self.population, 2)
            newDna = genome.mutateBreedWithPartnerMoveStripeToRandomPlace(mates[0].dna, mates[1].dna, self.populationAndSelectionConfig.mutateMoveStripeToRandomPlaceWithPartnerProbability + thresholdModification)
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=newDna, parentId=mates[0].identifier, method="M")
            self.population.append(new)
            self.log.debug("Mutation M with prob {} ({})".format(self.populationAndSelectionConfig.mutateMoveStripeToRandomPlaceWithPartnerProbability + self.thresholdModifier, id))


        mutationWeights = {mutateRandom : self.populationAndSelectionConfig.mutateRandomSelectionWeight,
                           mutateRandomWithPartner: self.populationAndSelectionConfig.mutateRandomWithPartnerSelectionWeight,
                           mutateRandomStripeWithPartner : self.populationAndSelectionConfig.mutateRandomStripeWithPartnerSelectionWeight,
                           mutateMoveStripeToRandomPlaceWithPartner : self.populationAndSelectionConfig.mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight,
                           newRandom : self.populationAndSelectionConfig.newRandomWeight}

        idCounter = 1

        while(len(self.population) < self.populationAndSelectionConfig.populationSize):
            f = self.weightedChoice(mutationWeights)
            f(idCounter)
            idCounter += 1

        assert len(self.population) == self.populationSize

        self.generation += 1

    def fitness(self, actual):
        return abs(self.fitnessFunction(0) - actual)

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

    def weightedChoice(self, choices):
        total = sum(choices.values())
        selectionPoint = random.uniform(0,total)
        pointer = 0
        for key, value in choices.iteritems():
            pointer += value
            if pointer >= selectionPoint:
                return key
        assert False, "Should not reach here"


class Individual(object):

    def __init__(self, log, type, generation, identifier, params = None, dnaString = None, parentId = None, method = None):

        # these specific to the type, need to be refactored out:
        # length = None, dnaString = None

        # dnaString should be replaced with 'value' allowing new value to be passed in
        self.genome = type()

        #either params are provided to setup a new individual, or dnaString is provided
        assert (params is None) != (dnaString is None)

        if params is None and dnaString is not None:
            self.dna = dnaString[:]

        if params is not None and dnaString is None:
            self.dna = self.genome.createIndividual(params)

        self.fitness = None
        self.result = None
        self.generationBorn = generation
        self.identifier = "C{}:{}".format(generation, identifier)

        if method is not None:
            self.identifier += "{}".format(method)

        if parentId is not None:
            self.identifier += "({})".format(parentId)

    def __lt__(self, other):
         return self.fitness < other.fitness
