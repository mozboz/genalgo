from g1.arithmeticgenome import ArithmeticGenome, reader
import random


class Population(object):

    def __init__(self, log, populationSize, dnaLength, genomeType, fitnessFunction):

        self.generation = 0
        self.genomeType = genomeType
        self.population = [Individual(genomeType, self.generation, x, length=dnaLength) for x in range(1,populationSize)]
        self.fitnessFunction = fitnessFunction
        self.dnaLength = dnaLength
        self.avg_previous = 0
        self.modifier = 0.0001
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

        return True



    def evaluate(self):

        r = reader(self.genomeType)

        for x in [x for x in self.population if x.result is None]:
            x.result = r.run(x.dna)
            x.fitness = self.fitness(x.result)

        self.population.sort()

    def newPopulation(self):

        # Check stagnation

        avg_now = self.avgFitness(20)

        if avg_now == self.avg_previous:
            self.modifier = min(1, self.modifier * 2)
            self.log.debug("Modifier: {}".format(self.modifier))
        else:
            self.modifier = 0.0001
            self.avg_previous = avg_now

        ## At this point select 20 from 60

        if self.modifier == 1:
            self.cullCount += 1
            self.log.debug("Cull {}. Avg age top 20 {}".format(self.cullCount, self.avgAge(20)))
            self.log.debug([self.generation - x.generationBorn for x in self.population[0:20]].__repr__())

            # assume stagnation and inbreeding happened, do some pruning

            # always taking the top guy leads to stagnation. kill off the top n guys

            killTop = 10

            self.population = self.population[killTop:20]
            for x in range(0,20 - killTop):
                self.population.append(Individual(self.genomeType, self.generation, x, length=self.dnaLength, method="N"))

        else:

            self.population = self.population[0:20]


        assert len(self.population) == 20

        ## Append a new 40
        newPop = []


        # Randomly mutates a random selection
        for x in range(0,10):
            mates = random.sample(self.population, 1)
            new = Individual(self.genomeType, self.generation, x+20, dnaString=mates[0].dna, parentId=mates[0].identifier, method="R")
            new.mutateRandomMutation(0.25 + self.modifier)
            newPop.append(new)

        # All of these are concerned with breeding two individuals together with different strategies

        for x in range(0,10):
            mates = random.sample(self.population, 2)
            new = Individual(self.genomeType, self.generation, x+30, dnaString=mates[0].dna, parentId=mates[0].identifier, method="S")
            new.mutateBreedWithPartnerRandomSymbol(mates[1].dna, 0.25 + self.modifier)
            newPop.append(new)

        for x in range(0,10):
            mates = random.sample(self.population, 2)
            new = Individual(self.genomeType, self.generation, x+40, dnaString=mates[0].dna, parentId=mates[0].identifier, method="T")
            new.mutateBreedWithPartnerRandomStrip(mates[1].dna, 0.4 + self.modifier)
            newPop.append(new)

        for x in range(0,10):
            mates = random.sample(self.population, 2)
            new = Individual(self.genomeType, self.generation, x+50, dnaString=mates[0].dna, parentId=mates[0].identifier, method="M")
            new.mutateBreedWithPartnerMoveStrip(mates[1].dna, 0.5 + self.modifier)
            newPop.append(new)


        self.population.extend(newPop)

        assert len(self.population) == 60

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



class Individual(object):

    def __init__(self, type, generation, identifier, length = None, dnaString = None, parentId = None, method = None):
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
    def mutateBreedWithPartnerRandomStrip(self, partnerDna, threshold):

        lengthToSwap = int(self.length * threshold * random.random())
        startPoint = random.randrange(0,self.length)

        # print "{} {}".format(startPoint, lengthToSwap)

        self.dna = [partnerDna[x] if x in range(startPoint, startPoint + lengthToSwap) else self.dna[x] for x in range(self.length)]

    def mutateBreedWithPartnerMoveStrip(self, partnerDna, threshold):

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


