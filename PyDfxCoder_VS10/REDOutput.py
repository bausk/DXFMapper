from math import *
import collections
import sdxf
import ShadowbinderDataTools

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
        NewPoints = []
        NewNumberedPoints = {}
        FirstFilter = Parameters['Filters'][0] #First filter: its elements will stay with the Point
        FiltersInParameters = Parameters['Filters'][1:] #All except the first: these ones are given new Points with same coords
        FiltersInPoint = [x.FilterName for x in Point['pointObjectReferences']]
        PointNumber = len(NumberedPoints)
        PointNumber2 = len(NumberedPoints) - 1
        if not FirstFilter in FiltersInPoint: return False #No elements from first filter? Not our client
        #for j, FilterInPoint in enumerate(FiltersInPoint):
        #    if FilterInPoint in Filters:
        #        if not FilterInPoint in NewPoints2:
        #            PointNumber2 += 1
        #            NewPoints2[FilterInPoint] = PointNumber2
        #            NumberedPoints.append(None)
        #            NumberedPoints[PointNumber2] = PointTuple
                
        #        print NewPoints2[FilterInPoint] # equals our point number


        for ParameterFilter in FiltersInParameters: #ParameterFilter will correspond to a New Point if we find any matches
            #If elements in this point have a filter equal to ParameterFilter, then we create a new point
            ElementIndices = [i for i, x in enumerate(FiltersInPoint) if x == ParameterFilter] #Which elements referenced by Point in Point['elementnumbers'] contain this Filter?
            #if not, then no elements are repatched and no new points are created.
            if ElementIndices: #This ParameterFilter exists in FiltersInPoint for elements referenced by ElementIndices
                #ElementIndices contain elements that are referenced in Point and were created
                NewNumberedPoints.append(PointNumber)
                #Point['number'] is where index for NumberedPoints is stored. We enhance it with new points.
                #No, we don't, because we want to avoid another for loop where possible.
                #Can we actually write the document already? Yep we can.
                for index in ElementIndices:
                    #We go through all elements that bind to this point and were produced by theParameterFilter
                    ElementNumber, ElementPointIndex = ShadowbinderDataTools.getElementFromPoint(Point, index)

                    #Gives us the element number in question that has to be patched
                    #gives actual point index in Elements[ElementNumber]



                NewPoints.append(PointNumber)

                #Point['elementnumbers']
                NumberedPoints.append(None) #To be extra sure about the number.
                NumberedPoints[PointNumber] = PointTuple
                PointNumber += 1
        if not NewNumberedPoints: return False #Not a single filter matches
        return NewNumberedPoints

    def RotateNodes(Parameters, Point, PointTuple, NumberedPoints, Elements):
        return True

    def Default():
        return True

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


        #A variant
        #for Point in Points:
            #OutputFile.append(sdxf.Point(Point, layer="0"))
            #OutputFile.append(sdxf.Line(points=[(0,0,0), Point], layer="0"))
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

        #First: routine to check point actions
        for Point in Points:
            #Check if there are points with filters belonging to actions
            #
            PointActions = SettingsDict['Point Actions']
            for PointAction in PointActions:
                PointActionFunction = getPointActionFunction(PointAction)
                NewPoints = PointActionFunction(PointActions[PointAction], Points[Point], Point, NumberedPoints, Elements)
                
            #FilterName = Point['pointObjectReferences'].FilterName

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