from Matroids import *
from Positroids import *


basis1 = {frozenset({1, 2, 4, 5}),frozenset({3, 4, 5}),frozenset({1, 2})}
emptybasis = {}
basis2 = {frozenset({1, 2, 5}),frozenset({3, 4, 5}),frozenset({1, 2,4})}

#answer = generateMatroidsSlice(4,0,0)
answer = generateMatroids(4,2)
#print(answer)
matroid1 = answer[0]
print(f"Consider the following Matroid: {matroid1}")

GN = basesToGrassmannNecklace(matroid1,4)

print(f"GN is {GN}")
print(f"GN is a Grassmann Necklace: {isGrassmannNecklace(GN,4,2)}")

positroid1 = grassmannNecklaceToPositroid(GN, 4,2)
print(f"The Positroid assoicated GN is: {positroid1}")
print(f"For reference, the matroid generating GN is: {matroid1}")
print(f"This matroid is a positroid: {isPositroid(matroid1, 4)}")
#print (size_check)

candidate = {frozenset({1,2,5}), frozenset({1,2,4}), frozenset({1,2,3}), frozenset({1,4,5}), frozenset({2,4,5}), frozenset({3,4}), frozenset({1,3,5}), frozenset({2,3,5})}

candidate2 = {frozenset({1,2,5,6}), frozenset({1,2,3,4}), frozenset({3,4,5,6}), frozenset({1,2,7}), frozenset({7,3,4}), frozenset({5,6,7})}


hasCircuitCond3(candidate)