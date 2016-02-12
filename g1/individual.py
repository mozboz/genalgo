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
            self.dna, _ = self.genome.createIndividual(params, [], 0)

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