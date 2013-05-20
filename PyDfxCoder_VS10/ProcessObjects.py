from math import *
import collections
from PyDxfTools import GetPoints, GetEntityData
import CoordinateTransform
import simplejson as json
from ShadowbinderDataTools import NearestNeighbor

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
        if (-0.535, -18.725, 0) in Points:
            pass
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
            NextLevel = zip([point[0] for point in Points], [point[1] for point in Points], [round(point[2] + Parameter, Precision) for point in Points])
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
            
            if len(set(Points)) == 3:
                prepObject['elements'].append('SOLID_6NODES')
            elif len(set(Points)) == 4:
                prepObject['elements'].append('SOLID_8NODES')
            elif len(set(Points)) == 5:
                prepObject['elements'].append('SOLID_10NODES')
            else:
                prepObject['elements'].append('SOLID_UNKNOWN')
                
        return prepObject

    def ExtrudeR(Entity, Precision, ParametersDict):
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


        OriginalPoints = GetPoints(Entity, Precision)
        CumulativeParameter = 0
        for index, Parameter in enumerate(Parameters):
            CumulativeParameter += Parameter
            #prepObject['objects'].append([])
            ExtendedModelData = json.loads(ParametersDict['Data'][index])

            #Injecting Spherical formula

            Mapping = {
                       'X': {'Mapping': 'X', 'Origin': 0},
                       'Y': {'Mapping': 'Y', 'Origin': 0},
                       'Z': {'Mapping': 'Z', 'Origin': 0},
                       'D': {'Scale': 1, 'Origin': 0},
                       'G': {'Scale': 1, 'Origin': 0},
                       'R': {'Scale': 1, 'Origin': -CumulativeParameter},
                       }
            FormulaX = CoordinateTransform.GetFormula('Preset', 'Orthospheric', 'X', Parameters = Mapping)
            FormulaY = CoordinateTransform.GetFormula('Preset', 'Orthospheric', 'Y', Parameters = Mapping)
            FormulaZ = CoordinateTransform.GetFormula('Preset', 'Orthospheric', 'Z', Parameters = Mapping)

            NextLevel = [(
                    round(FormulaX( {'X': point[0], 'Y': point[1], 'Z': point[2]}), Precision),
                    round(FormulaY( {'X': point[0], 'Y': point[1], 'Z': point[2]}), Precision),
                    round(FormulaZ( {'X': point[0], 'Y': point[1], 'Z': point[2]}), Precision)
                    ) for point in OriginalPoints]

            #NextLevel = zip([point[0] for point in Points], [point[1] for point in Points], [round(point[2] + Parameter, 6) for point in Points])
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
        elif Entity.dxftype in ['POLYLINE','CIRCLE','LWPOLYLINE']:
            prepObject['elements'].append(Entity.dxftype)
        else:
            prepObject['elements'].append('UNKNOWN')
        return prepObject

    def SphericMove(Entity, Precision, ParametersDict):
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

        Mapping = {
                   'X': {'Mapping': 'X', 'Origin': 0},
                   'Y': {'Mapping': 'Y', 'Origin': 0},
                   'Z': {'Mapping': 'Z', 'Origin': 0},
                   'D': {'Scale': 1, 'Origin': -Vector[0]},
                   'G': {'Scale': 1, 'Origin': -Vector[1]},
                   'R': {'Scale': 1, 'Origin': -Vector[2]},
                   }
        FormulaX = CoordinateTransform.GetFormula('Preset', 'Orthospheric', 'X', Parameters = Mapping)
        FormulaY = CoordinateTransform.GetFormula('Preset', 'Orthospheric', 'Y', Parameters = Mapping)
        FormulaZ = CoordinateTransform.GetFormula('Preset', 'Orthospheric', 'Z', Parameters = Mapping)

        for point in Points:
            #point = tuple([point[i] + x for i, x in enumerate(Vector)])
            Coords = (
                    round(FormulaX( {'X': point[0], 'Y': point[1], 'Z': point[2]}), Precision),
                    round(FormulaY( {'X': point[0], 'Y': point[1], 'Z': point[2]}), Precision),
                    round(FormulaZ( {'X': point[0], 'Y': point[1], 'Z': point[2]}), Precision)
                    )
            
            #prepObject['points'].append(tuple([round(x, Precision) for x in Coords]))
            prepObject['points'].append(Coords)
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
        elif Entity.dxftype in ['POLYLINE','CIRCLE','LWPOLYLINE']:
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
        elif Entity.dxftype in ['POLYLINE','CIRCLE','LWPOLYLINE',]:
            prepObject['elements'].append(Entity.dxftype)
        else:
            prepObject['elements'].append('UNKNOWN')
        return prepObject

    functions = {
        'ExtrudeZ' : ExtrudeZ,
        'Move' : Move,
        'Default' : Default,
        'ExtrudeR' : ExtrudeR,
        'SphericMove' : SphericMove,
        }

    if Preprocess == 'Preset':
        return functions[PrepFunctionName]
    else:
        return functions['Default']