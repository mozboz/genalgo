import datetime, time
import threading
import queue

from .population import Population

class PrintThread(threading.Thread):
    def __init__(self, filename, printQueue):
        threading.Thread.__init__(self)
        self.queue = printQueue
        self.f = open(filename, 'a')
        print("Data log started: " + filename)
        self.f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format("Completed","Time","Generation","Min Fitness","Pop Size", "DNA Length", "Best DNA"))

    def run(self):
        while True:
            logEntry = self.queue.get()
            self.f.write(logEntry + "\n")
            print(logEntry)
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
        print("TaskRunner started " + self.__repr__())

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

class MultiThreadingContext(object):

    def __init__(self, dataLogFileName = None, systemLog = None, numThreads = None):
        self.printQueue = None
        self.taskQueue = None
        if dataLogFileName is not None and systemLog is not None and numThreads is not None:
            self.start(dataLogFileName, systemLog, numThreads)

    def start(self, dataLogFileName, systemLog, numThreads=1):

        # print queue facilitates multi threaded writing to file and stdout
        self.printQueue = queue.Queue()
        self.printThread = PrintThread(dataLogFileName, self.printQueue)
        self.printThread.setDaemon(True)
        self.printThread.start()

        # Create job queue to distribute jobs to worker threads
        self.taskQueue = queue.Queue()

        for _ in range(0, numThreads):
            p = TaskRunner(systemLog, self.taskQueue, self.printQueue)
            p.setDaemon(True)
            p.start()

    def goGentleIntoThatGoodNight(self):

        # Pause for a moment to give caller time to put stuff in the queue
        time.sleep(1)

        # Queue.join() would be neater, but stops receiving interrupt and being able to kill process easily
        while True:
            if self.printQueue.qsize() == 0 and self.taskQueue.qsize() == 0:
                break
            time.sleep(5)

        self.printQueue.join()
        self.taskQueue.join()

    # Pause for any remaining stuff to be written to stdout/files before execution finishes
        time.sleep(1)

    def runTask(self, t):
        self.taskQueue.put(t)