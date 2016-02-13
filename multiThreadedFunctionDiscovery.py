
from g1.arithmeticgenome import ArithmeticGenome
from g1.population import Population, PopulationAndSelectionConfig
from g1.multithreading import PrintThread, FunctionDiscoveryTask, TaskRunner, createAndStartPrintAndTaskQueues, goGentleIntoThatGoodNight
from g1.individual import Individual

import random
import logging
# import cProfile, pstats
import datetime, time

### Setup
random.seed()

logFormat = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logFormat)
systemLog = logging.getLogger(__name__)
systemLog.setLevel(logging.WARNING)

st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
dataLogFileName = 'data/Times2.' + st + ".tsv"

# Creates queues which facilitate multi-threaded execution of populations simultaneously, and safe multi-threaded logging
taskQueue, printQueue = createAndStartPrintAndTaskQueues(dataLogFileName, systemLog, threads=1)

### Example to discover a constant value, looping through different dna lengths, with multi-threading

def problemTimesTwo(i):
    return i * i + i

timesTwoTestSet = [2,16,99,1045,0.1]

populationSize=60
iterations = 500

dnaLength = 10

for x in range(0,100):
    populationConfig = PopulationAndSelectionConfig(populationSize,0.0001, 0.33, 2, 0.16, 0.32, 0, 0.33, 1, 1, 1, 1, 0, 1, 0.25, 0.25, 0.4, 0.5, 1, 0)
    genomeConfig = {"length" : dnaLength}
    t = FunctionDiscoveryTask(problemTimesTwo, timesTwoTestSet, ArithmeticGenome, genomeConfig, populationConfig, iterations, False)
    taskQueue.put(t)


# Wait for everything to finish, and close peacefully. Without this end of execution of the main threads will kill off all other threads that are probably still running
goGentleIntoThatGoodNight(taskQueue, printQueue)
