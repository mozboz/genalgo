
from g1.arithmeticgenome import ArithmeticGenome
from g1.population import Population, PopulationAndSelectionConfig
from g1.individual import Individual

import random
import logging
import cProfile, pstats
import datetime, time
import Queue
import threading

##### 1) Map the concept space of possible developments !!! Expansion in abilities vs speed, multi server deployments?

##### Target interesting behaviours - synergistic relationships where both pop entities benefit?

##### 2) Ability to evolve 'masks' that control variability of the chromosome, such that the mask learns which parts of
##### the chromosome benefit from slower or more rapid change.as



FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

# r = reader(ArithmeticGenome)
# print r.run(['9', '5', '5', '.', 'O', '2', '4', '-', '5', 'N', '.', '2', '1', 'N', '.', '*', '*', '6', '5', '7'])
# exit(0)
#
# d = Individual(ArithmeticGenome, 1,1, length=20)
# e = Individual(ArithmeticGenome, 1,1, length=20)
# print d.dna
# print e.dna
# d.mutateBreedWithPartnerMoveStrip(e, 0.5)
# print d.dna
# exit(0)


class PrintThread(threading.Thread):
    def __init__(self, filename, printQueue):
        threading.Thread.__init__(self)
        self.queue = printQueue
        self.f = open(filename, 'a')
        print "Data log started: " + filename
        self.f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format("Completed","Time","Generation","Min Fitness","Pop Size", "DNA Length", "Best DNA"))

    def run(self):
        while True:
            logEntry = self.queue.get()
            self.f.write(logEntry + "\n")
            print logEntry
            self.queue.task_done()


class Task(object):
    def __init__(self, problem, type, genomeConfig, populationConfig, iterations):
        self.problem = problem
        self.type = type
        self.genomeConfig = genomeConfig
        self.populationConfig = populationConfig
        self.iterations = iterations


class TaskRunner(threading.Thread):
    def __init__(self, systemLog, taskQueue, printQueue):
        threading.Thread.__init__(self)
        self.taskQueue = taskQueue
        self.printQueue = printQueue
        self.systemLog = systemLog
        print "TaskRunner started " + self.__repr__()

    def run(self):
        while True:
            task = self.taskQueue.get()
            self.processTask(task)
            self.taskQueue.task_done()

    def processTask(self, task):

        print self.__repr__() + " took task"
        p = Population(
            self.systemLog,
            genomeType=task.type,
            genomeParams=task.genomeConfig,
            fitnessFunction=task.problem,
            populationAndSelectionConfig=task.populationConfig
        )

        start = time.time()
        p.iterate(task.iterations, printIterations=False)
        timeRan = time.time() - start

        logLine = "{}\t{}\t{}\t{}\t{}\t{}\t{}".\
            format(p.finished(), timeRan, p.generation, p.population[0].fitness, task.populationConfig.populationSize,
                   task.genomeConfig['length'], "".join(p.population[0].dna))

        printQueue.put(logLine)



random.seed()

systemLog = logging.getLogger(__name__)
systemLog.setLevel(logging.WARNING)


st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
dataLogFileName = 'data/Log0.333.' + st + ".tsv"

# Create print queue to take logging requests from multiple threads
printQueue = Queue.Queue()
printThread = PrintThread(dataLogFileName, printQueue)
printThread.setDaemon(True)
printThread.start()

# Crate job queue to distribute jobs to worker threads
taskQueue = Queue.Queue()
threads = 1

for k in range(0,threads):
    p = TaskRunner(systemLog, taskQueue, printQueue)
    p.setDaemon(True)
    p.start()

problem = lambda x: 0.333
populationSize=60

populationConfig = PopulationAndSelectionConfig(60, 0.0001, 0.33, 2, 0.16, 0.32, 0.33, 1, 1, 1, 1, 1, 0, 1, 0.25, 0.25, 0.4, 0.5, 1)


for dnaLength in range(10,51,5):
    for k in range(0,100):
        populationConfig = PopulationAndSelectionConfig(populationSize,0.0001, 0.33, 2, 0.16, 0.32, 0, 0.33, 1, 1, 1, 1, 0, 1, 0.25, 0.25, 0.4, 0.5, 1)
        genomeConfig = {"length" : dnaLength}
        t = Task(problem, ArithmeticGenome, genomeConfig, populationConfig, 1000)
        taskQueue.put(t)


# These sleeps iare to prevent strange errors if we try to exit too quickly
time.sleep(1)

# Queue.join() would be neater, but stops receiving interrupt and being able to kill process easily
while True:
    if printQueue.qsize() == 0 and taskQueue.qsize() == 0:
        break
    time.sleep(10)

printQueue.join()
taskQueue.join()
time.sleep(1)

# p = pstats.Stats('restats')
# p.sort_stats('time')
# p.print_stats()



# print(chr(27) + "[2J" + chr(27) + "[1;1H")
# p = Population(log, populationSize=60, dnaLength=30, genomeType=ArithmeticGenome, fitnessFunction=fixedValue, maxAge = 500)
# genome = ArithmeticGenome()
# reader = reader(genome)
#
#
# for x in range(1,10):
#     d = Individual(ArithmeticGenome, length=10)
#     v = reader.run(d.dna)
#     f = fitness(fixedValue, v)
#
#


