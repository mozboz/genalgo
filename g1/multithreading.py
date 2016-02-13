
import datetime, time
import threading
import Queue
from population import Population

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
    def __init__(self, problem, chromosomeType, genomeConfig, populationConfig, iterations, printIterations = False):
        self.problem = problem
        self.type = chromosomeType
        self.genomeConfig = genomeConfig
        self.populationConfig = populationConfig
        self.iterations = iterations
        self.printIterations = printIterations



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

        self.systemLog.debug(self.__repr__() + " took task")
        p = Population(
            self.systemLog,
            genomeType = task.type,
            genomeParams = task.genomeConfig,
            problem = task.problem,
            populationAndSelectionConfig = task.populationConfig
        )

        start = time.time()
        p.iterate(task.iterations, printIterations=task.printIterations)
        timeRan = time.time() - start

        logLine = "{}\t{}\t{}\t{}\t{}\t{}\t{}".\
            format(p.finished(), timeRan, p.generation, p.population[0].fitness, task.populationConfig.populationSize,
                   task.genomeConfig['length'], "".join(p.population[0].dna))

        self.printQueue.put(logLine)


def createAndStartPrintAndTaskQueues(dataLogFileName, systemLog, threads=1):

    # print queue facilitates multi threaded writing to file and stdout
    printQueue = Queue.Queue()
    printThread = PrintThread(dataLogFileName, printQueue)
    printThread.setDaemon(True)
    printThread.start()

    # Create job queue to distribute jobs to worker threads
    taskQueue = Queue.Queue()

    for k in range(0,threads):
        p = TaskRunner(systemLog, taskQueue, printQueue)
        p.setDaemon(True)
        p.start()

    return taskQueue, printQueue


def goGentleIntoThatGoodNight(taskQueue, printQueue):

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
