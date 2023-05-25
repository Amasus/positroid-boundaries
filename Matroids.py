#Author: Everett Sullivan.
#Note: This program was written for Python 3.
#Purpose: The purpose of this code is checking whether a given set of sets 
#satisfies the conditions neede for it to define a matroid.
#E.g. is it the set of bases, or circuits, etc. 
#currently only bases implemented.

#import sys
import math
import itertools #needed for generate all k element subsets
from warnings import warn
#from itertools import chain
#import functools #needed for custom compare functions
#import copy

from timeit import default_timer as timer

####################################################
#Matroids
####################################################

#nonEmptySetCheck:
#Purpose: Given a set of frozen set, checks that
#it is not empty
#candidateSet: frozen set to be tested
#returns: boolean
def nonEmptySetCheck(candidateSet):
    if len(candidateSet) == 0:
        isNotEmpty = False
    else:
        isNotEmpty = True
    return isNotEmpty

# sameSizeCheck:
# Purpose: Given a candidate Bases set, verify that every set has the same size.
# candidateBases: a non-empty set of frozensets 
# returns: boolean
def sameSizeCheck(candidateBases):
    sizeSet = {len(basisElement) for basisElement in candidateBases}
    if len(sizeSet) == 1:
        sameSize = True
    elif len(sizeSet) >1:
        sameSize = False
    else:
        raise ValueError('Unique lengths of candidate Bases set not positive')
    return sameSize

# hasExchange: (helper function to hasBasisExchangeProperty)
# Purpose: Given two sets and a set of seets, see if they have
#       the basis exchange property. I.e. for every element a in
#       A check that there is an element b in B such that
#       (A \ {a}) cup {b} is in basis.
# setA: a frozen set
# setB: a frozen set
# bases: a set of frozen sets.
# returns: boolean
def hasExchange(setA,setB,bases):
    #check that setA and setB are, indeed, in basis
    if (setA not in bases) or (setB not in bases):
        raise ValueError('One of the candidate sets not in given basis')
    #calculate the set differences
    setDiffAMinusB = setA - setB
    setDiffBMinusA = setB - setA

    addaToSetB = {setB.union({a}) for a in setDiffAMinusB}
    exchangedSets = {Bcupa-{b} for b in setDiffBMinusA for Bcupa in addaToSetB }
    exchangedSetsInBases = exchangedSets.intersection(bases)
    hasExchange=(len(exchangedSetsInBases >0))
    if not hasExchange:
        warn(f'{setA} and {setB} do not have a valid exchange')
    return hasExchange

# hasBasisExchangeProperty:
#Purpose: Given a set of sets, determine if
#          it has the basis exchange property
# candidateBases: a non-empty set of frozensets
# returns: boolean 
def hasBasisExchangeProperty(candidateBases):
    basisPairs = list(itertools.permutations(candidateBases, 2))
    #Since hasExchange checks only A againts B and not vice-versa we need to order them

    #note that basisPairs will be an empty list if candidateBases has only 
    #one element in it. Therefore this method will return True in this case
    #as desired
    if len(basisPairs) == 0:
        return True
    else:
        for pair in basisPairs:
            basisExchangeProperty = hasExchange(pair[0],pair[1],candidateBases) 
    return basisExchangeProperty

#isMatroidBases:
#Purpose: Check whether or not a candidate bases set is a matroid
def isMatroidBases(candidateBases):
    emptyMatroid = not nonEmptySetCheck(candidateBases) 
    nonemptyMatroid = nonEmptySetCheck(candidateBases) & sameSizeCheck(candidateBases) & hasBasisExchangeProperty(candidateBases)
    return (emptyMatroid | nonemptyMatroid)


# generateMatroidsSlice:
# Purpose: Create all matroids (including the empty matroids)
#           over a ground set of size n, with rank = k, 
#           defined by num Basis elements
# n: the size of the ground set
# k: the size of the basis elements
# num: the size of the Bases set
# returns: list of sets of frozen sets, each set of size num 

def generateMatroidsSlice(n,k,num):
    
    #Check that k <=n
    if n<k:
        raise ValueError('k cannot exceed n')
    if math.comb(n,k)<num:
        raise ValueError('num cannot exceed nCk')

    #Note: need to treat num = 0 differently so that it returns the set
    # with an empty frozen set, not an empty set

    if num == 0: #want empty matroid, equivalent to k= 0
        num = 1
        k = 0

    groundSet = set(range(1,n+1))

    #get all possible basis elements
    #namely all k subsets of the groundset
    basisElements = itertools.combinations(groundSet, k)
    frozenBasisElements = {frozenset(basis) for basis in basisElements}

    #get all possible matroids with the correct number of bases elements
    #Note: Making this into a set to avoid ({}, ) data structure
    #when k  = 0
    possibleMatroids = itertools.combinations(frozenBasisElements,num)
    matroids = [set(possibleMatroid) for possibleMatroid in possibleMatroids if isMatroidBases(frozenset(possibleMatroid))]
    return matroids

# generateMatroids:
# Purpose: Create all matroids (including the empty matroids)
#           over ground set n with basis elements of size k.
# n: the size of the ground set
# k: the size of the basis elements

def generateMatroids(n,k):
    #start with the empty list
    matroidList= []    
    #add to this list using generateMatroidSlice
    #Note, num here cannot be 0, to avoid overcounting
    #the empty matroid
    for num in range(1,math.comb(n,k)+1):
        matroidList.extend(generateMatroidsSlice(n,k, num))
    return matroidList

# printMatroid:
# Purpose: Given a Matroid print in out.
# k: rank
# matroid: the matroid #TODO: Everett, what type of a data structure is this?
# setsep: the string used to seperate the sets from one another.
# innerSetsetp: the string used to seperate the element inside a set.
# setBraces: (bool) Use braces for the sets.
def printMatroid(k,matroid,setsep = ',',innerSetsep = ',',setBraces = True):
    orderedNecklace = [sorted(list(element)) for element in matroid]
    orderedNecklace.sort()
    print("{", end ="")
    for i in range(len(orderedNecklace)):
        if (i != 0):
            print(setsep, end ="")
        if setBraces:
            print("{", end ="")
        for j in range(k):
            if (j != 0):
                print(innerSetsep, end ="")
            print(orderedNecklace[i][j], end ="")
        if setBraces:
            print("}", end ="")
    print("}")

#isMinDepenedent:
#Purpose: Given a set of frozen sets, determine it is defines the 
#minimal dependent set of an independence system
#candidateSet: set of frozen sets
def isMinDependent(candidateSet):
    containsEmptyset = frozenset({}) in candidateSet
    if containsEmptyset:
        warn("candidate dependent set contains the empty set")
    allPairs = list(itertools.permutations(candidateSet, 2))
    if len(allPairs) == 0:
        return(True)
    setContainment = any([pair[0].issubset(pair[1]) for pair in allPairs])
    if setContainment:
        warn('some set of the candidate dependent set is contained in another ') 
    return((not containsEmptyset) & (not setContainment))

# hasCircuitCond3:
#Purpose: Given a set of frozensets, determine if
#          it has the basis exchange property
# candidateCircuit: a set of frozensets
# returns: boolean 
def hasCircuitCond3(candidateCircuit):
    allCircuitPairs = list(itertools.combinations(candidateCircuit, 2))
    intersectingCircuitPairs = [circuitPair for circuitPair in allCircuitPairs if 
                                len(circuitPair[0].intersection(circuitPair[1]))>0]
    if len(intersectingCircuitPairs) > 0:
        for pair in intersectingCircuitPairs:
            complementList = [(pair[0].union(pair[1])).difference({elem}) for elem in pair[0].intersection(pair[1])]
            containsCircuit = [any([circuit.issubset(complements) for circuit in candidateCircuit]) for complements in complementList]                       
                #   if all([not(circuit.issubset(complement)) for circuit in candidateCircuit]):
            condition3 = all(containsCircuit)
            if not(condition3):
                warn(f'{pair} fails to saitisfy the circuit condition')
                return(condition3)
    return(condition3)

#isMatroidCircuit:
#Purpose: Check whether or not a candidate circuit set is a matroid
def isMatroidCircuit(candidateCircuit):
    minDependent = isMinDependent(candidateCircuit)
    conditionThree = hasCircuitCond3(candidateCircuit)
    return (minDependent & conditionThree)
  
#matroidClosure:
#Purpose: implementation of the algorithm to find the largest matroid contained in the
#independence system given by a set of circuits
#circuitSubset: set of frozen sets
#output: the circuit set of a matroid (set of frozen sets)
def matroidClosure(circuitSubset):
    if not isMinDependent(circuitSubset):
        raise ValueError(f"{circuitSubset} is not a valid minimally dependent set")
    isMatroid = isMatroidCircuit(circuitSubset)
    if isMatroid:
        return(circuitSubset)
    allCircuitPairs = list(itertools.combinations(circuitSubset, 2))
    intersectingCircuitPairs = [circuitPair for circuitPair in allCircuitPairs if 
                                len(circuitPair[0].intersection(circuitPair[1]))>0]
    interimResult = circuitSubset
    while len(intersectingCircuitPairs)>0:
        pair = intersectingCircuitPairs[0]
        complementList = [(pair[0].union(pair[1])).difference({elem}) for elem in pair[0].intersection(pair[1])]
        for complement in complementList:
            complementContained = any([circuit.issubset(complement) for circuit in interimResult])
            if complementContained:
                intersectingCircuitPairs.remove(pair)
                break
            else: #not complementContained case
                circuitsNotContainingComplement = {circuit for circuit in interimResult if not complement.issubset(circuit)}
                interimResult = circuitsNotContainingComplement.union({complement})
                allCircuitPairs = list(itertools.combinations(interimResult, 2))
                intersectingCircuitPairs = [circuitPair for circuitPair in allCircuitPairs if 
                                len(circuitPair[0].intersection(circuitPair[1]))>0]
    return(interimResult)

