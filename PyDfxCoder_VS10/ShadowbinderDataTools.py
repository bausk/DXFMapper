from math import sqrt
from scipy import spatial
from combinatorics import *


def getElementFromPoint(Point, ElementIndex):
    ElementNumber = Point['elementnumbers'][ElementIndex] #Gives us the element number in question that has to be patched
    ElementPointIndex = Point['pointObjectReferences'][ElementIndex].PointNumber #gives actual point index in Elements[ElementNumber]
    return ElementNumber, ElementPointIndex

def NearestNeighbor(Point, GlobalIndex):
    tree = spatial.KDTree(GlobalIndex)
    lowest_distance, index = tree.query(Point, k=1)
    Neighbor = tuple(tree.data[index])
#    lowest_distance = False
#    Neighbor = False
#    for point in GlobalIndex:
#        distance = sqrt((Point[0] - point[0])**2 + (Point[1] - point[1])**2 + (Point[2] - point[2])**2)
#        if not lowest_distance or distance < lowest_distance:
#            lowest_distance = distance
#            Neighbor = point
    return Neighbor, lowest_distance

def Neighborhood (Point, Precision, GlobalIndex):
    t = 10**(-Precision)
    if Point in GlobalIndex:
        return Point
    neighborhood = [
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,-t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,-t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,-t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,0,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,0,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,0,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,-t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,-t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,-t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,0,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,0,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,-t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,-t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,-t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,0,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,0,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,0,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,t,t)))
                ]
    for point in neighborhood:
        if point in GlobalIndex:
            return point
    GlobalIndex.append(Point)
    return Point

def NeighborhoodRaw (Point, Precision, GlobalIndex):
    t = 10**(-Precision)
    if Point in GlobalIndex:
        return Point
    neighborhood = [
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,-t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,-t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,-t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,0,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,0,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,0,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (-t,t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,-t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,-t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,-t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,0,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,0,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (0,t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,-t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,-t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,-t,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,0,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,0,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,0,t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,t,-t))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,t,0))),
                tuple(round(sum(pair),Precision) for pair in zip(Point, (t,t,t)))
                ]
    for point in neighborhood:
        if point in GlobalIndex:
            return point
    return Point    
