
from genomebase import GenomeBase
import random

class Runner(object):

    # this language is wrong, genome is the class, dna is the string
    def __init__(self, genomeType):
        self.genome = genomeType()

    # steps through dna from start to end, returns final information left in this cell
    def run(self, dna):
        self.dna = dna
        self.position = 0
        self.operator = self.genome.getOperatorFunction('O')
        self.operand = None
        self.information = 0.0
        self.numberBuilderString = ""
        self.numberHasDecimalPlace = False
        self.isNegativeNumber = False
        self.doing = self.genome.OPERATOR

        for symbol in self.dna:
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

    def createIndividual(self, params):
        return [random.choice(self.allSymbols) for x in range(params['length'])]

     # threshold likelihood of each character being swapped for random one
    def mutateRandomMutation(self, dna, threshold):
        return [dna[x] if random.random() > threshold else random.choice(self.allSymbols) for x in range(len(dna))]

    # return new dna same length as partner 1, with each character randomly selected from 1 or 2 weighted by threshold
    def mutateBreedWithPartnerRandomSymbol(self, partner1Dna, partner2Dna, threshold):
        return [partner1Dna[x] if random.random() > threshold else partner2Dna[x] for x in range(len(partner1Dna))]

    # threshold is max percent of characters that can be swapped
    def mutateBreedWithPartnerCopyRandomStripeToSamePlace(self, partner1Dna, partner2Dna, threshold):

        lengthToSwap = int(len(partner1Dna) * threshold * random.random())
        startPoint = random.randrange(0,len(partner1Dna))

        # print "{} {}".format(startPoint, lengthToSwap)

        return [partner2Dna[x] if x in range(startPoint, startPoint + lengthToSwap) else partner1Dna[x] for x in range(len(partner1Dna))]

    # takes a random length piece of partner2 and moves it to a random place on partner 1
    def mutateBreedWithPartnerMoveStripeToRandomPlace(self, partner1Dna, partner2Dna, threshold):

        lengthToSwap = int(len(partner2Dna) * threshold * random.random())
        startPointSource = random.randrange(0,len(partner2Dna))

        startPointDest = random.randrange(0, len(partner1Dna))

        # length might overrun new dna
        if lengthToSwap + startPointDest > len(partner1Dna):
            lengthToSwap = len(partner1Dna) - startPointDest

        # length and start point to read form are random, so they could read off end of source
        if lengthToSwap + startPointSource > len(partner2Dna):
            lengthToSwap = len(partner2Dna) - startPointSource

        # print "length {} source {} dest {}".format(lengthToSwap, startPointSource, startPointDest)

        newDna = partner1Dna[:]

        for x in range(0, lengthToSwap):
            newDna[startPointDest+x] = partner2Dna[startPointSource + x]

        return newDna
