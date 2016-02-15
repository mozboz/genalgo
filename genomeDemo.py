from g1.arithmeticgenome import ArithmeticGenome, Runner
from g1.population import Population, PopulationAndSelectionConfig
from g1.individual import Individual
import logging, random

### Setup

logFormat = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logFormat)
random.seed()
systemLog = logging.getLogger(__name__)
systemLog.setLevel(logging.WARNING)

age = 0

### Test Fixed Value

dna = "2*N2.5"    # expected output fixed value -5.0

# i = Individual(systemLog, ArithmeticGenome, age, "bob", dnaString=dna)
#
# runner = Runner()
#
# print runner.run(individual=i)


## Test Process An Input

dna = "*2+3"    # expected output is: input*2+3. So 2 -> 7, 10 -> 23
dna = ">*<"     # expected output is squared (stores value to storage, retrieves storage to number, multiplies value by number
dna = "+>*7<+<+<+<*3>-7-5-N" # 3n^2 + 9n -12 (evolved)
dna = ">/+>+<-1-1" # *2+2 (evolved)

i = Individual(systemLog, ArithmeticGenome, age, "bob", dnaString=dna)

runner = Runner()

print runner.run(individual=i,startValue=100)
# print runner.run(individual=i,startValue=10)



## Arbitrarily Long Dna is always executable

# i = Individual(systemLog, ArithmeticGenome, age, "bob", params={"length" : 100})
# print "".join(i.dna)
#
# runner = Runner()
#
# print runner.run(individual=i)