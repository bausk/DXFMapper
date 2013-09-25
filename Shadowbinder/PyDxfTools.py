import sys
from io import StringIO
from collections import OrderedDict
from dxfgrabber.drawing import Drawing
from dxfgrabber.entitysection import EntitySection
import numpy as np

def getDrawing(InputFile, GrabBlocks) :
    try:
        InputString = unicode(open(InputFile).read().decode('utf-8'))
    except:
        sys.exit(0)
    InputStream = StringIO(InputString)
    options = {
        'grab_blocks': GrabBlocks
    }
    return Drawing(InputStream, options)

def getEntities(InputFileList, GrabBlocks) :
    Entities = None
    if InputFileList and not (type(InputFileList) is list):
        InputFileList = [InputFileList]
    for InputFile in InputFileList:
        InputDXF = getDrawing(InputFile, GrabBlocks)
        NewEntities = InputDXF.entities
        if not Entities:
            Entities = NewEntities
        else:
            Entities._entities = Entities._entities + NewEntities._entities
        print "Reading file '{}'... {} entities.".format(InputFile, len(NewEntities))
    return Entities

def CheckCrossProduct(p1, p2, p3):
    vector1 = np.array([x[1] - x[0] for x in zip(p1,p2)])
    vector2 = np.array([x[1] - x[0] for x in zip(p2,p3)])
    if np.cross(vector1, vector2)[2] > 0:
        return True
    else:
        return False

def GetPoints(Entity, Precision, CheckDirection='No'):
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
        returnPoints = list(OrderedDict.fromkeys(Points))
        if CheckDirection == 'Yes':
            if not CheckCrossProduct(returnPoints[0], returnPoints[1], returnPoints[2]):
                return list(reversed(returnPoints))
        return returnPoints
    elif Entity.dxftype in ("SOLID", "3DFACE"):
        Points = []
        for point in list(Entity.points):
            if point == (-0.535, -18.725, 0):
                pass
            point = tuple([round(x, Precision) for x in point])
            if len(point) == 2:
                Points.append(point + (0.0,))
            else:
                Points.append(point)
        returnPoints = list(OrderedDict.fromkeys(Points))
        if CheckDirection == 'Yes':
            if not CheckCrossProduct(returnPoints[0], returnPoints[1], returnPoints[2]):
                return list(reversed(returnPoints))
        return returnPoints
    elif Entity.dxftype in ("POLYLINE",):
        Points = []
        for point in Entity.vertices:
            point = tuple([round(x, Precision) for x in point.location])
            if len(point) == 2:
                Points.append(point + (0.0,))
            else:
                Points.append(point)
        returnPoints = list(OrderedDict.fromkeys(Points))
        if CheckDirection == 'Yes':
            if not CheckCrossProduct(returnPoints[0], returnPoints[1], returnPoints[2]):
                return list(reversed(returnPoints))
        return returnPoints

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
    elif Entity.dxftype in ("SOLID", "3DFACE"):
        Points = []
        for point in list(Entity.points):
            point = tuple([round(x, Precision) for x in point])
            Points.append(point)
        return Points
    elif Entity.dxftype in ("POLYLINE",):
        Points = []
        for point in Entity.vertices:
            point = tuple([round(x, Precision) for x in point.location])
            Points.append(point)
        return Points
    elif Entity.dxftype in ("TEXT",):
        return [Entity.insert]
    else:
        return [(0,0,0)]


def GetEntityData(Entity):
    Data = {}
    if Entity.dxftype in ["LINE", "CIRCLE", "ARC", "LWPOLYLINE", "POLYLINE", "3DFACE"]:
        Data['color'] = Entity.color
        Data['layer'] = Entity.layer
        Data['linetype'] = Entity.linetype
        return Data
    else: return False

def Overkill(Entities, Precision):
    PurgedEntities = dict(enumerate(Entities))
    ReferencePointArray = {}
    for index, Entity in enumerate(Entities) :

        #1. Delete duplicate points in polys
        try: EntityPoints = [tuple(y for y in x) for x in GetRawPoints(Entity, Precision)]
        finally: pass
        if Entity.dxftype in ("LWPOLYLINE", "POLYLINE"):
            NewPoints = []
            for pointindex, EntityPoint in enumerate(EntityPoints):
                if not EntityPoint in NewPoints: NewPoints.append(EntityPoint)
                #else: Entities[index].points = RemovePoint(Entity, pointindex)
            Entities[index].points = tuple(NewPoints)
        
        #2. Delete duplicate objects
        EntityPoints = tuple(sorted((tuple(y for y in x) for x in GetRawPoints(Entity, Precision))))
        if not EntityPoints in ReferencePointArray :
            ReferencePointArray[EntityPoints] = {'layer':Entity.layer}
        elif ReferencePointArray[EntityPoints]['layer'] == Entity.layer:
            del PurgedEntities[index]
    print "Overkilling dataset: {} entities remain after overkill.".format(len(PurgedEntities))
    return PurgedEntities.values()