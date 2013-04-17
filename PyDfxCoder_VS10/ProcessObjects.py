from math import *
import collections
from PyDxfTools import GetPoints
import simplejson as json

PrepDxfObject = collections.namedtuple('PrepDxfObject', ['x', 'y'])
REMapperPointRef = collections.namedtuple('REMapperPointRef', ['FilterName', 'ObjectNumber', 'PointNumber'])

def prep(FilteredEntities, Function, Precision, Parameters):
    Result = []
    for FilteredEntity in FilteredEntities:
        Object = Function(FilteredEntity, Precision, Parameters)
        Result.append(Object)
    return Result

def getFunction(Preprocess, PrepFunctionName):

    def ExtrudeZ(Entity, Precision, ParametersDict):
        Parameters = [float(param) for param in ParametersDict['Parameter']]
        
        Points = GetPoints(Entity, Precision)
        prepObject = {
                      'points' : [],
                      'pointlist' : [],
                      'elements': [],
                      'data': [],
                     }
        for index, Parameter in enumerate(Parameters):
            #prepObject['objects'].append([])
            Data = json.loads(ParametersDict['Data'][index])
            NextLevel = zip([point[0] for point in Points], [point[1] for point in Points], [round(point[2] + Parameter, 6) for point in Points])
            ObjectTuple = ()
            for j, point in enumerate(Points):
                #if prepObject['points'] and prepObject['points'][-1] == point:
                #    print
                prepObject['points'].append(point)
                ObjectTuple = ObjectTuple + tuple([len(prepObject['points']) - 1])
            for j, point in enumerate(NextLevel):
                prepObject['points'].append(point)
                ObjectTuple = ObjectTuple + tuple([len(prepObject['points']) - 1])
            Points = NextLevel
            prepObject['pointlist'].append(ObjectTuple)
            if Data: prepObject['data'].append(Data)
            if len(Points) == 3:
                prepObject['elements'].append('SOLID_6NODES')
            elif len(Points) == 4:
                prepObject['elements'].append('SOLID_8NODES')
        return prepObject

    def Default(Entity, Precision, Parameters):
        Points = GetPoints(Entity, Precision)
        prepObject = {
                      'points' : [],
                      'pointlist' : [],
                      'elements' : [],
                      #'data': [],
                     }
        ObjectTuple = ()
        for point in Points:
            prepObject['points'].append(point)
            ObjectTuple = ObjectTuple + tuple([len(prepObject['points']) - 1])
        #prepObject = [tuple(Points)]
        prepObject['pointlist'].append(ObjectTuple)
        if len(Points) == 2:
            prepObject['elements'].append('LINE_2NODES')
        elif len(Points) == 3:
            prepObject['elements'].append('FACE_3NODES')
        elif len(Points) == 4:
            prepObject['elements'].append('FACE_4NODES')
        return prepObject

    functions = {
        'ExtrudeZ' : ExtrudeZ,
        'Default' : Default,
        }

    if Preprocess == 'Preset':
        return functions[PrepFunctionName]
    else:
        return functions['Default']