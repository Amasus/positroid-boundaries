# Dyck Path (DP): a path with only up and down steps that ends where it started and never goes below where it started
# Motzkin Path (MP): a path with only up, down, and sideways steps that ends where it started and never goes below where it started
# Marked Motzkin Path (MMP): a path with only up, down, sideways, and marked sideways steps that ends where it started and never goes below where it started
# Marked Base Motzkin Path (MBMP): a path with only up, down, sideways, and marked sideways steps that ends where it started, has every marked sideways step at the lowest hight, and never goes below where it started
# Peakless Marked Base Motzkin Path (PMBMP): a MBMP path with no down step comming immediatly after an up step.

#Author: Everett Sullivan.
#Note: This program was written for Python 3.

import sys
import itertools #needed for generate all k element subsets
from itertools import chain
import functools #needed for custom compare functions

# basicMatroidBasisCheck:
# Purpose: Given a set of independance data (which is presumably
#          a set of basis elements of a matroid), verify that it
#          is non-empty and that every set has the same size.
# independanceData: a non-empty set of frozensets that all have
#                   the same size.
def basicMatroidBasisCheck(independanceData):
    sameSize = True;
    i = 1;
    theElements = list(independanceData)
    if (len(independanceData) != 0): #the set is nonempty
        elementSize = len(theElements[0])
        while sameSize and i < len(theElements):
            if len(theElements[i] != elementSize):
                sameSize = False
    else:
        sameSize = False
    return sameSize     

# hasBasisExchangeProperty:
# Purpose: Given a set of independance data (which is presumably
#          a set of basis elements of a matroid), determine if
#          if has the basis exchange property of matroids.
# independanceData: a non-empty set of frozensets that all have
#                   the same size.
def hasBasisExchangeProperty(independanceData):
    basisPairs = list(itertools.permutations(independanceData, 2))
    #Since hasExchange checks only A againts B and not vice-versa we need to order them
    basisExchangeProperty = True
    i = 0
    while basisExchangeProperty and (i < len(basisPairs)):
        #If a set doesn't exchange with another set, we can quit the loop early.
        pair = basisPairs[i]
        basisExchangeProperty = hasExchange(pair[0],pair[1],independanceData)
        i += 1
    return basisExchangeProperty

# hasExchange: (helper functino to hasBasisExchangeProperty)
# Purpose: Given two sets of a (assumed) basis see if they have
#       the basis exchange property. I.e. for every element a in
#       A check that there is an element b in B such that
#       (A \ {a}) cup {b} is in basis.
# setA: a set
# setB: a set
# basis: a set of sets.
# Assumptions: basis is a set of frozensets.
#              setA and setB are in basis.
def hasExchange(setA,setB,basis):
    setDiffAMinusB = list(setA - setB)
    setDiffBMinusA = list(setB - setA)
    canExchangeAll = True
    i=0
    while canExchangeAll and (i < len(setDiffAMinusB)):
        #If no b exists for the given a we can quite the while loop early.
        hasAExchange = False
        j = 0
        while (not hasAExchange) and (j < len(setDiffBMinusA)):
            #If we find a b we can quit the while loop early.
            if (setA - {setDiffAMinusB[i]}) | {setDiffBMinusA[j]} in basis:
                hasAExchange = True
            j += 1
        i += 1
        canExchangeAll = hasAExchange
    return canExchangeAll

# generateMatroidsSlice:
# Purpose: Create all mataroids (including the empty matroids)
#           over ground set n with basis element of size k that
#          have exactly num elements in the basis.
# n: the size of the ground set
# k: the size of the basis elements
# Assumptions: 0 <= k <= n, 0 <= num
def generateMatroidsSlice(n,k,num):
    groundSet = set(range(1,n+1))
    basisElements = itertools.combinations(groundSet, k)
    frozenBasisElements = set()
    #get all possible basis elements
    for element in basisElements:
        frozenBasisElements.add(frozenset(element))
    possibleMatroids = itertools.combinations(frozenBasisElements,num)
    matroids = []
    for possibleMatroid in possibleMatroids:
        if hasBasisExchangeProperty(set(possibleMatroid)):
            matroids.append(set(possibleMatroid))
    return matroids

# generateMatroids:
# Purpose: Create all mataroids (including the empty matroids)
#           over ground set n with basis element of size k.
# n: the size of the ground set
# k: the size of the basis elements
# Assumptions: 0 <= k <= n
def generateMatroids(n,k):
    groundSet = set(range(1,n+1))
    basisElements = itertools.combinations(groundSet, k)
    frozenBasisElements = set()
    #get all possible basis elements
    for element in basisElements:
        frozenBasisElements.add(frozenset(element))
    #Get the power set of all possible basis elements
    possibleMatroids = chain.from_iterable(itertools.combinations(frozenBasisElements,num) for num in range(0,len(frozenBasisElements)))
    matroids = []
    for possibleMatroid in possibleMatroids:
        if hasBasisExchangeProperty(set(possibleMatroid)):
            matroids.append(set(possibleMatroid))
    return matroids

# shiftingCycleCompare:
# Purpose: Given two numbers a and b mod n, returns 1 if
#          a is bigger than b, -1 if a is smaller than b,
#          and 0 if a = b.
#          Note that the standard comparison is shifted by
#          by i so that i is the smallest number. E.g if
#          n = 5 and i = 3 then the smallest to largest is
#          3,4,5(0),1,2.
# a: a number mod n
# b: a number mod n
# n: the modulus
# i: the minimum element
# Assumptions: i is a number between 1 and n inclusive.
def shiftingCycleCompare(a,b,n,i):
    #We can shift the numbers by adding n if they are less
    #Then the shifted min
    if a < i:
        a += n
    if b < i:
        b += n
    #Now that the numbers have been shifted we can compare
    if (a > b):
        return 1
    elif (a < b):
        return -1
    else:
        return 0

# compareSets:
# Purpose: Given two sets setA and setB, returns 1 if
#          a is bigger than b, -1 if a is smaller than b,
#          and 0 if a = b.
#          The comparison used is to first sort the elements
#          of each set by the shifting cycle compare and then
#          Compare the sets on lexicographical order.
# setA: a basis element of a matroid
# setB: a basis element of the same matroid
# n: the modulus
# i: the minimum element
# Assumptions: i is a number between 1 and n inclusive.
def compareSets(setA,setB,n,i):
    #Comparing list will compare elementwise in lexicographical order
    listA = sorted([(num-i) % n for num in setA])
    listB = sorted([(num-i) % n for num in setB])
    #Now that the numbers have been shifted we can compare
    if (listA > listB):
        return 1
    elif (listA < listB):
        return -1
    else:
        return 0

# matroidToGrassmannNecklace:
# Purpose: Given a matroid create the Grassmann Necklace
#          associated with it.
#          The Grassmann Necklace is created as a list of
#          n sets which come from the basis of the matroid.
#          the nth item in the list is the smallest basis
#          element of the matroid with respect to the
#          cyclically shifted order <i.
# matroid: a matroid
# n: the size fo the ground set
# Assumptions: the matroid is over the elements {1,...,n}
def matroidToGrassmannNecklace(matroid,n):
    myGrassmanNecklace = []
    for i in range(1,n+1):
        myCompareFunc = lambda x,y: compareSets(x,y,n,i)
        myGrassmanNecklace.append(min(matroid,key=functools.cmp_to_key(myCompareFunc)))
    return myGrassmanNecklace

# grassmannNecklaceToMatroid:
# Purpose: Given a Grassmann Necklace create the matroid
#          associated with it.
#          The matroid is created by considering all subsets
#          of [n] that are size d (the length of each element
#          in the necklace).
#          For each set, it is is larger than or equal to each
#          set s_i in the necklace with respect to <i then it is
#          included as a basis element in the matroid.
# necklace: a Grassmann Necklace
# n: the size fo the ground set
# Assumptions: the necklace is of type (n,d) where n is positive
def grassmannNecklaceToMatroid(necklace,n):
    myMatroid = set()
    groundSet = set(range(1,n+1))
    d = len(necklace[0])
    basisElements = itertools.combinations(groundSet, d)
    for element in basisElements:
        i = 0
        isGreaterThan = True
        while (isGreaterThan and (i<n)):
            if (compareSets(element,necklace[i],n,i+1) == -1):
                isGreaterThan = False
            i += 1
        if isGreaterThan:
            myMatroid.add(frozenset(element))
    return myMatroid

# isPositroid:
# Purpose: Given a matroid determine if it is a positroid
#          A matroid is a positroid if the matroid
#          associated with the grassmann necklace of itself
#          is itself.
# matroid: a matroid
# n: the size fo the ground set
# Assumptions: the matroid is over the elements {1,...,n}
def isPositroid(matroid,n):
    necklace = matroidToGrassmannNecklace(matroid,n)
    if matroid == grassmannNecklaceToMatroid(necklace,n):
        return True
    return False

# printGrassmannNecklace:
# Purpose: Given a Grassmann Necklace print in out.
# n: size of the ground set
# k: rank
# necklace: the Grassmann Necklace
# cyclicOrder: (boolean) if true print the element in the shifted cyclic order
# setsep: the string used to seperate the sets from one another.
# innerSetsetp: the string used to seperate the element inside a set.
# setBraces: Use braces for the sets.
def printGrassmannNecklace(n,k,necklace,cyclicOrder,setsep,innerSetsep,setBraces):
    orderedNecklace = [sorted(list(element)) for element in necklace]
    if cyclicOrder:
        for i in range(n):
            myCompareFunc = lambda x,y: shiftingCycleCompare(x,y,n,i+1)
            orderedNecklace[i] = sorted(orderedNecklace[i],key=functools.cmp_to_key(myCompareFunc))
    print("(", end ="")
    for i in range(n):
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
    print(")")

# printMatroid:
# Purpose: Given a Grassmann Necklace print in out.
# k: rank
# matroid: the matroid
# setsep: the string used to seperate the sets from one another.
# innerSetsetp: the string used to seperate the element inside a set.
# setBraces: Use braces for the sets.
def printMatroid(k,matroid,setsep,innerSetsep,setBraces):
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
        

####################################################
#BEGIN MAIN
####################################################

n = 4
myMatroids = generateMatroids(n,2)
print(len(myMatroids))
for matroid in myMatroids:
    printMatroid(2,matroid," , ","",False)
