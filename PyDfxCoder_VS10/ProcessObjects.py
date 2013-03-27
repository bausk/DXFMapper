from math import *
import collections
from PyDxfTools import GetPoints

PrepDxfObject = collections.namedtuple('PrepDxfObject', ['x', 'y'])
REMapperPointRef = collections.namedtuple('REMapperPointRef', ['FilterName', 'ObjectNumber', 'PointNumber'])

def prep(FilteredEntities, Function, Parameters):
    Result = []
    for FilteredEntity in FilteredEntities:
        Object = Function(FilteredEntity, Parameters)
        Result.append(Object)
    return Result

def getFunction(Preprocess, PrepFunctionName):

    def ExtrudeZ(Entity, Parameters):
        Parameters = [float(param) for param in Parameters]
        Points = GetPoints(Entity)
        prepObject = {
                      'points' : [],
                      'nodes' : [],
                      'objects': [],
                     }
        for Parameter in Parameters:
            #prepObject['objects'].append([])
            NextLevel = zip([point[0] for point in Points], [point[1] for point in Points], [round(point[2] + Parameter, 6) for point in Points])
            ObjectTuple = ()
            for j, point in enumerate(Points):
                prepObject['points'].append(point)
                ObjectTuple = ObjectTuple + tuple([len(prepObject['points']) - 1])
            for j, point in enumerate(NextLevel):
                prepObject['points'].append(point)
                ObjectTuple = ObjectTuple + tuple([len(prepObject['points']) - 1])
            Points = NextLevel
            prepObject['nodes'].append(ObjectTuple)

            if len(Points) == 3:
                prepObject['objects'].append('SOLID_6NODES')
            elif len(Points) == 4:
                prepObject['objects'].append('SOLID_8NODES')
        return prepObject

    def Default(Entity, Parameters):
        Points = GetPoints(Entity)
        prepObject = {
                      'points' : [],
                      'nodes' : [],
                      'objects' : [],
                     }
        ObjectTuple = ()
        for point in Points:
            prepObject['points'].append(point)
            ObjectTuple = ObjectTuple + tuple([len(prepObject['points']) - 1])
        #prepObject = [tuple(Points)]
        prepObject['nodes'].append(ObjectTuple)
        if len(Points) == 2:
            prepObject['objects'].append('LINE_2NODES')
        return prepObject

    functions = {
        'ExtrudeZ' : ExtrudeZ,
        'Default' : Default,
        }

    if Preprocess == 'Preset':
        return functions[PrepFunctionName]
    else:
        return functions['Default']