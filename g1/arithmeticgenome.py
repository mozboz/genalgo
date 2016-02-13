
from genomebase import GenomeBase
import random

# Includes random creation and mutation functions
class ArithmeticGenome(GenomeBase):

    # Types of symbols
    NUMBER = 1          # literal numbers, negative and decimal point symbols
    OPERATOR = 2        # callable functions to operate on one or two numbers
    INSTRUCTION = 3     # instructions that should be immediately executed

    def store(self, key):
        def s():
            self.storage[key] = self.information
        return s

    def retrieve(self, key):
        def r():
            if self.storage.has_key(key):
                # if was in the middle of number, then it's lost
                if self.doing == ArithmeticGenome.NUMBER:
                    self.finishNumber()
                self.operand = self.storage[key]
                # put in number mode because there is a number ready
                self.doing = ArithmeticGenome.NUMBER
            # if the key is not set, do nothing
        return r

    def __init__(self):
        # iniitialisation settings are purposely unset/invalid
        self.operator = None
        self.operand = None
        self.information = 0.0
        self.numberBuilderString = ""
        self.numberHasDecimalPlace = False
        self.isNegativeNumber = False
        self.doing = None


        self.storage = {}
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
            '>' : (self.INSTRUCTION, self.store('A')),
            '<' : (self.INSTRUCTION, self.retrieve('A')),
            'O' : (self.OPERATOR, lambda x,y: y,),
            'F' : (self.OPERATOR, lambda x,y: x if y > 0 else 0)
        })

        self.allSymbols = self.symbols.keys()

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
        if self.numberBuilderString:
            try:
                v = float(self.numberBuilderString)
                if self.isNegativeNumber:
                    v = -v
                self.operand = v

            except ValueError:
                self.operand = 0

        else:
            # possibility that this can get called with number characters like '.' and 'N' but no digits, so check
            # for a valid number.
            if self.operand is None:
                self.operand = 0.0

        self.numberBuilderString = ""
        self.numberHasDecimalPlace = False
        self.isNegativeNumber = False

    def setOperator(self, symbol):
        self.operator = self.getFunction(symbol)

    def runOperatorOnNumber(self):
        try:
            self.information = self.operator(self.information, self.operand)
        except (ZeroDivisionError, OverflowError):
            self.information = 0

    def runInstruction(self, symbol):
        self.getFunction(symbol)()


    def getFunction(self, symbol):
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
        return newDna, 0

     # threshold likelihood of each character being swapped for random one
    def mutateRandomGeneMutation(self, params, parents, threshold):
        dna = parents[0].dna
        newDna = [dna[x] if random.random() > threshold else random.choice(self.allSymbols) for x in range(len(dna))]
        return newDna, 1

    # return new dna same length as partner 1, with each character randomly selected from 1 or 2 weighted by threshold
    def mutateRandomCopyFromPartner(self, params, parents, threshold):
        newDna = [parents[0].dna[x] if random.random() > threshold else parents[1].dna[x] for x in range(len(parents[0].dna))]
        return newDna, 2

    # threshold is max percent of characters that can be swapped
    def mutateStripeToSamePlace(self, params, parents, threshold):

        lengthToSwap = int(len(parents[0].dna) * threshold * random.random())
        startPoint = random.randrange(0,len(parents[0].dna))

        # print "{} {}".format(startPoint, lengthToSwap)

        newDna = [parents[1].dna[x] if x in range(startPoint, startPoint + lengthToSwap) else parents[0].dna[x] for x in range(len(parents[0].dna))]
        return newDna, 2

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

        return newDna, 2

    def newIndividualByRandomMutation(self, mutationWeights, mutationProbabilities, params, parents):

        newDna = parents[0].dna

        # This critically does not allow new dna to be identical to parent
        # Run while dna is same as either parent
        while [p for p in parents if p.dna == newDna]:

            mutationMethods = {"R" : self.mutateRandomGeneMutation,
                               "S" : self.mutateRandomCopyFromPartner,
                               "T" : self.mutateStripeToSamePlace,
                               "M" : self.mutateStripeToRandomPlace,
                               "N" : self.createIndividual}

            methodId = self.weightedChoice(mutationWeights)

            newDna, parentsUsed = mutationMethods[methodId](params, parents, mutationProbabilities[methodId])

        return newDna, parentsUsed, methodId


    def weightedChoice(self, choices):

        total = sum(choices.values())
        selectionPoint = random.uniform(0,total)
        pointer = 0
        for key, value in choices.iteritems():
            pointer += value
            if pointer >= selectionPoint:
                return key
        assert False, "Should not reach here"


class Runner(ArithmeticGenome):

    # this language is wrong, genome is the class, dna is the string
    def __init__(self):
        super(Runner, self).__init__()

    # steps through dna from start to end, returns final information left in this cell
    def run(self, dna=None, individual=None, startValue = None):
        if individual is not None:
            dna = individual.dna

        # print "Processing dna {}".format(dna)

        self.operator = self.getFunction('O')
        self.operand = None

        if startValue is None:
            self.information = 0.0
        else:
            self.information = startValue

        self.numberBuilderString = ""
        self.numberHasDecimalPlace = False
        self.isNegativeNumber = False
        self.doing = self.OPERATOR

        for symbol in dna:
            self.processSymbol(symbol)

        # if ending on a number, process it
        if self.doing == ArithmeticGenome.NUMBER:
            self.finishNumber()
            self.runOperatorOnNumber()

        return self.information

    def processSymbol(self, symbol):

        type = self.getType(symbol)

        # NOTE each instruction can choose which mode it leaves processing in, according to if it
        # has left a number ready or not
        if type == ArithmeticGenome.INSTRUCTION:
            self.runInstruction(symbol)

        elif type == ArithmeticGenome.NUMBER:
            if self.doing <> ArithmeticGenome.NUMBER:
                self.operand = 0

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


