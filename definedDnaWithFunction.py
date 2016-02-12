
from g1.arithmeticgenome import ArithmeticGenome
from g1.population import Population, PopulationAndSelectionConfig
from g1.multithreading import PrintThread, Task, TaskRunner, createAndStartPrintAndTaskQueues, goGentleIntoThatGoodNight
from g1.individual import Individual

import random
import logging
import datetime, time

### Setup
random.seed()

logFormat = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logFormat)
systemLog = logging.getLogger(__name__)
systemLog.setLevel(logging.WARNING)

st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
dataLogFileName = 'data/Log0.333.' + st + ".tsv"


### Example to test the fitness of a predefined set of dna strings, for a small set of test data and a simple function

def problemTimesTwo(i):
    return i * 2

timesTwoTestSet = [2,16,99,1045,0.1]

populationSize=60
iterations = 500

p = []
p.append(Individual(systemLog, ArithmeticGenome, 0, "1", dnaString = "1"))
p.append(Individual(systemLog, ArithmeticGenome, 0, "1", dnaString = "*2"))
p.append(Individual(systemLog, ArithmeticGenome, 0, "1", dnaString = "*3"))

config = PopulationAndSelectionConfig(populationSize,0.0001, 0.33, 2, 0.16, 0.32, 0, 0.33, 1, 1, 1, 1, 0, 1, 0.25, 0.25, 0.4, 0.5, 1)

pop = Population(systemLog, ArithmeticGenome, {}, problemTimesTwo, config, p)
pop.evaluateTestSet(timesTwoTestSet)

print pop.dump()
