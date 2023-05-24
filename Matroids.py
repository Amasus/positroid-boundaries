#Author: Everett Sullivan.
#Note: This program was written for Python 3.
#Purpose: The purpose of this code is checking whether a given set of sets 
#satisfies the conditions neede for it to define a matroid.
#E.g. is it the set of bases, or circuits, etc. 
#currently only bases implemented.

#import sys
import math
import itertools #needed for generate all k element subsets
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
        isEmpty = False
    else:
        isEmpty = True
    return isEmpty

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
# basis: a set of frozen sets.
# returns: boolean
def hasExchange(setA,setB,basis):
    #check that setA and setB are, indeed, in basis
    if (setA not in basis) or (setB not in basis):
        raise ValueError('One of the candidate sets not in given basis')
    #calculate the set differences
    setDiffAMinusB = setA - setB
    setDiffBMinusA = setB - setA

    addaToSetB = {setB.union({a}) for a in setDiffAMinusB}
    exchangedSets = {Bcupa-{b} for b in setDiffBMinusA for Bcupa in addaToSetB }

    hasExchange=nonEmptySetCheck( exchangedSets.intersection(basis))
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
    basisExchangeProperty = True
    i = 0
    while basisExchangeProperty and (i < len(basisPairs)):
        #If a set doesn't exchange with another set, we can quit the loop early.
        pair = basisPairs[i]
        basisExchangeProperty = hasExchange(pair[0],pair[1],candidateBases)
        i += 1
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

# hasCircuitCond:
#Purpose: Given a set of frozensets, determine if
#          it has the basis exchange property
# candidateBases: a non-empty set of frozensets
# returns: boolean 
def hasCircuitCond(candidateCircuit):
    allCircuitPairs = list(itertools.combinations(candidateCircuit, 2))
    intersectingCircuitPairs = [circuitPair for circuitPair in allCircuitPairs if 
                                len(circuitPair[0].intersection(circuitPair[1]))>0]
    for pair in intersectingCircuitPairs:
        for elem in pair[0].intersection(pair[1]):
            complement = (pair[0].union(pair[1])).difference({elem})
            if all([not(circuit.issubset(complement)) for circuit in candidateCircuit]):
                return (False)
    return(True)
    
