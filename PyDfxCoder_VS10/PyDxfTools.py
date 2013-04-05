
def GetPoints(Entity, Precision):
    #Points = []
    if Entity.dxftype == "LINE":
        point1 = Entity.start
        point1 = tuple([round(x, Precision) for x in point1])
        point2 = Entity.end
        point2 = tuple([round(x, Precision) for x in point2])
        return [point1, point2]
    elif Entity.dxftype == "CIRCLE":
        point = Entity.center
        point = tuple([round(x, Precision) for x in point])
        return [point]
    elif Entity.dxftype in ("LWPOLYLINE",):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            Points.append(point + (0.0,))
        return Points
    elif Entity.dxftype in ("SOLID", "FACE"):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            if len(point) == 2:
                Points.append(point + (0.0,))
            else:
                Points.append(point)
        return Points
    elif Entity.dxftype in ("POLYLINE",):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            if len(point) == 2:
                Points.append(point + (0.0,))
            else:
                Points.append(point)
        return Points

def GetRawPoints(Entity, Precision):
    #Points = []
    if Entity.dxftype == "LINE":
        point1 = Entity.start
        point1 = tuple([round(x, Precision) for x in point1])
        point2 = Entity.end
        point2 = tuple([round(x, Precision) for x in point2])
        return [point1, point2]
    elif Entity.dxftype == "CIRCLE":
        point = Entity.center
        point = tuple([round(x, Precision) for x in point])
        return [point]
    elif Entity.dxftype in ("LWPOLYLINE",):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            Points.append(point)
        return Points
    elif Entity.dxftype in ("SOLID", "FACE"):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            Points.append(point)
        return Points
    elif Entity.dxftype in ("POLYLINE",):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            Points.append(point)
        return Points

def Overkill(Entities, Precision):
    PurgedEntities = dict(enumerate(Entities))
    print "Overkilling the DXF dataset (alpha version feature)\n"
    ReferencePointArray = {}
    for index, Entity in enumerate(Entities) :
        #1. Delete duplicate points in polys
        EntityPoints = [tuple(y for y in x) for x in GetRawPoints(Entity, Precision)]
        if Entity.dxftype in ("LWPOLYLINE", "POLYLINE"):
            NewPoints = []
            for pointindex, EntityPoint in enumerate(EntityPoints):
                if not EntityPoint in NewPoints: NewPoints.append(EntityPoint)
                #else: Entities[index].points = RemovePoint(Entity, pointindex)
            Entities[index].points = tuple(NewPoints)
        
        #2. Delete duplicate objects
        EntityPoints = tuple(sorted((tuple(y for y in x) for x in GetRawPoints(Entity, Precision))))
        if not EntityPoints in ReferencePointArray :
            ReferencePointArray[EntityPoints] = index
        else :
            del PurgedEntities[index]

    return PurgedEntities.values()