
from g1.arithmeticgenome import ArithmeticGenome
from g1.population import Individual, Population

import random
import logging
import cProfile, pstats
import datetime, time
import Queue
import threading

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

    def run(self):
        while True:
            logEntry = self.queue.get()
            self.f.write(logEntry + "\n")
            print logEntry
            self.queue.task_done()


class Task(object):
    def __init__(self, problem, type, populationSize, dnaLength, iterations):
        self.problem = problem
        self.type = type
        self.populationSize = populationSize
        self.dnaLength = dnaLength
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
            populationSize=task.populationSize,
            dnaLength=task.dnaLength,
            genomeType=task.type,
            fitnessFunction=task.problem,
        )

        start = time.time()
        p.iterate(task.iterations, printIterations=False)
        timeRan = time.time() - start

        logLine = "{}\t{}\t{}\t{}\t{}\t{}\t{}".\
            format(p.finished(), timeRan, p.generation, p.population[0].fitness, task.populationSize, task.dnaLength, "".join(p.population[0].dna))

        printQueue.put(logLine)



random.seed()

systemLog = logging.getLogger(__name__)
systemLog.setLevel(logging.DEBUG)


st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
dataLogFileName = 'data/Log0.333.' + st + ".tsv"

# Create print queue to take logging requests from multiple threads
printQueue = Queue.Queue()
printThread = PrintThread(dataLogFileName, printQueue)
printThread.setDaemon(True)
printThread.start()

# Crate job queue to distribute jobs to worker threads
taskQueue = Queue.Queue()
threads = 4

for k in range(0,threads):
    p = TaskRunner(systemLog, taskQueue, printQueue)
    p.setDaemon(True)
    p.start()

problem = lambda x: 0.333
populationSize=60

for dnaLength in range(5,51,5):
    for k in range(0,100):
        t = Task(problem, ArithmeticGenome, 60, dnaLength, 1000)
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


