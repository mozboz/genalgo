# genalgo

This is an experiment with genetic algorithms.

The general idea is to create a basic language expressable in the genes of chromosomes, and therefore manipulable by genetic algorithms.

The GA language is simple numerical and mathematical symbols, and reasonably tolerant to any weird sequences and complete gibberish. This is by design: it allows the GA
to develop reasonably smoothly through strange/redundant patterns until something useful is found.

There is no invalid sequence, and no errors can be generated.

Some examples of well evolved chromosomes (called 'dna' in the code) for a selection algorithm that is attempting to get a numeric output as close to 0.333 as possible:

    7NO7139.77/793308*37
    8/95/++50+0865/2748/
    56+8/192.192.1921922
    +8--.87*.18+8/27.878
    3737O/222/8417-2//6N
    03N/07+531/894*.5611
    O.54-.207.OO.54-.207
    650O*..5252+984/3980
    92/.8/345.3453453453
    916+N1678N5+4/053168
    ONO.03-7.6-.*6O2/6.-
    78.*3.0/N9/2887+9/27

As of writing, the dna length is not variable during evolution, there is no fitness related to length or unused characters in the string.

Mutation and selection are reasonably simple, see Population.py. There is a 'cull' feature which is to detect when progress has 
stagnated and kill off what are always a set of in-bred very similar chromosome

Fun features to maybe make next, opportunities for development:

* Single populations seem to hone in on a particular solution. Once there are a small number of chromosomes who are very close to the solution but who can not make it, it is impossible for any new introductions to the community to develop, because they are immediately outselected by the existing very fit individuals
* Multiple simultaneous population execution, with cross over between populations
* Execution of other individuals as 'functions'
* Variable storage/recall allowing out of order (parenthesized) execution
* Variable length 'dna'/chromosome
* Fitness calculation factoring in account execution time or dna/chromosome length
* As there are many factors to the evolution algorithm, it seems like a GA would be a great way to evolve the best set of parameters for the selection process itself!

# the arithmetic genome

There is an initial set of genes and functionality called ArithmeticGenome that support definition of a set of symbols that allow numbers and operators to be built into strings of DNA, and a 'Runner' which processes strings of these symbols of arbitrary length.

There are symbols to allow numbers to be represented (NUMBERs), and symbols for functions which act on stored values and numbers found in the dna (OPERATORS).

There are only two 'values' available to the Runner: A single stored value referred to as the 'Information', and any next number found in the DNA, called the 'number'. An operator is always called with:

    Information = Operator(Information, Number)
    
Note: The operator does not have to return a value that is a function of both or either of the input values. The Operator only runs when a number is found to run on. In code, Information and Number are both floats

## Examples

In the examples 'I' is the initial information, 'output' refers to the value of 'I' after the dna has been processed.

    I: ?
    dna: '2*6'
    
In this case, output will be 12. Any initial value of I is overwritten by the first 2

    I: 4
    dna: '+2*3'
    
Output here will be 18. Note that as commands are executed sequentially the output here is 18, not 10 as you would expect if the expression '4+2*3' was evaluated using normal operator precedence.

    I: 12
    dna: '/4*-++17N.23NN.7'
    
This will first executre /4 to set I to 3. The next group of operators '*-++' are redundant - only the final '+' will be used as the operator. The string after the final + will be parsed as a single number of value -17.237, so output will be -14.237

## Adding Operators

Operators are defined in class ArithmeticGenome, and can be added by adding a new entry to the dict initialised in the constructor.

For example, to add a logical 'AND', and exponential operations you would add the line:

     ...
     '&' : (self.OPERATOR, lambda x,y: int(x) & int(y)),                # having to translate to int is troublesome...
     '^' : (self.OPERATOR, lambda x,y: x ^ y),
     ...

 All symbols get included in chromosome creation and mutation functions automatically, with equal precedence. Because of the evolution algorithm they will be rapidly used or evolved out of the chromosome depending on how useful they are in solving the problem.
 
 
