

class reader(object):

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


    def getOperatorFunction(self, symbol):
        return self.symbols[symbol][1]
