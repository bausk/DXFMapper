from math import *
import collections
import sdxf
import ShadowbinderDataTools
from ShadowbinderFormats import *
import simplejson as json
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

        Output = []
        if 'CutoffZ' in Parameters:
            Position = PointTuple[2]
            if Position < float(Parameters['CutoffZ'][0]) or Position > float(Parameters['CutoffZ'][1]): return False, []
        NewPointIndex = NumberedPoints['maximumNode']
        NewNumberedPoints = {}
        FirstFilter = Parameters['Filters'][0] #First filter: its elements will stay with the Point
        FiltersInParameters = Parameters['Filters'][1:] #All except the first: these ones are given new Points with same coords
        FiltersInPoint = [x.FilterName for x in Point['pointObjectReferences']]
        if not FirstFilter in FiltersInPoint: return  False, [] #No elements from first filter? Not our client
        OldPointIndex = Point['number']
        Output.append(OldPointIndex)
        for ParameterFilter in FiltersInParameters: #ParameterFilter will correspond to a New Point if we find any matches
            #If elements in this point have a filter equal to ParameterFilter, then we create a new point
            ElementIndices = [i for i, x in enumerate(FiltersInPoint) if x == ParameterFilter] #Which elements referenced by Point in Point['elementnumbers'] contain this Filter?
            #if not, then no elements are repatched and no new points are created.
            if ElementIndices: #This ParameterFilter exists in FiltersInPoint for elements referenced by ElementIndices
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

    def ElementForce(Parameters, Element, NumberedPoints, Elements):
        #Okay
        Output = {}
        if not Element: return False, False
        #First, define if element needs the ElementAction
        if 'Filters' in Parameters:
            FiltersInParameters = Parameters['Filters']
            ElementFilter = Element['filter']
            if not ElementFilter in FiltersInParameters: return False, False
        if 'Markers' in Parameters:
            if not isinstance(Parameters['Markers'], list): Parameters['Markers'] = [Parameters['Markers']]
            Markers = dict(Marker.split(':') for Marker in Parameters['Markers'])
            #Markers are checked against Element's entity_model_data
            #Element should satisfy all markers
            for marker, value in Markers.iteritems():
                ElementValue = str(Element['entity_model_data'][marker]) if Element['entity_model_data'] and (marker in Element['entity_model_data']) else None
                if marker == "generation_order":
                    ElementValue = Element['generation_order']
                if str(value) != str(ElementValue) : return False, False
                
        if Parameters['Type'] == "Dilatation":
            LoadID = 8
            ElementNumber = Element['elementnum']
            Output['load_id'] = LoadID
            Output['direction'] = 1
            Output['element'] = ElementNumber
            Output['loadcase'] = 1
            Output['value'] = Parameters['Value']
            Output['string'] = "{} 0.05 0 0".format(Output['value'])
        elif Parameters['Type'] == "VolumePressure":
            ForceValue = json.loads(Parameters['Value'])
            LoadID = ForceValue['loadtype']
            ElementNumber = Element['elementnum']
            Output['load_id'] = LoadID
            Output['direction'] = ForceValue['axis']
            Output['element'] = ElementNumber
            Output['loadcase'] = 1
            Output['value'] = ForceValue['value']
            Output['string'] = "{} {} 0 0".format(Output['value'], ForceValue['face'])

        return False, Output

    def AssignLayer(Parameters, Element, NumberedPoints, Elements):
        ElementFilter = Element['filter']
        AssignedLayers = json.loads(Parameters['Layers'])
        if ElementFilter in AssignedLayers:
            AssignedLayer = AssignedLayers[ElementFilter]
            Element['entity_model_data']['layer'] = AssignedLayer
        return False, False

    def ElementProperty(Parameters, Element, NumberedPoints, Elements):
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


def ProcessGlobalAction(ActionType, GlobalAction, NumberedPoints, Elements):
    ExtendedData = {'ElementPropertyIndex' : {}}
    if ActionType == 'ElementProperties':
        Output = {}
        for index, key in enumerate(GlobalAction):
            index += 1
            ExtendedData['ElementPropertyIndex'][key] = index #In this same notation we can get the index when writing elements
            Output[index] = GlobalAction[key]
        return ExtendedData, Output #Here we have Output ready to be printed and ExtendedData, a mapper to Output
    if ActionType == 'Orphans':
        Output = []
        for Number, Point in NumberedPoints['points'].iteritems():
            ElementAmount = len(Point['elementnumbers'])
            if ElementAmount < 2:
                print "Orphan node {}!".format(Number)
                Output.append({'element_type': 'POINT', 'position': Point['point'], 'layer': 'Errors', 'nodenumber': Number})
        return {'information':'addObjects'}, Output#Here we have Output ready to be printed and ExtendedData, a mapper to Output
    return False


def getFormatWriter(SettingsDict):

    def Dxf(Objects, Filters, Points, NumberedPoints, Elements):
        OutputFile = sdxf.Drawing()
        #ExtendedData = {}
        GlobalActions = SettingsDict['Actions'].copy() if 'Actions' is SettingsDict else {}
        GlobalActionOrder = SettingsDict['ActionOrder'] if 'ActionOrder' in SettingsDict else False
        for GlobalAction in GlobalActions:
            ActionType = GlobalActions[GlobalAction].pop('Type')
            ExtendedData, Output = ProcessGlobalAction(ActionType, GlobalActions[GlobalAction], NumberedPoints, Elements)
            if ExtendedData['information'] == 'addObjects':
                for Item in Output:
                    if Item['element_type'] == 'POINT':
                        OutputFile.append(sdxf.Text(text=Item['nodenumber'], point=Item['position'], layer=Item['layer']))


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
                NewElements, Output = ElementActionFunction(ElementAction, Element, NumberedPoints, Elements)
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
                Point1 = NumberedPoints['points'][compoundObject['points'][0]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][2]]['point']
                Point4 = NumberedPoints['points'][compoundObject['points'][3]]['point']
                OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer=objectLayer))
                Point1 = NumberedPoints['points'][compoundObject['points'][4]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][5]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][6]]['point']
                Point4 = NumberedPoints['points'][compoundObject['points'][7]]['point']
                OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer=objectLayer))
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
                Point1 = NumberedPoints['points'][compoundObject['points'][1]]['point']
                Point2 = NumberedPoints['points'][compoundObject['points'][2]]['point']
                Point3 = NumberedPoints['points'][compoundObject['points'][3]]['point']
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
            if objectType == 'POLYLINE':
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
        ExtendedData = {}
        #First: routine to check point actions
        GlobalActions = SettingsDict['Actions'].copy() if 'Actions' is SettingsDict else {}
        GlobalActionOrder = SettingsDict['ActionOrder'] if 'ActionOrder' in SettingsDict else False
        for GlobalAction in GlobalActions:
            ActionType = GlobalActions[GlobalAction].pop('Type')
            NewExtendedData, Output = ProcessGlobalAction(ActionType, GlobalActions[GlobalAction], NumberedPoints, Elements)
            ExtendedData.update(NewExtendedData)
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

        for Element in Elements:
            
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
                NewElements, Output = ElementActionFunction(ElementAction, Element, NumberedPoints, Elements)
                #2013-04-20 Working here
                if Output: Format(FormatDict, ActionClass, Output, ExtendedData)

            for ElementAction in ElementActions:
                ActionClass = ElementActions[ElementAction]['Action']
                ElementsActionFunction = getElementActionFunction(ActionClass)
                NewElements, Output = ElementActionFunction(ElementActions[ElementAction], Element, NumberedPoints, Elements)
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