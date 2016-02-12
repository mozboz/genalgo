


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