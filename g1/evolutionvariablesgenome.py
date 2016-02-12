# from g1.arithmeticgenome import ArithmeticGenome
# from g1.population import Individual, Population, PopulationAndSelectionConfig
#
# class Runner(object):
#
#     # this language is wrong, genome is the class, dna is the string
#     def __init__(self, genomeType):
#         self.genome = genomeType()
#
#     # steps through dna from start to end, returns final information left in this cell
#     def run(self, dna):
#         self.dna = dna # a complete configuration for population
#
#
#         # run pop 50 times, with max iterations ~250
#
#         p = Population(
#             self.systemLog,
#             genomeType=task.type,
#             fitnessFunction=task.problem,
#             populationAndSelectionConfig=self.dna
#         )
#
#
#         # fitness score = num generations total. failure should be largely penalised so that success inside range is much better
#         # than failure
#
#         # perhaps scale fitness by a reasonable time frame?
#
#         # shorter dna length should be fitter.
#
#         # faster execution time should be fitter
#
#         # population size should affect score
#
#         # most important factor should make most difference to score
#
#         # select first for success, then for other factors?
#
#
#         start = time.time()
#         p.iterate(task.iterations, printIterations=False)
#         timeRan = time.time() - start
#         # self.processSymbol(ArithmeticGenome.END_MARKER)
#
#         # if ending on a number, process it
#         if self.doing == ArithmeticGenome.NUMBER:
#             self.finishNumber()
#             self.runOperatorOnNumber()
#
#         return self.information
#
#
# class GenomeBase(object):
#
#     END_MARKER = 0
#
#     def __init__(self):
#         # List of tuples of the form (TYPE, VALUE)
#         self.symbols = {}
#
#     def registerSymbols(self, symbols):
#         self.symbols.update(symbols)
#
#     def isSymbolType(self, symbol, type):
#         return self.symbols[symbol][0] == type
#
#     def getType(self, symbol):
#         return self.symbols[symbol][0]
#
#
# class EvolutionGenome(GenomeBase):
#
#  self.populationSize = populationSize # integer min/max, positive
#         self.dnaLength = dnaLength # integer min/max, positive
#         self.startingModifier = startingModifier # 0.0001  - float positive 0-1
#         self.percentToCheckForStagnation = percentToCheckForStagnation # 33% - float 0-1
#         self.stagnationModifierMultiplier = stagnationModifierMultiplier # 2 - float small (0-100?)
#         self.cullStartPercentage = cullStartPercentage # 16% float 0-1
#         self.cullEndPercentage = cullEndPercentage # 32% float 0-1
#         self.fittestSelectionStartPercentage = fittestSelectionStartPercentage # 0% float 0-1
#         self.fittestSelectionEndPercentage = fittestSelectionEndPercentage # 33% float 0-1
#         # The weights that a given mutation method will be chosen
#         self.mutateRandomSelectionWeight = mutateRandomSelectionWeight # 1 positive 0-1
#         self.mutateRandomWithPartnerSelectionWeight = mutateRandomWithPartnerSelectionWeight # 1 positive 0-1
#         self.mutateRandomStripeWithPartnerSelectionWeight = mutateRandomStripeWithPartnerSelectionWeight # 1 positive 0-1
#         self.mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight = mutateMoveStripeToRandomPlaceWithPartnerSelectionWeight # 1 positive 0-1
#         self.newRandomWeight = newRandomWeight # 1 positive 0-1
#         # The base probability of mutation in each method
#         self.mutateRandomProbability = mutateRandomProbability # 0.25 float 0-1
#         self.mutateRandomWithPartnerProbability = mutateRandomWithPartnerProbability # 0.25 float 0-1
#         self.mutateRandomStripeWithPartnerProbability = mutateRandomStripeWithPartnerProbability # 0.4 float 0-1
#         self.mutateMoveStripeToRandomPlaceWithPartnerProbability = mutateMoveStripeToRandomPlaceWithPartnerProbability # 0.5 float 0-1
#
#         self.stagnationMargin = stagnationMargin # 0
#         self.thresholdModifierScaler = thresholdModifierScaler # 1
#
#
#     def __init__(self):
#         super(ArithmeticGenome, self).__init__()
#
#
#
#
#         self.registerSymbols( {
#             '0' : (self.NUMBER, "0") ,
#             '1' : (self.NUMBER, "1") ,
#             '2' : (self.NUMBER, "2") ,
#             '3' : (self.NUMBER, "3") ,
#             '4' : (self.NUMBER, "4") ,
#             '5' : (self.NUMBER, "5") ,
#             '6' : (self.NUMBER, "6") ,
#             '7' : (self.NUMBER, "7") ,
#             '8' : (self.NUMBER, "8") ,
#             '9' : (self.NUMBER, "9") ,
#             '.' : (self.NUMBER, ".") ,
#             'N' : (self.NUMBER, "N") ,
#
#             '+' : (self.OPERATOR, lambda x,y: x + y) ,
#             '*' : (self.OPERATOR, lambda x,y: x * y) ,
#             '-' : (self.OPERATOR, lambda x,y: x - y) ,
#             '/' : (self.OPERATOR, lambda x,y: x / y) ,
#             'O' : (self.OPERATOR, lambda x,y: y)
#         })
#
#
#     def getOperatorFunction(self, symbol):
#         return self.symbols[symbol][1]
