import random

class Runner(object):

    # this language is wrong, genome is the class, dna is the string
    def __init__(self, genomeType):
        self.genome = genomeType()

    # steps through dna from start to end, returns final information left in this cell
    def run(self, dna):

        # assume dna is 32 bits long, 4 x 8 bit

        result = []

        for x in range(0,3):
            binaryString = dna[x*8:x*8+8]
            result[x] = int(binaryString, 2)



class GenomeBase(object):

    END_MARKER = 0

    def __init__(self):
        # List of tuples of the form (TYPE, VALUE)
        self.symbols = {}

    def registerSymbols(self, symbols):
        self.symbols.update(symbols)

    def isSymbolType(self, symbol, type):
        return self.symbols[symbol][0] == type

    def getType(self, symbol):
        return self.symbols[symbol][0]


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

