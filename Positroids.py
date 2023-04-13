#Author: Everett Sullivan.
#Note: This program was written for Python 3.
#Purpose: The purpose of this code is for generating Le Diagrams, Matroids, Positroid, Grassman Necklaces, and finding the assoicated objects under bijection with one another.

import sys
from Matroids import *
import math
import itertools #needed for generate all k element subsets
from itertools import chain
import functools #needed for custom compare functions
import copy

from timeit import default_timer as timer




####################################################
#Grassman Necklaces
####################################################

#cyclicShift:
#Purpose: In order to simulate the <_i linear ordering
#on a cyclic set [n], take all numbers smaller than i
#and move to after n
#a: (int) number to be shifted
#n: size of the cycle
#i: linear order of interest
def cyclicShift(a,n,i):
    if i >n or i <1:
        raise ValueError('i must be in [1, n]')
    #We can shift the numbers by adding n if they are less
    #Then the shifted min
    if a < i:
        a += n
    return a

# shiftingCompare:
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
def shiftingCycleCompare(a,b,n,i):
    a = cyclicShift(a, n, i)
    b = cyclicShift(a, n, i)    
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
# setA: a frozenset
# setB: a frozenset 
# n: the modulus
# i: the minimum element
#NOTE: this is a strict lex ordering. SetA and SetB need not be of the same size

#rangeCheck:
#Purpose: to check that all elements in a set are between 1 and n inclusive
#setA: a frozen set
#n: integer defining bound
def rangeCheck(setA, n):
    return all(a <= n for a in setA) and all(a>=1 for a in setA)

def compareSets(setA,setB,n,i):
    #Check that all elements of the set are in the right range
    if not rangeCheck(setA, n):
        raise ValueError('SetA has some values out of range')
    if not rangeCheck(setB, n):
        raise ValueError('SetB has some values out of range')  


    #Comparing list will compare elementwise in lexicographical order
    # Changing this. If x = [4,3,1], n = 5, i = 2
    # sorted([(num-i) % n for num in x]) gives [1,2,4]
    # listA = sorted([(num-i) % n for num in setA])
    # listB = sorted([(num-i) % n for num in setB])


    #shift the elements of the set
    listA = [cyclicShift(a,n,i) for a in setA]
    listA.sort()
    listB = [cyclicShift(b,n,i) for b in setB]
    listB.sort()

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
# matroid: (set of Frozen sets) bases set of a matroid 
# n: the size of the ground set, note, we assume that the 
# matroid is defined over a cyclically ordered set.

def matroidToGrassmannNecklace(matroid,n):
    if not isMatroidBases(matroid):
        raise ValueError("matroid is not a bases set")
    if any(not rangeCheck(basis, n) for basis in matroid):
        raise ValueError("some basis set is not in range")

    myGrassmanNecklace = []
    if len(matroid) == 0:
        for i in range(1,n+1):
            myGrassmanNecklace.append([]);
    else:
        for i in range(1,n+1):
            myCompareFunc = lambda x,y: compareSets(x,y,n,i)
            myGrassmanNecklace.append(min(matroid,key=functools.cmp_to_key(myCompareFunc)))
    return myGrassmanNecklace

#isGrassmannNecklace:
#Purpose: Takes a list of frozen sets and checks if it 
#is a Grassmann necklace of the right type
#GN: a list of frozen sets
#n: [n] is the ground set
#d: each set is of size d
def isGrassmannNecklace(GN, n, d):
    # Check that GN has the right shape
    # Check if all the sets are of the right size
    if any(len(element) != d for element in GN ):
        print('not all elements of size {d}')
        return False
    if any(not rangeCheck(element, n) for element in GN):
        print('not all elements contained in [{n}]')
        return False
    if len(GN) != n:
        print("GN has the wrong length")
        return False
    
    #If GN has the right shape, check the GN conditions
    isGN = True
    for i in range(1,n+1):
        if i in GN[i-1]:
            cond1Set = GN[i-1] - {i}
            cond1 = cond1Set.issubset(GN[i])
            isGN = isGN and cond1
        else:
            cond2 = GN[i-1]==GN[1] 
            isGN = isGN and cond2
    return isGN     

# grassmannNecklaceToPositroid:
# Purpose: Given a Grassmann Necklace create the Positroid
#          associated with it.
#          The matroid is created by considering all subsets
#          of [n] that are size d (the length of each element
#          in the necklace).
#          For each set, it is is larger than or equal to each
#          set s_i in the necklace with respect to <i then it is
#          included as a basis element in the matroid.
# necklace: (List of frozen Sets)a Grassmann Necklace
# n: the size of the ground set

def grassmannNecklaceToPositroid(necklace,n,k):
    myMatroid = set()
    groundSet = set(range(1,n+1))
    basisElements = itertools.combinations(groundSet, k)
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
    if matroid == grassmannNecklaceToPositroid(necklace,n):
        return True
    return False





# printGrassmannNecklace:
# Purpose: Given a Grassmann Necklace print in out.
# n: size of the ground set
# k: rank
# necklace: the Grassmann Necklace TODO: Everett, what's the data structure here?
# cyclicOrder: (boolean) if true print the element in the shifted cyclic order
# setsep: the string used to seperate the sets from one another.
# innerSetsetp: the string used to seperate the element inside a set.
# setBraces: Use braces for the sets.
def printGrassmannNecklace(n,k,necklace,cyclicOrder,setsep = ',',innerSetsep= ','
                         ,setBraces = True):
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


####################################################
#Le Diagrams
####################################################

# verifyLeDiagram:
# Purpose: Verify that a Le Diagram is correct.
#   it must be that n and k are non-negative integers
#   with 0 <= k <= n.
#   Addtionally the YoungDiagram must fit inside the
#   box of size k * (n-k) and satify the plus
#   property
# leDiagram: a proposed Le Diagram
# Assumptions: that leDiagram = (n,k,filledYoungTab)
#   n and k are integers, and filledYoungTab is a
#   (possibly emtpy) list of (possibly empty) lists
#   that contain only 1's (+'s) and 0's
def verifyLeDiagram(leDiagram):
    n = leDiagram[0];
    k = leDiagram[1];
    filledYoungTab = leDiagram[2];
    verified = False;

    # Check for proper n and k.
    if n < 0:
        print("ERROR: n must be a non-negative integer.")
    elif (k < 0) or (k > n):
        print("ERROR: k must be a non-negative integer less than.")
    #check the Young Tableau fits inside the box
    elif len(filledYoungTab) > k:
        print("ERROR: Young Tableau must have no more than k parts.")
    elif (len(filledYoungTab) != 0) and (len(filledYoungTab[0]) > (n-k)):
        print("ERROR: Young Tableau parts must be no larger than (n-k).")
    #Verify tha the Young Tableau is in fact a Young Tableau
    else:
        partLength = [len(part) for part in filledYoungTab]
        if (not all(x<y for x,y in zip(partLength,parthLength[1:]))):
            print("ERROR: Young Tableau must have non-increasing part lengths.")
        #Verify that the Young Tableau satisfies the + property.
        elif (not plusProperty(filledYoungTab)):
            print("ERROR: Young Tableau must satisify the + property.")
        #All critiera are meet.
        else:
            verified = True
    return verified


# plusProperty:
# Purpose: Verify that a Young Diagram filled with +'s and 0's
#   has the property that for any 0 in the diagram, either
#   every cell above it is zero, or every cell to its left
#   is zero.
# youngTab: a Young Tableau (a list of lists)
# Assumptions: the Young Tableau is a (possibly empty) list
#   of (possibly empty) lists filled with 0's and +'s
#   (represented by 1's)
def plusProperty(filledYoungTab):
    numParts = len(filledYoungTab)
    #any zeros in the first column or row will always
    #have a path of zeros out, so we skip to the second
    for i in range(1,numParts):
        for j in range(1,len(filledYoungTab[i])):
            if (filledYoungTab[i][j] == 0):
                zerosAbove = all(x==0 for x in filledYoungTab[i][:j])
                zerosLeft = all(a[j]==0 for a in filledYoungTab[:i])
                zeroPath = (zerosAbove or zerosLeft)
                if (not zeroPath):
                    return False
    return True

#nextYoungDiagram:
#Purpose: to iterate through all Young Tableaus with no more
#   Then maxParts parts where each part is no larger than
#   maxPartLength.
#   To start, pass it "None", iterating after the last
#   Tableau will return none.
#   Otherwise it starts with the empty Tableau and ends
#   with the full Tableau by incrementmenting the first part
#   that is less than the first part, and setting all parts after
#   that to zero, otherwise increment the first part.
#maxParts: the largest number of parts a Tableau may hold
#MaxPartLength: the largest a part may be.
#currentYoungTab: the current Young Tableau
#Assumptions: That Young Tableau is either None or a Young
#   Tableau with no more than maxParts where each Part is
#   no larger than maxPartLength.
#Notes: In this method a Young Tableau is repseented as a
#   (possibly empty) list of part lengths, and is padded
#   with 0's (empty parts) to the size of maxParts.
def nextYoungDiagram(maxParts,maxPartLength,currentYoungTab):
    #Create a "empty" Young Tableau of maxParts empty parts
    if currentYoungTab is None:
        currentYoungTab = [0 for i in range(0,maxParts)]
        return currentYoungTab
    #If the Young Tableau has no parts there is only one such
    #   object, so we end.
    elif ((maxParts == 0) or (maxPartLength == 0)):
        return None
    #If the Young Tableau is full, this is the last object.
    elif (currentYoungTab[maxParts-1] == maxPartLength):
        return None
    #Else we advance to the next Tableau
    else:
        firstSmallestIndex = currentYoungTab.index(min(currentYoungTab))
        currentYoungTab[firstSmallestIndex] += 1
        for i in range(firstSmallestIndex+1,maxParts):
            currentYoungTab[i] = 0
    return currentYoungTab

#nextPlusZeroRow:
#Purpose: to iterate through all possible +,0 lists
#   that satify the plus property from the mask.
#   To start, pass it "None", iterating after the last
#   row will return none.
#   Otherwise it starts with a row of all zeros and ends
#   with a row of all +'s (1's) by setting the rightmost
#   zero to a plus and setting all indexs after that to
#   zero IF it is not below a + (1) in the mask (Since
#   we want to satisfy the plus property)
#Purpose to iterate though all list (of zome size n)
#topPlusMask: a mask that indicates which columns
#   have a zero above the current index. (may be longer
#   then currentRow) A list of 0's and 1's (+'s)
#currentRow: the current Row (a (possibly empty) list
#   of 0's and 1's)
#Assumptions:
#Notes: when starting, the currentRow will start with
#   the same length as the mask.
def nextPlusZeroRow(topPlusMask,currentRow):
    #Create a row of all zeros (the first object)
    if currentRow is None:
        return [0 for i in topPlusMask]
    #If the row is all +'s (the last object) we are done.
    elif all([x==1 for x in currentRow]):
        return None
    #find the rightmost 0, make is a plus and change all
    # +'s to the right to zero IF they are not in the mask
    # (since that would violate the plus property)
    else:
        lastZeroIndex = len(currentRow) - 1 - currentRow[::-1].index(0)
        currentRow[lastZeroIndex] = 1
        for i in range(lastZeroIndex+1,len(currentRow)):
            if (topPlusMask[i] != 1):
                currentRow[i] = 0
    return currentRow

#nextFilledYoungTabOfShape:
#Purpose to iterate though all young diagrams filled
#   with 0's and 1's that satify the plus property.
#   This is done by starting with None, return the youngTab
#   filled with all 0's, the next object is obtained by finding
#   the starting at the bottom, and incrementing a row.
#   if the row is ful, zero it out and increment the next row
#   above
#currentFilledYoungTab: a list of list that contains 0's
#   and 1's that satify the + property and has shape
#   youngTab
#youngTab: a young Tableau, given as a list of part lengths
#Assumptions: That the current shape of currentFilledYoungTab is
#   of the shape given by Young Tab
def nextFilledYoungTabOfShape(currentFilledYoungTab,youngTab):
    if currentFilledYoungTab is None:
        #Return a Le Diagram of all zeros.
        currentFilledYoungTab = [[0 for i in range(0,partLen)] for partLen in youngTab]
        return currentFilledYoungTab
    #If the Le Diagram is all +'s it is the last diagram
    elif all([all([x==1 for x in currentRow]) for currentRow in currentFilledYoungTab]):
        return None
    else:
        #Find the first zero part (if it exists)
        #We only need to consider the nonzero parts
        if youngTab[len(youngTab)-1] != 0:
            firstZeroPart = len(youngTab)
        else:
            firstZeroPart = youngTab.index(0)
        #the bottommost non-full (not all plus's) row is incremented and the rows below it zeroed out.
        for i in reversed(range(firstZeroPart)):
            currentPart = currentFilledYoungTab[i];
            #The mask with have a 1 (+) if any cell above it has a 1.
            currentMask = [any([currentFilledYoungTab[k][j]==1 for k in range(i) ]) for j in range(len(currentPart))]
            currentPart = nextPlusZeroRow(currentMask,currentPart)
            if currentPart is not None:
                currentFilledYoungTab[i] = currentPart
                return currentFilledYoungTab
            else:
                currentPart = nextPlusZeroRow(currentMask,currentPart)
                currentFilledYoungTab[i] = currentPart

#nextLeDiagam:
#Purpose to iterate though all Le Diagrams.
#   A Le Diagram is a tuple (n,k,filledYoungTableau)
#   such that 0 <= n <= k and filledYoungTableau is a
#   Young Tableau that fits inside a k*(n-k) box, that is
#   also filled with 0's and 1's (+'s) such that the plus
#   property holds.
#   Thus filledYOungTalbeau is a list of length k (padded
#   with empty lists to the size of k) of lists filled with
#   0's and 1's.
#leDiagram: a Le Diagram (or None if we are at the beginning)
#n,k: non-negative integers.
#Assumptions: 0 <= k <= n, leDiagram (if not None) matches
#   with n and k.
def nextLeDiagam(leDiagram,n,k):
    if leDiagram is None:
        #Check if we have a degerate case
        if ((n==0) or (k==0) or (n==k)):
            leDiagram = (n,k,[[] for i in range(k)])
            return leDiagram
        else:
            currentShape = nextYoungDiagram(k,n-k,None)
            filledYoungTab = nextFilledYoungTabOfShape(None,currentShape)
            leDiagram = (n,k,filledYoungTab)
            return leDiagram
    else:
        currentShape = [len(part) for part in leDiagram[2]]
        filledYoungTab = nextFilledYoungTabOfShape(leDiagram[2],currentShape)
        if filledYoungTab is not None:
            leDiagram = (n,k,filledYoungTab)
            return leDiagram
        else:
            #If fill is maxed, get next shape
            currentShape = nextYoungDiagram(k,n-k,currentShape)
            if currentShape is not None:
                leDiagram = (n,k,nextFilledYoungTabOfShape(None,currentShape))
                return leDiagram
            else:
                #If both shape and fill are maxed, we are done.
                return None
            
# leDiagramASCII:
# Purpose: Print out a Le Diagram in ASCII
# leDiagram: a Le Diagram (n,k,filledYoungTab) or a filledYoungTab.
# Assumptions: that leDiagram is a proper Le Diagram
def leDiagramASCII(leDiagram):
    #If not a tuple, just a filled Young diagram
    if (type(leDiagram) is not tuple):
        print("*");
        for part in leDiagram:
            print(":",end="");
            for x in part:
                print(x,end="")
            print("");
        print("");
    #Else we have the full Le Diagram
    else:
        n = leDiagram[0]
        k = leDiagram[1]
        print("*");
        for part in leDiagram[2]:
            print(":",end="");
            line = ""
            for i in range(n-k):
                if i < len(part):
                    line += str(part[i])
                else:
                    line += "-"
            print(line);
        print("");

# leDiagramTex:
# Purpose: Create the LaTeX code to print out a
#   Le Diagram in tikz.
# leDiagram: a Le Diagram a tuple (n,k,filledYoungTab)
# Assumptions: that leDiagram is a proper Le Diagram
def leDiagramTex(leDiagram):
    n = leDiagram[0];
    k = leDiagram[1];
    filledYoungTab = leDiagram[2];
    partLength = [len(part) for part in filledYoungTab]
    numParts = len(filledYoungTab)
    #Padd the partLength with 0's so that when the label printer runs there is always a part length to check.
    partLength += [0 for i in range(k-numParts+1)]
    print("\\begin{center}")
    print("\t\\begin{tikzpicture}[scale=1]")
    print("\t\t\draw[dashed] (0,0) rectangle (" + str(int(n-k)) + "," + str(int(k)) + ");\n")
    
    for i in range(numParts):
        if (len(filledYoungTab[i]) != 0):
            print("\t\t\draw[very thick] (0," + str(k-i-1) + ") grid ++(" + str(int(len(filledYoungTab[i]))) + ",1);")

    print("")

    for i in range(numParts):
        for j in range(partLength[i]):
            if (filledYoungTab[i][j] == 0):
                print("\t\t\\node at (" + str(j) + ".5," + str(k-i-1) + ".5) {0};")
            else:
                print("\t\t\\node at (" + str(j) + ".5," + str(k-i-1) + ".5) {+};")

    print("")

    currentLabel = 1
    currentDepth = 0
    currentWidth = (n-k)
    while (currentLabel <= n) :
        if partLength[currentDepth] < currentWidth:
            print("\t\t\\node[below] at (" + str(currentWidth-1) + ".5," + str(k-currentDepth) + "  ) {" + str(currentLabel) + "};")
            currentWidth -= 1
        else:
            print("\t\t\\node[right] at (" + str(currentWidth) + "  ," + str(k-currentDepth-1) + ".5) {" + str(currentLabel) + "};")
            currentDepth += 1
        currentLabel += 1
                
    
    print("\t\\end{tikzpicture}")
    print("\\end{center}")

####################################################
#Functors, bijections, etc.
####################################################




# taxiCabCloser:
# Purpose: Given two points and a reference point,
#          returs -1,0, or 1 if the first point is
#          closer, equal, or farther away to the
#          reference point then second point using
#          the taxi cab metric.
# firstPoint: a tuple (x,y)
# secondPoint: a tuple (x,y)
# refPoint: a tuple (x,y)
# Assumptions: None
def taxiCabCloser(firstPoint,secondPoint,refPoint):
    relPoint1 = (firstPoint[0] - refPoint[0],firstPoint[1] - refPoint[1])
    relPoint2 = (secondPoint[0] - refPoint[0],secondPoint[1] - refPoint[1])
    taxiCabDist1 = abs(relPoint1[0]) + abs(relPoint1[1])
    taxiCabDist2 = abs(relPoint2[0]) + abs(relPoint2[1])
    if taxiCabDist1 < taxiCabDist2:
        return -1
    elif taxiCabDist1 > taxiCabDist2:
        return 1
    else:
        return 0

# getNearestNWPlus:
# Purpose: Given a  filled Young Tableau return a
#   Young Tableau of the same shape where each
#   cell contains the coordinates of the cell cloest
#   to itself when looking above and to the left that
#   has a 1 (+).
#   coordinates are given row then column when viewed
#   from the top left.
#   If no such cell exits, it contains None.
# filledYoungTab: a Young Tableau given as a list of
#   lists that contains 0's and 1's (+'s).
# Assumptions: filledYoungTab satisfies the plus
#   property
def getNearestNWPlus(filledYoungTab):
    nearestNWPlus = copy.deepcopy(filledYoungTab)
    if (len(filledYoungTab) == 0):
        return nearestNWPlus
    elif (len(filledYoungTab[0]) == 0):
        return nearestNWPlus
    filledYoungTab = filledYoungTab + [[]]
    if (filledYoungTab[0][0] == 1):
        nearestNWPlus[0][0] = (0,0)
    else:
        nearestNWPlus[0][0] = None
    #Find the nearest plus for each square in the first row
    for i in range(1,len(filledYoungTab[0])):
        if (filledYoungTab[0][i] == 1):
            nearestNWPlus[0][i] = (0,i)
        else:
            nearestNWPlus[0][i] = nearestNWPlus[0][i-1]
    firstZeroPart = [len(part) for part in filledYoungTab].index(0)
    #Find the nearest plus for each suare in the the first column
    for i in range(1,firstZeroPart):
        if (filledYoungTab[i][0] == 1):
            nearestNWPlus[i][0] = (i,0)
        else:
            nearestNWPlus[i][0] = nearestNWPlus[i-1][0]
    #Now consider the "interior" of the tableau.
    for i in range(1,firstZeroPart):
        for j in range(1,len(filledYoungTab[i])):
            if (filledYoungTab[i][j] == 1):
                nearestNWPlus[i][j] = (i,j)
            elif nearestNWPlus[i][j-1] is None:
                nearestNWPlus[i][j] = nearestNWPlus[i-1][j]
            elif nearestNWPlus[i-1][j] is None:
                nearestNWPlus[i][j] = nearestNWPlus[i][j-1]
            elif (taxiCabCloser(nearestNWPlus[i-1][j],nearestNWPlus[i][j-1],(i,j)) == -1):
                nearestNWPlus[i][j] = nearestNWPlus[i-1][j]
            else:
                nearestNWPlus[i][j] = nearestNWPlus[i][j-1]
    return nearestNWPlus

# getLabelNums:
# Purpose: Returns arrays thare are the row numbers
#   and column numbers of the algoirthm given in
#   leDiagramToGrassmannNecklace
# n: size of the ground set
# kt: the rank
# shape: a partition with max size n and max k parts.
# Assumptions: That shape is as given.
def getLabelNums(n,k,shape):
    rowNums = [0 for i in range(n-k)]
    colNums = [0 for i in range(k)]
    currentLabel = 1
    currentDepth = 0
    currentWidth = (n-k)
    numParts = len(shape)
    #Pad the partLength with 0's so that when the label printer runs there is always a part length to check.
    shape += [0 for i in range(k-numParts+1)]
    while (currentLabel <= n) :
        if shape[currentDepth] < currentWidth:
            rowNums[currentWidth-1] = currentLabel
            currentWidth -= 1
        else:
            colNums[currentDepth] = currentLabel
            currentDepth += 1
        currentLabel += 1
    return (rowNums,colNums)

def leDiagramToGrassmannNecklace(leDiagram):
    n = leDiagram[0]
    k = leDiagram[1]
    # if n is zero return an empty array
    if n == 0:
        return []
    # if k is zero return a n-size array of empty sets.
    elif k == 0:
        return [frozenset() for i in range(n)]
    # if n=k is zero return a n-size array of sets with every
    #   element from 1 to n.
    elif n == k:
        onlyElement = frozenset([1+i for i in range(n)])
        return [onlyElement for i in range(n)]
    #else we have a non-degenerate case
    else:
        filledYoungTab = leDiagram[2]
        nearestNWPlus = getNearestNWPlus(filledYoungTab)
        nearestNWPlus.append([])
        (rowNums,colNums) = getLabelNums(n,k,[len(part) for part in nearestNWPlus])
        #The Grassman necklace always starts with the col nums.
        necklace = [frozenset(colNums)]
        currentIndex = 2
        currentDepth = 0
        currentColumn = n-k-1
        while (currentIndex <= n):
            #this part can be made faster by handeling all the cells outside
            #the shape at once.
            #If outside the shape, the set is just the col nums.
            if ( (len(nearestNWPlus[currentDepth]) - 1) < currentColumn ):
                necklace.append(frozenset(colNums))
                if (currentColumn == 0):
                    currentDepth += 1
                else:
                    currentColumn -= 1
            else:
                myNums = colNums.copy()
                nextPlus = nearestNWPlus[currentDepth][currentColumn]
                while nextPlus is not None:
                    myNums[nextPlus[0]] = rowNums[nextPlus[1]]
                    if ((nextPlus[0] == 0) or (nextPlus[1] == 0)):
                        nextPlus = None
                    else:
                        nextPlus = nearestNWPlus[nextPlus[0]-1][nextPlus[1]-1]
                necklace.append(frozenset(myNums))
                if ((len(nearestNWPlus[currentDepth+1])-1 == currentColumn) or (currentColumn == 0)):
                    currentDepth += 1
                else:
                    currentColumn -= 1
            currentIndex += 1
        return necklace

def grassmannNecklaceToLeDiagram(n,k,necklace):
    # if n is zero return an empty array
    if n == 0:
        return (n,k,[])
    # if k is zero return a k-size list of empty lists.
    elif k == 0:
        return (n,k,[[] for i in range(n)])
    elif n == k:
        return (n,k,[])
    #else we have a non-degenerate case
    else:
        colNums = sorted(list(necklace[0]))
        rowNums = sorted(list(set([(i+1) for i in range(n) ]).difference(necklace[0])))
        rowNums = rowNums[::-1]
        shape = [0 for i in range(k)]
        shape[0] = (n-k) - colNums[0] + 1
        shape[k-1] = n - colNums[k-1]
        for i in range(1,k-1):
            shape[i] = shape[i-1] + colNums[i] - colNums[i+1] + 1
        filledYoungTab = [[0 for i in range(part)] for part in shape]
        for i in range(1,n):
            colLabels = sorted(list(necklace[0] - necklace[i]))
            rowLabels = sorted(list(necklace[i] - necklace[0]))
            rowLabels = rowLabels[::-1]
            for j in range(len(colLabels)):
                xCord = rowNums.index(rowLabels[j])
                yCord = colNums.index(colLabels[j])
                filledYoungTab[yCord][xCord] = 1
        return (n,k,filledYoungTab)
                    
            

####################################################
#Testing
####################################################

def unitTest1():
    youngTab = [2,2]
    filledYoungTab = [[1,0],[0,1]]
    leDiagramASCII((4,2,filledYoungTab))
    printGrassmannNecklace(4,2,leDiagramToGrassmannNecklace((4,2,filledYoungTab)),True," , ","",False)
    

####################################################
#Under construction
####################################################           

def positroidChordTex(positroidChord):
    n = positroidChord[0]
    angles = [360.0/n,2*math.pi/n]
    strAngles = [f"{i*angles[0]:{7}.{6}}" for i in range(n)]
    print("\\begin{center}")
    print("\t\\begin{tikzpicture}[scale=1]")

    print("\t\t\\draw (0,0) circle (1);")
    for i in range(n):
        print("\t\t\\filldraw [black] (" + strAngles[i] + ":1) circle (2pt);")
        print("\t\t\draw (" + strAngles[i] + ":1.5) node {" + str(i+1) + "};")        

    
    print("\t\\end{tikzpicture}")
    print("\\end{center}")    

####################################################
#BEGIN MAIN
####################################################

##n = 4
##k = 2
##myMatroids = generateMatroids(n,k)
##myNecklacess = [matroidToGrassmannNecklace(myMatroid,n) for myMatroid in myMatroids]
##res = []
##[res.append(x) for x in myNecklacess if x not in res]
##for neck in res:
##    print(neck)
##print(len(myMatroids))
##for matroid in myMatroids:
##    print(matroid)
##    printMatroid(k,matroid," , ","",True)
##    necklace = matroidToGrassmannNecklace(matroid,n)
##    printGrassmannNecklace(n,k,necklace,True," , ","",False)
##    print("neck")
##    print(necklace)
##    positroid = grassmannNecklaceToPositroid(necklace,n,k)
##    printMatroid(k,positroid," , ","",True)
##    print("---------------------------------")


start = timer()

for n in range(6):
    for k in range(n+1):
        myMatroids = generateMatroids(n,k)
        myNecklacess = [frozenset(matroidToGrassmannNecklace(myMatroid,n)) for myMatroid in myMatroids]
        res = []
        [res.append(x) for x in myNecklacess if x not in res]
        print(len(res),end = " ")
    print("");

end = timer()
print(end - start)

start = timer()

for n in range(6):
    for k in range(n+1):
        count = 0
        currentObject = None
        currentObject = nextLeDiagam(currentObject,n,k)
        while currentObject is not None:
            count += 1
            currentObject = nextLeDiagam(currentObject,n,k)
        print(f'{count:{" "}{7}}',end = " ")
    print("");

end = timer()
print(end - start)

youngTab = [[1,0,1,0],[0,0,1],[1,0]]

currentTab = None
currentTab = nextYoungDiagram(3,2,currentTab)
while currentTab is not None:
    print(currentTab)
    currentTab = nextYoungDiagram(3,2,currentTab)

mask = [0,1,0,1]
currentRow = None
currentRow = nextPlusZeroRow(mask,currentRow)
while currentRow is not None:
    print(currentRow)
    currentRow = nextPlusZeroRow(mask,currentRow)

##youngTab = [2,1]
##filledYoungTab = None
##filledYoungTab = nextFilledYoungTabOfShape(filledYoungTab,youngTab)
##while filledYoungTab is not None:
##    leDiagramASCII((4,2,filledYoungTab))
##    printGrassmannNecklace(4,2,leDiagramToGrassmannNecklace((4,2,filledYoungTab)),True," , ","",False)
##    filledYoungTab = nextFilledYoungTabOfShape(filledYoungTab,youngTab)
##
##unitTest1()


n=5
k=2
currentObject = None
currentObject = nextLeDiagam(currentObject,n,k)
while currentObject is not None:
    leDiagramASCII(currentObject)
    myNecklace = leDiagramToGrassmannNecklace(currentObject)
    printGrassmannNecklace(5,2,myNecklace,True," , ","",False)
    myLeDiagram = grassmannNecklaceToLeDiagram(5,2,myNecklace)
    leDiagramASCII(myLeDiagram)
    currentObject = nextLeDiagam(currentObject,n,k)
    print("--------------------------------------------")
    print("--------------------------------------------")

##n=4
##k=2
##currentObject = None
##currentObject = nextLeDiagam(currentObject,n,k)
##while currentObject is not None:
##    leDiagramASCII(currentObject)
##    currentObject = nextLeDiagam(currentObject,n,k)
##
##n=4
##k=2
##currentObject = None
##currentObject = nextLeDiagam(currentObject,n,k)
##while currentObject is not None:
##    leDiagramTex(currentObject)
##    currentObject = nextLeDiagam(currentObject,n,k)

#print(plusProperty([]))
#print(plusProperty([[0]]))
#print(plusProperty([[1]]))
#print(plusProperty([[0,1,0,1]]))
#print(plusProperty([[0],[1],[1],[0]]))
#print(plusProperty([[0,0,1,0],[0,1,1,0],[0,0]]))
#print(plusProperty([[0,0,1,0],[0,1,1,0],[1,0]]))

#print(plusProperty([[0,0,1,0],[0,1,1,0],[1,1]]))

#leDiagramTex((8,3,youngTab))

#leDiagramTex((5,2,[]))
#leDiagramTex((5,2,[[1]]))
#leDiagramTex((5,2,[[1,0,1]]))
#leDiagramTex((5,2,[[1,0,1],[1]]))
#leDiagramTex((5,2,[[1,0],[1,0]]))
#leDiagramTex((5,2,[[1,0,1],[1,1,1]]))

#positroidChordTex((11,[[1,2],[2,3],[3,4],[6,9,10]]))
    
