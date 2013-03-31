from math import *
import collections
import sdxf

#from PyDxfTools import GetPoints

#PrepDxfObject = collections.namedtuple('PrepDxfObject', ['x', 'y'])
#REMapperPointRef = collections.namedtuple('REMapperPointRef', ['FilterName', 'ObjectNumber', 'PointNumber'])

#def postp(Points, Settings):
#    Result = []
#    for FilteredEntity in FilteredEntities:
#        Object = Function(FilteredEntity, Parameters)
#        Result.append(Object)
#    return Result

def getFormatWriter(SettingsDict):

    def Dxf(Objects, Filters, Points, Nodes, Elements):
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
        #Elements[PointNumber]['points']        = ((Point), ...)
        #                     ['elementclass']  = ElementClass
        #                     ['elementnum']    = ElementNumber
        #Points[(Point)]['number']                = PointNumber
        #               ['elements']              = (ElementNumber, ...)
        #               ['pointObjectReferences'] = (FilterName, ObjectNumber, PointNumber)
        #PointsNumbered[PointNumber]['point']   = pointTuple
        #Okay let's go.

        #First: routine to check point actions
        for Point in Points:
            #Check if there are points with filters belonging to actions
            #
            PointActions = 
            Point['pointObjectReferences'].FilterName

        return true

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