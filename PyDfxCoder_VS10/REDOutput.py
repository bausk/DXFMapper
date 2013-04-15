from math import *
import collections
import sdxf
import ShadowbinderDataTools
from ShadowbinderFormats import *
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

        #For any given point Point, including its ['additionalPoints'], if any
        #1. Find all elements that connect to Point and whose filters are in Parameters['Filters']
        #2. Find all elements that are LINE_2NODE
        #3. Parameters['Direction'] gives the rule to identify fisrt and last vector points from LINE_2NODE
        #4. Compute vector sum of the obtained vectors.
        #5. Write node number and vector sum into Output
        if not Output: return False, False
        return False, Output

    def Default():
        return False, False

    functions = {
        'Compatible Nodes' : CompatibleNodes,
        'Rotate Nodes' : RotateNodes,
        'Default' : Default,
        }

    if PointAction in functions:
        return functions[PointAction]
    else:
        return functions['Default']

def getFormatWriter(SettingsDict):

    def Dxf(Objects, Filters, Points, NumberedPoints, Elements):
        OutputFile = sdxf.Drawing()
        for FilterName in Filters:
            print "Output for filter %s\n" % FilterName
            for compoundObject in Objects[FilterName]:
                for objectNum, objectType in enumerate(compoundObject['elements']):
                    if objectType == 'LINE_2NODES':
                        Point1 = compoundObject['points'][compoundObject['pointlist'][objectNum][0]]
                        Point2 = compoundObject['points'][compoundObject['pointlist'][objectNum][1]]
                        OutputFile.append(sdxf.Line(points=[Point1, Point2], layer="Lines"))
                    if objectType == 'SOLID_8NODES':
                        Point1 = compoundObject['points'][compoundObject['pointlist'][objectNum][0]]
                        Point2 = compoundObject['points'][compoundObject['pointlist'][objectNum][1]]
                        Point3 = compoundObject['points'][compoundObject['pointlist'][objectNum][2]]
                        Point4 = compoundObject['points'][compoundObject['pointlist'][objectNum][3]]
                        OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer="Faces"))
                        Point1 = compoundObject['points'][compoundObject['pointlist'][objectNum][4]]
                        Point2 = compoundObject['points'][compoundObject['pointlist'][objectNum][5]]
                        Point3 = compoundObject['points'][compoundObject['pointlist'][objectNum][6]]
                        Point4 = compoundObject['points'][compoundObject['pointlist'][objectNum][7]]
                        OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer="Faces"))
                    if objectType == 'SOLID_6NODES':
                        Point1 = compoundObject['points'][compoundObject['pointlist'][objectNum][0]]
                        Point2 = compoundObject['points'][compoundObject['pointlist'][objectNum][1]]
                        Point3 = compoundObject['points'][compoundObject['pointlist'][objectNum][2]]
                        OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point3], layer="Faces"))
                        Point1 = compoundObject['points'][compoundObject['pointlist'][objectNum][3]]
                        Point2 = compoundObject['points'][compoundObject['pointlist'][objectNum][4]]
                        Point3 = compoundObject['points'][compoundObject['pointlist'][objectNum][5]]
                        OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point3], layer="Faces"))
                    if objectType == 'FACE_3NODES':
                        Point1 = tuple(list(compoundObject['points'][compoundObject['pointlist'][objectNum][0]])[0:2])
                        Point2 = tuple(list(compoundObject['points'][compoundObject['pointlist'][objectNum][1]])[0:2])
                        Point3 = tuple(list(compoundObject['points'][compoundObject['pointlist'][objectNum][2]])[0:2])
                        OutputFile.append(sdxf.LwPolyLine(points=[Point1, Point2, Point3], flag=1, layer="Polylines"))
                        OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point3], layer="Faces"))
                    if objectType == 'FACE_4NODES':
                        Point1 = compoundObject['points'][compoundObject['pointlist'][objectNum][0]]
                        Point2 = compoundObject['points'][compoundObject['pointlist'][objectNum][1]]
                        Point3 = compoundObject['points'][compoundObject['pointlist'][objectNum][2]]
                        Point4 = compoundObject['points'][compoundObject['pointlist'][objectNum][3]]
                        OutputFile.append(sdxf.LwPolyLine(points=[Point1, Point2, Point3, Point4], flag=1, layer="Polylines"))
                        OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer="Faces"))
        OutputFile.saveas(SettingsDict['OutputFile'])
        return True

    def LiraCustom(Objects, Filters, Points, NumberedPoints, Elements):
        #Objects is formed in prep Functions, which is the ABSOLUTELY WRONG WAY TO DO THINGS
        #Objects[str(filter)]['points'][A] = tuple(3), links to Points
        #Objects[str(filter)]'[pointlist'][tuple(2..8)] = links to A^
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
        def PointActionFunction():
            return True

        Format = getFormat(SettingsDict['Format'])
        FormatDictInitializer = initFormat(SettingsDict['Format'], __name__)
        FormatDict = FormatDictInitializer(False)
        #First: routine to check point actions
        for Point in Points:
            #Check if there are points with filters belonging to actions
            #
            PointActions = SettingsDict['Point Actions'].copy() #Copying because we will be pop()ping already processed Actions
            PointActionOrder = SettingsDict['PointActionOrder']
            ActionName = None
            #aaa = dict((ActionName, PointActions[ActionName]) for ActionIndex, ActionName in enumerate(PointActionOrder))
            #bbb = {}
            #for ccc in aaa:
            #    print

            #The first loop goes through ordered Point Actions, the 
            for i, ListElement in enumerate(PointActionOrder):
                ActionName = PointActionOrder[i]
                PointAction = PointActions.pop(ActionName)
                PointActionFunction = getPointActionFunction(ActionName)
                NewPoints, Output = PointActionFunction(PointAction, Points[Point], Point, NumberedPoints, Elements)
                if Output: Format(FormatDict, ActionName, Output)

            for PointAction in PointActions:
                PointActionFunction = getPointActionFunction(PointAction)
                NewPoints, Output = PointActionFunction(PointActions[PointAction], Points[Point], Point, NumberedPoints, Elements)
                #Points[Point], NumberedPoints and Elements get updated
                if Output: Format(FormatDict, PointAction, Output)
                #if NewPoints: NumberedPoints.update(NewPoints) #Already done in PointActionFunction
            
            #FilterName = Point['pointObjectReferences'].FilterName
        Format(FormatDict, "Nodes", NumberedPoints['points'])    #Forming Nodes document
        Format(FormatDict, "Elements", Elements)                                                        #Forming Elements document
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