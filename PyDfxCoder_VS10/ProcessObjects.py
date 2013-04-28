from math import *
import collections
from PyDxfTools import GetPoints, GetEntityData
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
        EntityModelData = GetEntityData(Entity)
        prepObject = {
                      'points' : [],
                      'pointlist' : [],
                      'elements': [],
                      'entity_model_data': EntityModelData,
                      'extended_model_data': [],
                      'generation_order': [],
                     }
        for index, Parameter in enumerate(Parameters):
            #prepObject['objects'].append([])
            ExtendedModelData = json.loads(ParametersDict['Data'][index])
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

            if ExtendedModelData: prepObject['extended_model_data'].append(ExtendedModelData)
            prepObject['generation_order'].append(index)
            
            if len(Points) == 3:
                prepObject['elements'].append('SOLID_6NODES')
            elif len(Points) == 4:
                prepObject['elements'].append('SOLID_8NODES')
            elif len(Points) == 5:
                prepObject['elements'].append('SOLID_10NODES')
            else:
                prepObject['elements'].append('SOLID_UNKNOWN')
                
        return prepObject

    def Move(Entity, Precision, ParametersDict):
        Points = GetPoints(Entity, Precision)
        EntityModelData = GetEntityData(Entity)
        prepObject = {
                      'points' : [],
                      'pointlist' : [],
                      'elements' : [],
                      'entity_model_data': EntityModelData,
                      'extended_model_data': [],
                     }
        ObjectTuple = ()
        ExtendedModelData = json.loads(ParametersDict['Data']) if 'Data' in ParametersDict and ParametersDict['Data'] else None
        if ExtendedModelData: prepObject['extended_model_data'].append(ExtendedModelData)
        Parameters = json.loads(ParametersDict['Parameter']) if 'Parameter' in ParametersDict and ParametersDict['Data'] else None
        if Parameters['Method'].lower() == "bylayer":
            Layer = Entity.layer
            Vector = Parameters[Layer]
        else:
            Vector = Parameters['Default'] if 'Default' in Parameters else [0, 0, 0]
        for point in Points:
            point = tuple([point[i] + x for i, x in enumerate(Vector)])
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
        elif len(Points) == 5:
            prepObject['elements'].append('PLINE_5NODES')
        elif Entity.dxftype in ['POLYLINE','CIRCLE',]:
            prepObject['elements'].append(Entity.dxftype)
        else:
            prepObject['elements'].append('UNKNOWN')
        return prepObject

    def Default(Entity, Precision, ParametersDict):
        Points = GetPoints(Entity, Precision)
        EntityModelData = GetEntityData(Entity)
        prepObject = {
                      'points' : [],
                      'pointlist' : [],
                      'elements' : [],
                      'entity_model_data': EntityModelData,
                      'extended_model_data': [],
                     }
        ObjectTuple = ()
        ExtendedModelData = json.loads(ParametersDict['Data']) if 'Data' in ParametersDict and ParametersDict['Data'] else None
        if ExtendedModelData: prepObject['extended_model_data'].append(ExtendedModelData)
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
        elif len(Points) == 5:
            prepObject['elements'].append('PLINE_5NODES')
        elif Entity.dxftype in ['POLYLINE','CIRCLE',]:
            prepObject['elements'].append(Entity.dxftype)
        else:
            prepObject['elements'].append('UNKNOWN')
        return prepObject

    functions = {
        'ExtrudeZ' : ExtrudeZ,
        'Move': Move,
        'Default' : Default,
        }

    if Preprocess == 'Preset':
        return functions[PrepFunctionName]
    else:
        return functions['Default']