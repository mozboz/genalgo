
from genomebase import GenomeBase
import random

class Runner(object):

    # this language is wrong, genome is the class, dna is the string
    def __init__(self):
        self.genome = ArithmeticGenome()

    # steps through dna from start to end, returns final information left in this cell
    def run(self, dna=None, individual=None, startValue = None):
        if individual is not None:
            dna = individual.dna

        self.operator = self.genome.getOperatorFunction('O')
        self.operand = None

        if startValue is None:
            self.information = 0.0
        else:
            self.information = startValue

        self.numberBuilderString = ""
        self.numberHasDecimalPlace = False
        self.isNegativeNumber = False
        self.doing = self.genome.OPERATOR

        for symbol in dna:
            self.processSymbol(symbol)

        # self.processSymbol(ArithmeticGenome.END_MARKER)

        # if ending on a number, process it
        if self.doing == ArithmeticGenome.NUMBER:
            self.finishNumber()
            self.runOperatorOnNumber()

        return self.information

    def processSymbol(self, symbol):

        type = self.genome.getType(symbol)

        if type == ArithmeticGenome.NUMBER:

            self.appendNumber(symbol)
            self.doing = ArithmeticGenome.NUMBER

        elif type == ArithmeticGenome.OPERATOR:

            if self.doing == ArithmeticGenome.NUMBER:
                self.finishNumber()
                self.runOperatorOnNumber()
                self.setOperator(symbol)
                self.doing = ArithmeticGenome.OPERATOR

            elif self.doing == ArithmeticGenome.OPERATOR:
                self.setOperator(symbol)

        else:
            assert False, "Unknown Type"


    def appendNumber(self, symbol):

        # decimal place
        if symbol == ".":
            if not self.numberHasDecimalPlace:
                self.numberBuilderString += symbol
                self.numberHasDecimalPlace = True

        # negative number
        elif symbol == "N":
            self.isNegativeNumber = not self.isNegativeNumber

        else:
            self.numberBuilderString += symbol

    def finishNumber(self):
        try:
            v = float(self.numberBuilderString)
            if self.isNegativeNumber:
                v = -v
            self.operand = v

        except ValueError:
            self.operand = 0

        self.numberBuilderString = ""
        self.numberHasDecimalPlace = False
        self.isNegativeNumber = False

    def setOperator(self, symbol):
        self.operator = self.genome.getOperatorFunction(symbol)

    def runOperatorOnNumber(self):
        try:
            self.information = self.operator(self.information, self.operand)
        except ZeroDivisionError:
            self.information = 0



# Includes random creation and mutation functions
class ArithmeticGenome(GenomeBase):

    # Types of symbols
    NUMBER = 1          # literal numbers, negative and decimal point symbols
    OPERATOR = 2        # callable functions to operate on one or two numbers

    def __init__(self):
        super(ArithmeticGenome, self).__init__()
        self.registerSymbols( {
            '0' : (self.NUMBER, "0") ,
            '1' : (self.NUMBER, "1") ,
            '2' : (self.NUMBER, "2") ,
            '3' : (self.NUMBER, "3") ,
            '4' : (self.NUMBER, "4") ,
            '5' : (self.NUMBER, "5") ,
            '6' : (self.NUMBER, "6") ,
            '7' : (self.NUMBER, "7") ,
            '8' : (self.NUMBER, "8") ,
            '9' : (self.NUMBER, "9") ,
            '.' : (self.NUMBER, ".") ,
            'N' : (self.NUMBER, "N") ,

            '+' : (self.OPERATOR, lambda x,y: x + y) ,
            '*' : (self.OPERATOR, lambda x,y: x * y) ,
            '-' : (self.OPERATOR, lambda x,y: x - y) ,
            '/' : (self.OPERATOR, lambda x,y: x / y) ,
            'O' : (self.OPERATOR, lambda x,y: y)
        })

        self.allSymbols = self.symbols.keys()


    def getOperatorFunction(self, symbol):
        return self.symbols[symbol][1]

    # Methods that create new dnaStrings must all follow the same interface:

    # parameters:
    # : parents - an array of two parents
    # params - a set of configuration parameters for this genome
    # : threshold - a float 0-1 that dictates how much change or randomness should be introduced

    # return value, tuple of:
    # : new dna
    # : array of parents used


    def createIndividual(self, params, parents, threshold):
        newDna = [random.choice(self.allSymbols) for x in range(params['length'])]
        return newDna, []

     # threshold likelihood of each character being swapped for random one
    def mutateRandomGeneMutation(self, params, parents, threshold):
        dna = parents[0].dna
        newDna = [dna[x] if random.random() > threshold else random.choice(self.allSymbols) for x in range(len(dna))]
        return newDna, parents[0:1]

    # return new dna same length as partner 1, with each character randomly selected from 1 or 2 weighted by threshold
    def mutateRandomCopyFromPartner(self, params, parents, threshold):
        newDna = [parents[0].dna[x] if random.random() > threshold else parents[1].dna[x] for x in range(len(parents[0].dna))]
        return newDna, parents

    # threshold is max percent of characters that can be swapped
    def mutateStripeToSamePlace(self, params, parents, threshold):

        lengthToSwap = int(len(parents[0].dna) * threshold * random.random())
        startPoint = random.randrange(0,len(parents[0].dna))

        # print "{} {}".format(startPoint, lengthToSwap)

        newDna = [parents[1].dna[x] if x in range(startPoint, startPoint + lengthToSwap) else parents[0].dna[x] for x in range(len(parents[0].dna))]
        return newDna, parents

    # takes a random length piece of partner2 and moves it to a random place on partner 1
    def mutateStripeToRandomPlace(self, params, parents, threshold):

        lengthToSwap = int(len(parents[1].dna) * threshold * random.random())
        startPointSource = random.randrange(0,len(parents[1].dna))

        startPointDest = random.randrange(0, len(parents[0].dna))

        # length might overrun new dna
        if lengthToSwap + startPointDest > len(parents[0].dna):
            lengthToSwap = len(parents[0].dna) - startPointDest

        # length and start point to read form are random, so they could read off end of source, and source could be shorter
        if lengthToSwap + startPointSource > len(parents[1].dna):
            lengthToSwap = len(parents[1].dna) - startPointSource

        # print "length {} source {} dest {}".format(lengthToSwap, startPointSource, startPointDest)

        newDna = parents[0].dna[:]

        for x in range(0, lengthToSwap):
            newDna[startPointDest+x] = parents[1].dna[startPointSource + x]

        return newDna, parents

    def newIndividualByRandomMutation(self, mutationWeights, mutationProbabilities, params, parents):

        mutationMethods = {"R" : self.mutateRandomGeneMutation,
                           "S" : self.mutateRandomCopyFromPartner,
                           "T" : self.mutateStripeToSamePlace,
                           "M" : self.mutateStripeToRandomPlace,
                           "N" : self.createIndividual}

        methodId = self.weightedChoice(mutationWeights)

        newDna, parents = mutationMethods[methodId](params, parents, mutationProbabilities[methodId])

        return newDna, parents, methodId


    def weightedChoice(self, choices):

        total = sum(choices.values())
        selectionPoint = random.uniform(0,total)
        pointer = 0
        for key, value in choices.iteritems():
            pointer += value
            if pointer >= selectionPoint:
                return key
        assert False, "Should not reach here"

