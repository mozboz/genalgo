from g1.arithmeticgenome import ArithmeticGenome, reader
import random

class PopulationAndSelectionConfig(object):
    def __init__(self, populationSize, dnaLength, startingModifier, numberToCheckForStagnation, stagnationModifierMultiplier,
                 cullStartPercentage, cullEndPercentage, fittestSelectionStartPercentage, fittestSelectionEndPercentage,
                 mutateRandomSelectionWeight, mutateRandomWithPartnerSelectionWeight, mutateRandomStripeWithPartnerSelectionWeight,
                 mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight, stagnationMargin, thresholdModifierScaler,
                 mutateRandomProbability, mutateRandomWithPartnerProbability, mutateRandomStripeWithPartnerProbability,
                 mutateMoveStripeToRandomPlaceWithPartnerProbability, newRandomWeight):

        self.populationSize = populationSize
        self.dnaLength = dnaLength
        self.startingModifier = startingModifier # 0.0001
        self.numberToCheckForStagnation = numberToCheckForStagnation # 20
        self.stagnationModifierMultiplier = stagnationModifierMultiplier # 2
        self.cullStartPercentage = cullStartPercentage # 16%
        self.cullEndPercentage = cullEndPercentage # 32%
        self.fittestSelectionStartPercentage = fittestSelectionStartPercentage # 0%
        self.fittestSelectionEndPercentage = fittestSelectionEndPercentage # 33%
        # The weights that a given mutation method will be chosen
        self.mutateRandomSelectionWeight = mutateRandomSelectionWeight # 1
        self.mutateRandomWithPartnerSelectionWeight = mutateRandomWithPartnerSelectionWeight # 1
        self.mutateRandomStripeWithPartnerSelectionWeight = mutateRandomStripeWithPartnerSelectionWeight # 1
        self.mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight = mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight # 1
        self.newRandomWeight = newRandomWeight # 1
        # The base probability of mutation in each method
        self.mutateRandomProbability = mutateRandomProbability # 0.25
        self.mutateRandomWithPartnerProbability = mutateRandomWithPartnerProbability # 0.25
        self.mutateRandomStripeWithPartnerProbability = mutateRandomStripeWithPartnerProbability # 0.4
        self.mutateMoveStripeToRandomPlaceWithPartnerProbability = mutateMoveStripeToRandomPlaceWithPartnerProbability # 0.5
        
        self.stagnationMargin = stagnationMargin # 0
        self.thresholdModifierScaler = thresholdModifierScaler # 1

        # **** IDEA: Introduce generational modifiers to things so that they can change throughout the population
        # lifecycle. For example, each mutation methodolgy may have a modifier like 1.01 or -1.01 so that it becomes
        # more or less applied during the population's life


class Population(object):

    def __init__(self, log, genomeType, fitnessFunction, populationAndSelectionConfig):
        self.populationAndSelectionConfig = populationAndSelectionConfig
        self.generation = 0
        self.genomeType = genomeType
        self.populationSize = populationAndSelectionConfig.populationSize
        self.population = \
            [Individual(log, genomeType, self.generation, x, length=populationAndSelectionConfig.dnaLength)
             for x in range(1,self.populationSize)
            ]
        self.fitnessFunction = fitnessFunction
        self.dnaLength = populationAndSelectionConfig.dnaLength
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
                return True

            self.newPopulation()

            # if x % 10 == 0:
            #     raw_input("Press Enter to continue...")

        return True


    def evaluate(self):

        r = reader(self.genomeType)

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

        avg_now = self.avgFitness(self.populationAndSelectionConfig.numberToCheckForStagnation)

        self.log.debug("avg now {}, avg before {}, num to check {}, allowed difference {}".format(avg_now, self.avg_previous, self.populationAndSelectionConfig.numberToCheckForStagnation, self.populationAndSelectionConfig.stagnationMargin))

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
            new = Individual(self.log, self.genomeType, self.generation, id, length = self.dnaLength, method="N")
            self.population.append(new)
            self.log.debug("New random added ({})".format(id))

        # Define mutation functions

        def mutateRandom(id):
            mates = random.sample(self.population, 1)
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=mates[0].dna, parentId=mates[0].identifier, method="R")
            new.mutateRandomMutation(self.populationAndSelectionConfig.mutateRandomProbability + self.thresholdModifier)
            self.population.append(new)
            self.log.debug("Mutation R with prob {} ({})".format(self.populationAndSelectionConfig.mutateRandomProbability + self.thresholdModifier, id))

        # All of these are concerned with breeding two individuals together with different strategies

        def mutateRandomWithPartner(id):
            mates = random.sample(self.population, 2)
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=mates[0].dna, parentId=mates[0].identifier, method="S")
            new.mutateBreedWithPartnerRandomSymbol(mates[1].dna, self.populationAndSelectionConfig.mutateRandomWithPartnerProbability + thresholdModification)
            self.population.append(new)
            self.log.debug("Mutation S with prob {} ({})".format(self.populationAndSelectionConfig.mutateRandomWithPartnerProbability + self.thresholdModifier, id))

        def mutateRandomStripeWithPartner(id):
            mates = random.sample(self.population, 2)
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=mates[0].dna, parentId=mates[0].identifier, method="T")
            new.mutateBreedWithPartnerCopyRandomStripeToSamePlace(mates[1].dna, self.populationAndSelectionConfig.mutateRandomStripeWithPartnerProbability + thresholdModification)
            self.population.append(new)
            self.log.debug("Mutation T with prob {} ({})".format(self.populationAndSelectionConfig.mutateRandomStripeWithPartnerProbability + self.thresholdModifier, id))

        def mutateMoveStripeToRandomPlaceWithPartner(id):
            mates = random.sample(self.population, 2)
            new = Individual(self.log, self.genomeType, self.generation, id, dnaString=mates[0].dna, parentId=mates[0].identifier, method="M")
            new.mutateBreedWithPartnerMoveStripeToRandomPlace(mates[1].dna, self.populationAndSelectionConfig.mutateMoveStripeToRandomPlaceWithPartnerProbability + thresholdModification)
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

        finish = False

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

    def __init__(self, log, type, generation, identifier, length = None, dnaString = None, parentId = None, method = None):
        self.type = type

        assert length is not None or dnaString is not None

        if length is not None and dnaString is not None:
            self.dna = dnaString[:]
            assert length == len(dnaString)
            self.length = length

        if length is None and dnaString is not None:
            self.dna = dnaString[:]
            self.length = len(self.dna)

        if length is not None and dnaString is None:
            self.length = length
            self.initRandom()

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

    def initRandom(self):
        genome = self.type()
        allSymbols = genome.symbols.keys()
        self.dna = [random.choice(allSymbols) for x in range(self.length)]

    # threshold = likelihood of each character being swapped for partner's
    def mutateBreedWithPartnerRandomSymbol(self, partnerDna, threshold):
        assert self.length == len(partnerDna)

        self.dna = [self.dna[x] if random.random() > threshold else partnerDna[x] for x in range(self.length)]

    # threshold likelihood of each character being swapped for random one
    def mutateRandomMutation(self, threshold):
        genome = self.type()
        allSymbols = genome.symbols.keys()

        self.dna = [self.dna[x] if random.random() > threshold else random.choice(allSymbols) for x in range(self.length)]

    # threshold is max percent of characters that can be swapped
    def mutateBreedWithPartnerCopyRandomStripeToSamePlace(self, partnerDna, threshold):

        lengthToSwap = int(self.length * threshold * random.random())
        startPoint = random.randrange(0,self.length)

        # print "{} {}".format(startPoint, lengthToSwap)

        self.dna = [partnerDna[x] if x in range(startPoint, startPoint + lengthToSwap) else self.dna[x] for x in range(self.length)]

    def mutateBreedWithPartnerMoveStripeToRandomPlace(self, partnerDna, threshold):

        lengthToSwap = int(self.length * threshold * random.random())
        startPointSource = random.randrange(0,self.length)

        startPointDest = random.randrange(0, self.length)

        if lengthToSwap + startPointDest > self.length:
            lengthToSwap = self.length - startPointDest

        if lengthToSwap + startPointSource > self.length:
            lengthToSwap = self.length - startPointSource

        # print "length {} source {} dest {}".format(lengthToSwap, startPointSource, startPointDest)

        for x in range(0, lengthToSwap):
            self.dna[startPointDest+x] = partnerDna[startPointSource + x]


