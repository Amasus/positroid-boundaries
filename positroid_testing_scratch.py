from Matroids import *
from Positroids import *


basis1 = {frozenset({1, 2, 4, 5}),frozenset({3, 4, 5}),frozenset({1, 2})}
emptybasis = {}
basis2 = {frozenset({1, 2, 5}),frozenset({3, 4, 5}),frozenset({1, 2,4})}

#answer = generateMatroidsSlice(4,0,0)
answer = generateMatroids(4,2)
print(answer)

matroid1 = answer[13]
print(matroid1)

GN = matroidToGrassmannNecklace(matroid1,4)
print(GN)
print(isGrassmannNecklace(GN,4,2))
#size_check = sameSizeCheck(basis2)

#print (size_check)

