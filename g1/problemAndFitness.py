
# Subclass this class to define a problem.

# Override the 'problem' method with any function that either returns a constant value, or takes
# the input parameter and does anything with it.

# If your method returns a boolean value, and therefore any guess can either be 'right' or 'wrong', then have it
# return either 1 or 0, and set the 'type' property to Problem.BOOLEAN.

# If your method returns anything other than bool, and a guess can be exactly correct, close, or far away, then set
# the 'type' property to Problem.CONTINUOUS.

# Generally, unless you are returning a constant value, you should always have a set of test inputs defined in the
# testData property. These will be passed to the chromosome to get it to operate on them, and the output of that
# will be compared with the output of your function.


## THIS IS THE BASE CLASS, DO NOT ALTER. SEE BELOW FOR EXAMPLE OF DEFINING PROBLEMS.
class ProblemBase(object):
    CONTINUOUS = 1
    BOOLEAN = 2

    type = None

    # Override with testData, see examples below
    testData = []

    # Override with problem function, see examples below
    def problem(self, input):
       print "Redefine me with a problem that returns a constant or function of input"
       exit(0)

    def fitness(self, actual, input=0):
        if self.type == ProblemBase.BOOLEAN:
            if abs(actual - self.problem(input)) < 0.25:
                return 0
            else:
                return 1

        elif self.type == ProblemBase.CONTINUOUS:
            return abs(actual - self.problem(input))

        assert False, "type not found"


##### EXAMPLES

# Try to find pi. As this is a constant value there is no test data set, and as it's not a boolean,
# type is set to CONTINUOUS
class DiscoverPiProblem(ProblemBase):

    def problem(self, input):
        return 3.141

    type = ProblemBase.CONTINUOUS


# Try to find functionality that multiplies input by 2. As this requires some input, we have to give
# some test data here in the testData property
class TimesBy2(ProblemBase):

    def problem(self, input):
        return input * 2

    type = ProblemBase.CONTINUOUS

    testData = [5, 10, -67.9, 42, -31337, 2^6, 1/3, 0.333]

# Try to find a function that determines if input is greater than 42 or not. Because this requires some input
# we provide testData, particularly with test input relevant to the problem - e.g. close to the threshold
class GreaterThan42(ProblemBase):

    def problem(self, input):
        if input > 42:
            return 1
        else:
            return 0

    type = ProblemBase.BOOLEAN

    testData = [41, 43, 0.001, 100000, -1, -100]