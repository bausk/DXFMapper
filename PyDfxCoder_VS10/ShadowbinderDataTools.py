def getElementFromPoint(Point, ElementIndex):
    ElementNumber = Point['elementnumbers'][ElementIndex] #Gives us the element number in question that has to be patched
    ElementPointIndex = Point['pointObjectReferences'][ElementNumber].PointNumber #gives actual point index in Elements[ElementNumber]
    return ElementNumber, ElementPointIndex