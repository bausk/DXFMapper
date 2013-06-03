from math import *
import collections
import sdxf
import ShadowbinderDataTools
from ShadowbinderDataTools import NeighborhoodRaw
from ShadowbinderFormats import *
from meshpy.tet import MeshInfo, build, Options
import simplejson as json
#import numpy as np
#import scipy.spatial
from Settings import UpdateDict
import csv



#from PyDxfTools import GetPoints

#PrepDxfObject = collections.namedtuple('PrepDxfObject', ['x', 'y'])
#REMapperPointRef = collections.namedtuple('REMapperPointRef', ['FilterName', 'ObjectNumber', 'PointNumber'])

#def postp(Points, Settings):
#    Result = []
#    for FilteredEntity in FilteredEntities:
#        Object = Function(FilteredEntity, Parameters)
#        Result.append(Object)
#    return Result




def getPointActionFunction(PointAction):

    def CompatibleNodes(Parameters, Point, PointTuple, NumberedPoints, Elements):
        #if PointTuple == (-19.4,-4.85,58.3):
        #    pass
        Output = []
        if 'CutoffZ' in Parameters:
            Position = PointTuple[2]
            if Position < float(Parameters['CutoffZ'][0]) or Position > float(Parameters['CutoffZ'][1]): return False, []
        NewPointIndex = NumberedPoints['maximumNode']
        NewNumberedPoints = {}
        FirstFilter = Parameters['Filters'][0] #First filter: its elements will stay with the Point
        FiltersInParameters = Parameters['Filters'][1:] #All except the first: these ones are given new Points with same coords
        point_number = Point['number']
        ElementsInPoint = NumberedPoints['points'][point_number]['elementnumbers']
        #FiltersInPoint = [x.FilterName for x in Point['pointObjectReferences']]
        FiltersInPoint = [Elements[x]['filter'] for x in ElementsInPoint]
        if not FirstFilter in FiltersInPoint: return  False, [] #No elements from first filter? Not our client
        OldPointIndex = Point['number']
        Output.append(OldPointIndex)
        for ParameterFilter in FiltersInParameters: #ParameterFilter will correspond to a New Point if we find any matches
            #If elements in this point have a filter equal to ParameterFilter, then we create a new point
            ElementIndices = [i for i, x in enumerate(FiltersInPoint) if x == ParameterFilter] #Which elements referenced by Point in Point['elementnumbers'] contain this Filter?
            #if not, then no elements are repatched and no new points are created.
            if ElementIndices: #This ParameterFilter exists in FiltersInPoint for elements referenced by ElementIndices
                #if PointTuple == (-19.4, -4.85, 58.3):
                #    pass
                #ElementIndices contains elements that are referenced in Point
                #Now we: 
                #  create new numbered point (aka node),
                NewPointIndex += 1
                NewNumberedPoints[NewPointIndex] = {u'point': PointTuple, u'elementnumbers': []}
                Point['additionalPoints'].append(NewPointIndex)
                #  continue the record for output
                Output.append(NewPointIndex)
                #  and write every filtered element from this Point to new Point
                for index in ElementIndices:
                    ElementNumber, ElementPointIndex = ShadowbinderDataTools.getElementFromPoint(Point, index)
                    #Now we can add reference to element and remove it from old NumberedPoint
                    NewNumberedPoints[NewPointIndex][u'elementnumbers'].append(ElementNumber)
                    NumberedPoints['points'][OldPointIndex][u'elementnumbers'].remove(ElementNumber)
                    Element = Elements[ElementNumber]
                    Element['points'][ElementPointIndex] = NewPointIndex

        if not NewNumberedPoints: return False, [] #Not a single filter matches
        NumberedPoints['maximumNode'] = NewPointIndex
        NumberedPoints['points'].update(NewNumberedPoints)
        return NewNumberedPoints, Output

    def RotateNodes(Parameters, Point, PointTuple, NumberedPoints, Elements):
        Output = {}
        if 'Action' in Parameters:
            Rule = Parameters['Action'] #Only VectorSum is implemented
        else: Rule = 'VectorSum'
        if 'Direction' in Parameters:
            Direction = Parameters['Direction']
            if Direction[1] == '-': DirectionPositive = False
            else: DirectionPositive = True
            if Direction[0] == 'X': DirectionIndex = 0
            elif Direction[0] == 'Y': DirectionIndex = 1
            else: DirectionIndex = 2

        else: Direction = 'Z+'
        if 'Filters' in Parameters:
            FiltersInParameters = Parameters['Filters']
        PointNumbers = [Point['number']] + [x for x in Point['additionalPoints']] #Point number plus whatever additional points there are, if any
        ResultingVector = [0, 0, 0]
        for pointNumber in PointNumbers:
            ElementList = NumberedPoints['points'][pointNumber]['elementnumbers']
            SelectedElements = [Elements[x] for x in ElementList if Elements[x]['filter'] in FiltersInParameters]
            if not SelectedElements: continue
            for SelectedElement in SelectedElements:
                if PointTuple == (6.95,-0.53,64.2):
                    pass
                Point1index = SelectedElement['points'][0]
                Point2index = SelectedElement['points'][1]
                Coords1 = NumberedPoints['points'][Point1index]['point']
                Coords2 = NumberedPoints['points'][Point2index]['point']
                ElementVector = [(item2 - item1) for item1, item2 in zip(Coords1, Coords2)]
                if (ElementVector[DirectionIndex] >= 0) != DirectionPositive:
                    ElementVector = [-item for item in ElementVector]
                ResultingVector = [(item1 + item2) for item1, item2 in zip(ResultingVector, ElementVector)]
            Output[pointNumber] = [round(x + y, 4) for x,y in zip(ResultingVector, PointTuple)]
            Output[Point['number']] = [round(x + y, 4) for x,y in zip(ResultingVector, PointTuple)]
        #For any given point Point, including its ['additionalPoints'], if any
        #1. Find all elements that connect to Point and whose filters are in Parameters['Filters']
        #2. Find all elements that are LINE_2NODE
        #3. Parameters['Direction'] gives the rule to identify fisrt and last vector points from LINE_2NODE
        #4. Compute vector sum of the obtained vectors.
        #5. Write node number and vector sum into Output
        if not Output: return False, False
        return False, Output

    def Supports(Parameters, Point, PointTuple, NumberedPoints, Elements):
        Output = {}
        if 'CutoffZ' in Parameters:
            Position = PointTuple[2]
            if Position < float(Parameters['CutoffZ'][0]) or Position > float(Parameters['CutoffZ'][1]): return False, []
        if 'Value' in Parameters:
            SupportDirections = Parameters['Value']
        else: SupportDirections = ['UX', 'UY', 'UZ', 'RX', 'RY', 'RZ']
        pointNumber = Point['number']

        Output[pointNumber] = SupportDirections

        #PointNumbers = [Point['number']] + [x for x in Point['additionalPoints']] #Point number plus whatever additional points there are, if any
        #ResultingVector = [0, 0, 0]
        #for pointNumber in PointNumbers:
        #    ElementList = NumberedPoints['points'][pointNumber]['elementnumbers']
        #    SelectedElements = [Elements[x] for x in ElementList if Elements[x]['filter'] in FiltersInParameters]
        #    if not SelectedElements: 

        #    for SelectedElement in SelectedElements:
        #        Point1index = SelectedElement['points'][0]
        #        Point2index = SelectedElement['points'][1]
        #        Coords1 = NumberedPoints['points'][Point1index]['point']
        #        Coords2 = NumberedPoints['points'][Point2index]['point']
        #        ElementVector = [(item2 - item1) for item1, item2 in zip(Coords1, Coords2)]
        #        if (ElementVector[DirectionIndex] >= 0) != DirectionPositive:
        #            ElementVector = [-item for item in ElementVector]
        #        ResultingVector = [(item1 + item2) for item1, item2 in zip(ResultingVector, ElementVector)]
        #    Output[pointNumber] = [round(x + y, 4) for x,y in zip(ResultingVector, PointTuple)]


        if not Output: return False, False
        return False, Output


    def Default():
        return False, False

    functions = {
        'Compatibility' : CompatibleNodes,
        'NodalAxisRotation' : RotateNodes,
        'Supports' : Supports,
        'Default' : Default,
        }

    if PointAction in functions:
        return functions[PointAction]
    else:
        return functions['Default']


def getElementActionFunction(ElementAction):

    def ElementForce(Parameters, Element, NumberedPoints, Elements, ExtendedData):
        #Okay
        Output = {}

        if not Element: return False, False
        #if (-10.64, 20.53, 57.86) in [NumberedPoints['points'][pointindex]['point'] for pointindex in Element['points']]:
        #    if Element['elementclass'] == "LINE_2NODES" and Parameters['Filters'] == "TendonsCyl":
        #        pass
        #if Element['elementclass'] == "FACE_3NODES":
        #    pass
        #First, define if element needs the ElementAction
        if 'Filters' in Parameters:
            FiltersInParameters = Parameters['Filters']
            ElementFilter = Element['filter']
            if not ElementFilter in FiltersInParameters: return False, False
        if 'Markers' in Parameters:
            #MarkerData = json.loads(Parameters['Markers'])
            if not isinstance(Parameters['Markers'], list): Parameters['Markers'] = [Parameters['Markers']]
            Markers = dict(Marker.split(':') for Marker in Parameters['Markers'])
            #Markers are checked against Element's entity_model_data
            #Element should satisfy all markers
            for marker, value in Markers.iteritems():
                ElementValue = str(Element['entity_model_data'][marker]) if Element['entity_model_data'] and (marker in Element['entity_model_data']) else None
                if marker == "generation_order":
                    ElementValue = Element['generation_order']

                if str(value) != str(ElementValue) : return False, False
        try:
            Value = json.loads(Parameters['Value'])
            ForceValue = Value['value'] if type(Value) is dict else Value
        except:
            ForceValue = Parameters['Value']
        
        if type(Value) is dict and 'source' in Value:
            #if (-14.96, -19.46, 54.93) in [NumberedPoints['points'][pointindex]['point'] for pointindex in Element['points']]:
            #    pass
            ValueIndex = None
            MappingFilter = Value['map']
            for MappingCandidate in ExtendedData['SpecialEntities']:
                if MappingFilter == MappingCandidate['filter'] and (not ('color' in Value) or Value['color'] == MappingCandidate['entity_model_data']['color']):
                    MappingElement = MappingCandidate
                    break
            ElementPointTuples = [NumberedPoints['points'][point]['point'] for point in Element['points']]
            for i, point in enumerate(MappingElement['points']):
                pointTuple = NumberedPoints['points'][point]['point']
                if pointTuple in ElementPointTuples:
                    ValueIndex = i
            if ValueIndex != None:

                SourceFile = Value['source']
                counter = 0
                with open(SourceFile, 'rb') as f:
                    try:
                        reader = csv.reader(f)
                    except:
                        reader = csv.reader(f, delimiter=';')
                    for row in reader:
                        if counter == ValueIndex:
                            ForceValue = float(row[0])
                            break
                        else:
                            counter += 1
            else:
                return False, False

        if Parameters['Type'] == "Dilatation":
            
            LoadID = 8
            ElementNumber = Element['elementnum']
            Output['load_id'] = LoadID
            Output['direction'] = 1
            Output['element'] = ElementNumber
            Output['loadcase'] = 2
            Output['value'] = ForceValue
            Output['string'] = "{} 0.000012 0 0".format(Output['value'])
        elif Parameters['Type'] == "VolumePressure":
            #if Element['elementclass'] == "FACE_3NODES":
            #    pass
            LoadID = Value['loadtype']
            ElementNumber = Element['elementnum']
            Output['load_id'] = LoadID
            Output['direction'] = Value['axis']
            Output['element'] = ElementNumber
            Output['loadcase'] = 1
            Output['value'] = ForceValue
            Output['string'] = "{} {} 0 0".format(Output['value'], Value['face'])
        elif Parameters['Type'] == "PlatePressure":
            #if Element['elementclass'] == "FACE_3NODES":
            #    pass
            LoadID = Value['loadtype']
            ElementNumber = Element['elementnum']
            Output['load_id'] = LoadID
            Output['direction'] = Value['axis']
            Output['element'] = ElementNumber
            Output['loadcase'] = 1
            Output['value'] = ForceValue
            Output['string'] = "{}".format(Output['value'])
        return False, Output

    def AssignLayer(Parameters, Element, NumberedPoints, Elements, ExtendedData):
        ElementFilter = Element['filter']
        AssignedLayers = json.loads(Parameters['Layers'])
        if ElementFilter in AssignedLayers:
            AssignedLayer = AssignedLayers[ElementFilter]
            Element['entity_model_data']['layer'] = AssignedLayer
        return False, False

    def ElementProperty(Parameters, Element, NumberedPoints, Elements, ExtendedData):
        Output = {}
        return False, Output

    functions = {
        'ElementForce' : ElementForce,
        'ElementProperty' : ElementProperty,
        'AssignLayer' : AssignLayer,
        }

    if ElementAction in functions:
        return functions[ElementAction]
    else:
        return functions['Default']


def ProcessGlobalAction(ActionType, GlobalAction, NumberedPoints, Elements, Points):
    ExtendedData = {'ElementPropertyIndex' : {}}
    if ActionType == 'SpecialEntities':
        Filters = json.loads(GlobalAction['Filters'])
        if not 'SpecialEntities' in ExtendedData:
            ExtendedData['SpecialEntities'] = []
        for Element in Elements:
            if Element and Element['filter'] in Filters:
                ExtendedData['SpecialEntities'].append(Element)
        return ExtendedData, False

    if ActionType == 'Nonlinear':
        Output = {}
        #for key in GlobalAction:
        #    if 'ElementPropertyMaxIndex' in ExtendedData:
        #        ExtendedData['ElementPropertyMaxIndex'] += 1
        #    else:
        #         ExtendedData['ElementPropertyMaxIndex'] = 1
        #    propertyindex = ExtendedData['ElementPropertyMaxIndex']
        #    ExtendedData['ElementPropertyIndex'][key] = propertyindex
        #    ExtendedData['NonlinearPropertyIndex'][key] = nonlinearindex
        #
        #
        #    ExtendedData['ElementPropertyIndex'][key] = workingindex #In this same notation we can get the index when writing elements
        #    Output[index] = ""
        return ExtendedData, Output #Here we have Output ready to be printed and ExtendedData, a mapper to Output
    if ActionType == 'ElementProperties':
        Output = {}
        for key in GlobalAction:
            if 'ElementPropertyMaxIndex' in ExtendedData:
                ExtendedData['ElementPropertyMaxIndex'] += 1
            else:
                ExtendedData['ElementPropertyMaxIndex'] = 1
            workingindex = ExtendedData['ElementPropertyMaxIndex']
            ExtendedData['ElementPropertyIndex'][key] = workingindex #In this same notation we can get the index when writing elements
            
            Output[workingindex] = GlobalAction[key]
        return ExtendedData, Output #Here we have Output ready to be printed and ExtendedData, a mapper to Output
    if ActionType == 'Orphans':
        Output = []
        for Number, Point in NumberedPoints['points'].iteritems():
            ElementAmount = len(Point['elementnumbers'])
            if ElementAmount < 2:
                print "Orphan node {}!".format(Number)
                Output.append({'element_type': 'POINT', 'position': Point['point'], 'layer': 'Errors', 'nodenumber': Number})
        return {'information':'addObjects'}, Output#Here we have Output ready to be printed and ExtendedData, a mapper to Output
    if ActionType == 'Meshing':

        EntityModelData = json.loads(GlobalAction['EntityModelData']) if 'EntityModelData' in GlobalAction else {}
        ExtendedModelData = json.loads(GlobalAction['ExtendedModelData']) if 'ExtendedModelData' in GlobalAction else {}
        Semantic = json.loads(GlobalAction['Semantic']) if 'Semantic' in GlobalAction else {}
        if 'exclude filters' in Semantic:
            if not 'ExcludeFilters' in ExtendedData: ExtendedData['ExcludeFilters'] = []
            ExtendedData['ExcludeFilters'] = ExtendedData['ExcludeFilters'] + Semantic['exclude filters']
        Boundaries = []
        Output = []
        Geometry = json.loads(GlobalAction['Geometry']) if 'Geometry' in GlobalAction else {}
        Parameters = json.loads(GlobalAction['Parameters']) if 'Parameters' in GlobalAction else {}
        AdditionalPointsFilters = Geometry['points'] if 'points' in Geometry else []
        for Filter in Geometry['boundaries']:
            print "Using filter {} as finite element domain boundary.".format(Filter)
            for Element in Elements:
                if Element and Element['filter'] == Filter and Element['elementclass'] in ['FACE_3NODES', 'FACE_4NODES', 'POLYLINE']:
                    Boundaries.append(Element)

        AdditionalPoints = []
        for Filter in AdditionalPointsFilters:
            print "Using filter {} as additional points container.".format(Filter)
            for Element in Elements:
                if Element and Element['filter'] == Filter and Element['elementclass'] in ['FACE_3NODES', 'FACE_4NODES', 'POLYLINE', 'LINE_2NODES']:
                    AdditionalPoints.extend(
                                            Element['points']
                                            )

        print "Assembling FE domain"

        mesh_info = MeshInfo()
        #additional_points = MeshInfo()
        #additional_points.set_points(list(set(AdditionalPoints)))
        MeshPoints = []
        MeshFacets = []
        MeshPointsIndex = {}
        PointIndex = 0

        for BoundaryElement in Boundaries:
            
            ElementPoints = BoundaryElement['points']

            MeshFacet = []
            if Parameters['type'] == 'divide_4p_faces':
                for point in [ElementPoints[0],ElementPoints[1],ElementPoints[2]]:
                    if not point in MeshPointsIndex:
                        MeshPointsIndex[point] = PointIndex
                        MeshPoints.append(False)
                        MeshPoints[PointIndex] = NumberedPoints['points'][point]['point']
                        PointIndex += 1
                    MeshFacet.append(MeshPointsIndex[point])
                MeshFacets.append(MeshFacet)
                MeshFacet = []
                if ElementPoints[2] != ElementPoints[3]:
                    for point in [ElementPoints[0],ElementPoints[2],ElementPoints[3]]:
                        if not point in MeshPointsIndex:
                            MeshPointsIndex[point] = PointIndex
                            MeshPoints.append(False)
                            MeshPoints[PointIndex] = NumberedPoints['points'][point]['point']
                            PointIndex += 1
                        MeshFacet.append(MeshPointsIndex[point])
                    MeshFacets.append(MeshFacet)
            else:
                for point in ElementPoints:
                    if not point in MeshPointsIndex:
                        MeshPointsIndex[point] = PointIndex
                        MeshPoints.append(False)
                        MeshPoints[PointIndex] = NumberedPoints['points'][point]['point']
                        PointIndex += 1
                    if not MeshPointsIndex[point] in MeshFacet:
                        MeshFacet.append(MeshPointsIndex[point])
                    else:
                        print "Mesh error or 3-point 3DFACE."
                MeshFacets.append(MeshFacet)
                MeshFacet = []

        for point in list(set(AdditionalPoints)):
            if not point in MeshPointsIndex: #See whether the point is already indexed by its native number
                MeshPointsIndex[point] = PointIndex
                MeshPoints.append(False)
                MeshPoints[PointIndex] = NumberedPoints['points'][point]['point']
                PointIndex += 1

            
        mesh_info.set_facets(MeshFacets)
        mesh_info.set_points(MeshPoints)
        #insertaddpoints
        
        #points = np.array([list(x) for x in MeshPoints])
        #qhull = scipy.spatial.Delaunay(points)
        #mesh_info.Options(switches='pq')
        #mesh_info.set_points([
        #    (0,0,0), (12,0,0), (12,12,0), (0,12,0),
        #    (0,0,12), (12,0,12), (12,12,12), (0,12,12),
        #    ])
        #mesh_info.set_facets([
        #    [0,1,2,3],
        #    [4,5,6,7],
        #    [0,4,5,1],
        #    [1,5,6,2],
        #    [2,6,7,3],
        #    [3,7,4,0],
        #    ])
        
        #opts = Options(switches='pq')
        #opts.maxvolume = 0.0001
        #opts.parse_switches()

        mesh_info.regions.resize(1)
        mesh_info.regions[0] = [
                                MeshPoints[0][0], MeshPoints[0][1], MeshPoints[0][2], # point in volume -> first box
                                0, # region tag (user-defined number)
                                Parameters['maxvolume'], # max tet volume in region
                                ]
        mesh = build(mesh_info, options=Options(switches="pqT", epsilon=Parameters['tolerance']), volume_constraints=True)
        print "Created mesh with {} points, {} faces and {} elements.".format(len(mesh.points), len(mesh.faces), len(mesh.elements))
        #mesh = build(mesh_info, options=Options(switches="pTi", epsilon=Parameters['tolerance'], insertaddpoints=True), volume_constraints=True, insert_points=additional_points)
        #mesh.write_vtk("test.vtk")
        #mesh.points
        #mesh.elements
        #mesh.faces
        filename = "test"
        #mesh.save_elements(filename)
        #mesh.save_nodes(filename)
        #mesh.save_elements(filename)
        #mesh.save_faces(filename)
        #mesh.save_edges(filename)
        #mesh.save_neighbors(filename)
        #mesh.save_poly(filename)
        #for element in qhull.simplices:
        #    Position = [list(qhull.points[x]) for x in element]
        #    Output.append({'element_type': '3DFACE', 'position': Position, 'layer': 'Elements'})
        #NumberedPoints['points'][compoundObject['points'][0]]['point']
        if not Boundaries: return False, False
        Precision = int(GlobalAction['Precision']) if 'Precision' in GlobalAction else 4

        if Semantic['output'].lower() == 'graphics':
            for face in mesh.faces:
                Position = [mesh.points[x] for x in face]
                Output.append({'element_type': '3DFACE', 'position': Position, 'layer': 'Faces'})
            for element in mesh.elements:
                Position = [mesh.points[x] for x in element]
                Output.append({'element_type': '3DFACE', 'position': Position, 'layer': 'Elements'})
            return {'information':'addObjects'}, Output
        elif Semantic['output'].lower() == 'fea':
            Points = {}
            for NumberedPoint in NumberedPoints['points']:
                Points[NumberedPoints['points'][NumberedPoint]['point']] = NumberedPoint
            NodeNumber = NumberedPoints['maximumNode']
            for element in mesh.elements:
                Position = [mesh.points[x] for x in element]
                for i, point in enumerate(Position):
                    Position[i] = [round(x, Precision) for x in point]

                #else:
                #    if tuple([round(x, PrepPrecision) for x in Coords]) in [(4.95,-17.69,58.9), (4.96,-17.69,58.9)]:
                #        pass                    
                #    object['points'][i] = tuple([round(x, PrepPrecision) for x in Coords])
                #    if not object['points'][i] in GlobalPointIndex:
                #        GlobalPointIndex.append(object['points'][i])



                ElementPoints = []
                ElementNumber = len(Elements)
                for point in Position:

                    #Update NumberedPoints and construct all necessary data for Elements
                    point = NeighborhoodRaw(tuple(point), Precision, Points)
                    if not tuple(point) in Points:
                        NodeNumber += 1
                        Points[tuple(point)] = NodeNumber
                        #PointsNumbered.append(None)
                        NumberedPoints['points'][NodeNumber] = {'point': tuple(point), 'elementnumbers': []}
                        NumberedPoints['maximumNode'] = NodeNumber
                    CurrentPointNumber = Points[tuple(point)]
                    ElementPoints.append(CurrentPointNumber)
                    NumberedPoints['points'][CurrentPointNumber]['elementnumbers'].append(ElementNumber)

                    #Update Points if possible


                #Update Elements
                Element = { 'points' : ElementPoints,
                'elementclass' : 'SOLID_4NODES',
                'elementnum': ElementNumber, #???
                'filter': Semantic['filter'],
                'entity_model_data': EntityModelData,
                'extended_model_data': ExtendedModelData,
                'generation_order': None,
                }
                Elements.append(None)
                Elements[ElementNumber] = Element
            return ExtendedData, False

    if ActionType == 'AddShells':
        ExtendedData = {}
        EntityModelData = json.loads(GlobalAction['EntityModelData']) if 'EntityModelData' in GlobalAction else {}
        ExtendedModelData = json.loads(GlobalAction['ExtendedModelData']) if 'ExtendedModelData' in GlobalAction else {}
        Filters = json.loads(GlobalAction['Filters']) if 'Filters' in GlobalAction else {}
        for Element in Elements:
            if not Element or not Element['filter'] in Filters: continue
            if Element['generation_order'] == 0 and Element['entity_model_data']['layer'] != "Concrete bases crown":
                ElementPoints = [Element['points'][0], Element['points'][1], Element['points'][2]]
                ElementNumber = len(Elements)
                NewElement = { 'points' : ElementPoints,
                'elementclass' : 'FACE_3NODES',
                'elementnum': ElementNumber, #???
                'filter': GlobalAction['AssignedFilter'],
                'entity_model_data': EntityModelData,
                'extended_model_data': ExtendedModelData,
                'generation_order': None,
                }
                Elements.append(None)
                Elements[ElementNumber] = NewElement

                if Element['elementclass'] == 'SOLID_8NODES':
                    ElementPoints = [Element['points'][0], Element['points'][2], Element['points'][3]]
                    ElementNumber = len(Elements)
                    NewElement = { 'points' : ElementPoints,
                    'elementclass' : 'FACE_3NODES',
                    'elementnum': ElementNumber, #???
                    'filter': GlobalAction['AssignedFilter'],
                    'entity_model_data': EntityModelData,
                    'extended_model_data': ExtendedModelData,
                    'generation_order': None,
                    }
                    Elements.append(None)
                    Elements[ElementNumber] = NewElement

                if Element['elementclass'] == 'SOLID_10NODES':
                    pass

                pass
                
        return {}, {}
    return False


def getFormatWriter(SettingsDict):

    def Dxf(Objects, Filters, Points, NumberedPoints, Elements):
        OutputFile = sdxf.Drawing()
        #ExtendedData = {}
        GlobalActions = SettingsDict['Actions'].copy() if 'Actions' in SettingsDict else {}
        GlobalActionOrder = SettingsDict['ActionOrder'] if 'ActionOrder' in SettingsDict else False
        for GlobalAction in GlobalActions:
            ActionType = GlobalActions[GlobalAction].pop('Type')
            ExtendedData, Output = ProcessGlobalAction(ActionType, GlobalActions[GlobalAction], NumberedPoints, Elements, Points)
            if ExtendedData['information'] == 'addObjects':
                for Item in Output:
                    if Item['element_type'] == 'POINT':
                        OutputFile.append(sdxf.Text(text=Item['nodenumber'], point=Item['position'], layer=Item['layer']))
                    if Item['element_type'] == '3DFACE':
                        if len(Item['position'])<4:
                            Item['position'].append(Item['position'][-1])
                        OutputFile.append(sdxf.Face(points=Item['position'], layer=Item['layer']))


        ElementActions = SettingsDict['Element Actions'].copy() if 'Element Actions' in SettingsDict else [] #Copying because we will be pop()ping already processed Actions
        ElementActionOrder = SettingsDict['ElementActionOrder'] if 'ElementActionOrder' in SettingsDict else []
        ActionName = None
        if not isinstance(ElementActionOrder, list):
            ElementActionOrder = [ElementActionOrder]

        for compoundObject in Elements:
            if not compoundObject: continue


            for i, ListElement in enumerate(ElementActionOrder):
                ActionName = ListElement
                ElementAction = ElementActions.pop(ActionName)
                ActionType = ElementAction['Action']
                ElementActionFunction = getElementActionFunction(ActionType)
                NewElements, Output = ElementActionFunction(ElementAction, Element, NumberedPoints, Elements, ExtendedData)
                #2013-04-20 Working here. ERRONEOUS CODE!
                if Output: Format(FormatDict, ActionType, Output, ExtendedData)

            for ElementAction in ElementActions:
                ActionType = ElementActions[ElementAction]['Action']
                ElementActionFunction = getElementActionFunction(ActionType)
                NewElements, Output = ElementActionFunction(ElementActions[ElementAction], compoundObject, NumberedPoints, Elements)
                #Points[Point], NumberedPoints and Elements get updated

            objectType = compoundObject['elementclass']
            objectLayer = compoundObject['entity_model_data']['layer'] if 'entity_model_data' in compoundObject and compoundObject['entity_model_data'] else objectType
            if objectType == 'LINE_2NODES':
                Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                OutputFile.append(sdxf.Line(points=[Point1, Point2], layer=objectLayer))
            if objectType == 'SOLID_8NODES':
                for x in [    [[0,1,2,3], "bottom"],
                              [[4,5,6,7], "top"],
                              [[0,1,5,4], "side1"],
                              [[1,2,6,5], "side2"],
                              [[2,3,7,6], "side3"],
                              [[3,0,4,7], "side4"]
                              ]:
                    FaceVertices = [NumberedPoints['points'][compoundObject['points'][index]]['point'] for index in x[0]]
                    OutputFile.append(sdxf.Face(points=FaceVertices, layer=objectLayer + " " + x[1]))

                #Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                #Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                #Point3 = NumberedPoints['points'][compoundObject['points'][2]]['point']
                #Point4 = NumberedPoints['points'][compoundObject['points'][3]]['point']
                #OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer=objectLayer))
                #Point1 = NumberedPoints['points'][compoundObject['points'][4]]['point']
                #Point2 = NumberedPoints['points'][compoundObject['points'][5]]['point']
                #Point3 = NumberedPoints['points'][compoundObject['points'][6]]['point']
                #Point4 = NumberedPoints['points'][compoundObject['points'][7]]['point']
                #OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer=objectLayer))
                #Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                #Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                #Point3 = NumberedPoints['points'][compoundObject['points'][4]]['point']
                #Point4 = NumberedPoints['points'][compoundObject['points'][5]]['point']
                #OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer=objectLayer))

            if objectType == 'SOLID_10NODES':
                Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][2]]['point']
                Point4 = NumberedPoints['points'][compoundObject['points'][3]]['point']
                #Point1 = compoundObject['points'][compoundObject['pointlist'][objectNum][0]]
                #Point2 = compoundObject['points'][compoundObject['pointlist'][objectNum][1]]
                #Point3 = compoundObject['points'][compoundObject['pointlist'][objectNum][2]]
                #Point4 = compoundObject['points'][compoundObject['pointlist'][objectNum][3]]
                OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer=objectLayer))
                #Point1 = compoundObject['points'][compoundObject['pointlist'][objectNum][5]]
                #Point2 = compoundObject['points'][compoundObject['pointlist'][objectNum][6]]
                #Point3 = compoundObject['points'][compoundObject['pointlist'][objectNum][7]]
                #Point4 = compoundObject['points'][compoundObject['pointlist'][objectNum][8]]
                #OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer="Faces"))
            if objectType == 'SOLID_6NODES':
                Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][2]]['point']
                OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point3], layer=objectLayer))
                Point1 = NumberedPoints['points'][compoundObject['points'][3]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][4]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][5]]['point']
                OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point3], layer=objectLayer))
            if objectType == 'FACE_3NODES':
                #Point1 = tuple(list(compoundObject['points'][compoundObject['pointlist'][objectNum][0]])[0:2])
                #Point2 = tuple(list(compoundObject['points'][compoundObject['pointlist'][objectNum][1]])[0:2])
                #Point3 = tuple(list(compoundObject['points'][compoundObject['pointlist'][objectNum][2]])[0:2])
                Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][2]]['point']
                #OutputFile.append(sdxf.LwPolyLine(points=[Point1, Point2, Point3], flag=1, layer="Polylines"))
                OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point3], layer=objectLayer))
            if objectType == 'FACE_4NODES':
                Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][2]]['point']
                Point4 = NumberedPoints['points'][compoundObject['points'][3]]['point']
                #OutputFile.append(sdxf.LwPolyLine(points=[Point1, Point2, Point3, Point4], flag=1, layer=objectLayer))
                OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer=objectLayer))
            if objectType == 'PLINE_5NODES':
                Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][2]]['point']
                Point4 = NumberedPoints['points'][compoundObject['points'][3]]['point']
                #OutputFile.append(sdxf.LwPolyLine(points=[Point1, Point2, Point3, Point4], flag=1, layer="Polylines"))
                OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer=objectLayer))
            if objectType in ['POLYLINE', 'LWPOLYLINE']:
                PointRefs = compoundObject['points']
                PointList = [NumberedPoints['points'][x]['point'] for x in PointRefs]
                OutputFile.append(sdxf.PolyLine(points=PointList, layer=objectLayer))
        OutputFile.saveas(SettingsDict['OutputFile'])
        return True

    def LiraCustom(Objects, Filters, Points, NumberedPoints, Elements):
        #Objects is formed in prep Functions, which is the ABSOLUTELY WRONG WAY TO DO THINGS
        #Objects[str(filter)]['points'][A] = tuple(3), links to Points
        #Objects[str(filter)]['pointlist'][tuple(2..8)] = links to A^
        #Objects[str(filter)]['nodelist'][tuple(2..8)] = links to A^
        #Objects[str(filter)]['elements'] = "LINE_2NODES" etc. Shares index with 'nodes'
        #Elements[ElementNumber]['points']        = ((Point), ...)
        #                     ['elementclass']  = ElementClass
        #                     ['elementnum']    = ElementNumber
        #Points[(Point)]['number']                = PointNumber
        #               ['elements']              = (ElementNumber, ...)
        #               ['pointObjectReferences'] = ((FilterName, ObjectNumber, PointNumber), ...)
        #PointsNumbered[PointNumber]['point']   = pointTuple
        #Okay let's go.

        Format = getFormat(SettingsDict['Format'])
        FormatDictInitializer = initFormat(SettingsDict['Format'], __name__)
        OutputSemantic = SettingsDict['Semantic'] if 'Semantic' in SettingsDict else False
        FormatDict = {}
        FormatDict = FormatDictInitializer(OutputSemantic)
        ExtendedData = {'ExcludeFilters':[],}

        #First: routine to check global actions
        GlobalActions = SettingsDict['Actions'].copy() if 'Actions' in SettingsDict else {}
        GlobalActionOrder = SettingsDict['ActionOrder'] if 'ActionOrder' in SettingsDict else False
        if not type(GlobalActionOrder) is list: GlobalActionOrder = [GlobalActionOrder]
        for GlobalAction in GlobalActionOrder:
            ActionType = GlobalActions[GlobalAction].pop('Type')
            if ActionType == "Nonlinear":
                pass
            NewExtendedData, Output = ProcessGlobalAction(ActionType, GlobalActions[GlobalAction], NumberedPoints, Elements, Points)
            ExtendedData = UpdateDict(ExtendedData, NewExtendedData)
            if Output: Format(FormatDict, ActionType, Output, ExtendedData)

        for Point in Points:
            #Check if there are points with filters belonging to actions
            #
            PointActions = SettingsDict['Point Actions'].copy() if 'Point Actions' in SettingsDict else [] #Copying because we will be pop()ping already processed Actions
            PointActionOrder = SettingsDict['PointActionOrder'] if 'PointActionOrder' in SettingsDict else []
            ActionName = None
            #aaa = dict((ActionName, PointActions[ActionName]) for ActionIndex, ActionName in enumerate(PointActionOrder))
            #bbb = {}
            #for ccc in aaa:
            #    print
            #The first loop goes through ordered Point Actions, the 
            if not isinstance(PointActionOrder, list):
                PointActionOrder = [PointActionOrder]
            for i, ListElement in enumerate(PointActionOrder):
                ActionName = PointActionOrder[i]
                PointAction = PointActions.pop(ActionName)
                ActionType = PointAction['Type']
                PointActionFunction = getPointActionFunction(ActionType)
                NewPoints, Output = PointActionFunction(PointAction, Points[Point], Point, NumberedPoints, Elements)
                if Output: Format(FormatDict, ActionType, Output, ExtendedData)

            for PointAction in PointActions:
                ActionType = PointActions[PointAction]['Type']
                PointActionFunction = getPointActionFunction(ActionType)
                NewPoints, Output = PointActionFunction(PointActions[PointAction], Points[Point], Point, NumberedPoints, Elements)
                #Points[Point], NumberedPoints and Elements get updated
                if Output: Format(FormatDict, ActionType, Output, ExtendedData)
                #if NewPoints: NumberedPoints.update(NewPoints) #Already done in PointActionFunction

        #Build element index
        ElementNumber = 1
        ExtendedData['elementcounter'] = {}
        for Element in Elements:
            if Element and (not Element['filter'] in ExtendedData['ExcludeFilters']) and (Element['elementclass'] in ["LINE_2NODES", "SOLID_8NODES", "SOLID_4NODES", "SOLID_6NODES", "SOLID_10NODES", "FACE_3NODES", "FACE_4NODES"]):
                ExtendedData['elementcounter'][Element['elementnum']] = ElementNumber
                ElementNumber +=1

        for Element in Elements:
            if Element and Element['filter'] == "LowerTendonsSph" and Element['entity_model_data']['color'] == 1:
                pass
            ElementActions = SettingsDict['Element Actions'].copy() if 'Element Actions' in SettingsDict else [] #Copying because we will be pop()ping already processed Actions
            ElementActionOrder = SettingsDict['ElementActionOrder'] if 'ElementActionOrder' in SettingsDict else []
            ActionName = None
            if not isinstance(ElementActionOrder, list):
                ElementActionOrder = [ElementActionOrder]
            for i, ListElement in enumerate(ElementActionOrder):
                ActionName = ListElement
                ElementAction = ElementActions.pop(ActionName)
                ActionClass = ElementAction['Action']
                ActionType = ElementAction['Type']
                ElementActionFunction = getElementActionFunction(ActionClass)
                NewElements, Output = ElementActionFunction(ElementAction, Element, NumberedPoints, Elements, ExtendedData)
                #2013-04-20 Working here
                if Output: Format(FormatDict, ActionClass, Output, ExtendedData)

            for ElementAction in ElementActions:
                ActionClass = ElementActions[ElementAction]['Action']
                ElementActionFunction = getElementActionFunction(ActionClass)
                NewElements, Output = ElementActionFunction(ElementActions[ElementAction], Element, NumberedPoints, Elements, ExtendedData)
                #Points[Point], NumberedPoints and Elements get updated
                if Output: Format(FormatDict, ActionClass, Output, ExtendedData)


        Format(FormatDict, "Nodes", NumberedPoints['points'], ExtendedData)    #Forming Nodes document
        Format(FormatDict, "Elements", Elements, ExtendedData)                                                      #Forming Elements document

        #We have to merge ExtendedData information with the existing FormatDict
        FormatDict.update(dict((key, FormatDict[key] + value) for key, value in ExtendedData.iteritems() if key in range(1, 13))) #FREAKING SORCERY to merge lists under keys of two dicts
        WriteFormat = writeFormat(SettingsDict['Format'])
        WriteFormat(FormatDict, SettingsDict['OutputFile'])
        return True

    def Default():
        return

    functions = {
        'Lira-Custom' : LiraCustom,
        'DXF' : Dxf,
        'Default' : Default,
        }

    if SettingsDict['OutputType'] == 'Preset':
        return functions[SettingsDict['Name']]
    else:
        return functions['Default']