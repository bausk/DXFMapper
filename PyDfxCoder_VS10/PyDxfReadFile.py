# Created: 08.03.13
# License: MIT License
from __future__ import unicode_literals
__author__ = "Alex Bausk <bauskas@gmail.com>"

from dxfgrabber.classifiedtags import ClassifiedTags
from dxfgrabber.entities import entity_factory
import dxfgrabber
import collections
from sys import argv
from configobj import ConfigObj
from validate import Validator
from dxfgrabber.drawing import Drawing
from io import StringIO
import CoordinateTransform
import ProcessObjects
import REDOutput
import sdxf
import PyDxfTools


def readSettings(filename):
    v = Validator()
    spec = ConfigObj("Parameters.spec", encoding = "UTF8", list_values=False)
    config = ConfigObj(filename, configspec = spec, encoding = "UTF8")
    config.validate(v)
    return config

def readSettingsKey(Section, Key, settings):
    if Section in settings and Key in settings[Section]:
        return (settings[Section][Key] or False)
    else:
        return False

def getDrawing(InputFile, GrabBlocks) :
    InputString = unicode(open(InputFile).read().decode('utf-8'))
    InputStream = StringIO(InputString)
    options = {
        'grab_blocks': False
    }
    return Drawing(InputStream, options)

def GetSections(Type, settings):
    SectionsSet = {}
    for Section in settings:
        if "Type" in settings[Section] and settings[Section]["Type"] == Type:
            SectionsSet[Section] = settings[Section]
    return SectionsSet

def FilterEntities(Entities, FilterName, SettingsDict):
    FilteredEntities = []

    Layer = False
    if 'Layer' in SettingsDict: Layer = SettingsDict['Layer']
    if Layer and not (type(Layer) is list): Layer = [Layer] #prevents from searching for substrings when doing in Layer
    Color = False
    if 'Color' in SettingsDict: Color = SettingsDict['Color']
    if Color and not (type(Color) is list): Color = [Color]
    FilterEntities = False
    if 'Entities' in SettingsDict: FilterEntities = SettingsDict['Entities']
    if FilterEntities and not (type(FilterEntities) is list): FilterEntities = [FilterEntities]
    FilterPoints = False
    if 'Points' in SettingsDict: FilterPoints = [int(x) for x in SettingsDict['Points']]
    if FilterPoints and not (type(FilterPoints) is list): FilterPoints = [FilterPoints]
    FilterClosed = False
    if 'Closed' in SettingsDict: FilterClosed = SettingsDict['Closed']

    for entity in Entities:
#        if entity.dxftype == 'LWPOLYLINE':
#            print
        try:
            if entity.is_closed == True: EntityClosed = 'yes'
            else: EntityClosed = 'no'
        except AttributeError:
            FilterClosed = False
        Condition = (not Layer or entity.layer in Layer) and \
                    (not Color or entity.color in Color) and \
                    (not FilterEntities or entity.dxftype in FilterEntities) and \
                    (not FilterPoints or len(entity.points) in FilterPoints) and \
                    (not FilterClosed or FilterClosed.lower() == EntityClosed)
        if Condition:
            FilteredEntities.append(entity)
    return FilteredEntities

def UpdateSetting(origin, u):
    d = origin.copy()
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = UpdateSetting(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

def main():
    script, filename = argv
    Settings = readSettings(filename)

    Filters = GetSections("Filter", Settings)
    EntitiesRefs = {} #Map to export entities
    EntitiesList = [] #Entities list

    FilteredEntities = {}
    ObjectList = {}
    Points = {}
    NodeNumber = 0
    ElementNumber = 0
    Nodes = [False]
    PointsNumbered = {'points' : {}, 'maximumNode' : None}
    DefaultFilter = GetSections("DefaultFilter", Settings)['DefaultFilter']
    Elements = [False]

    InputFile = readSettingsKey("DefaultFilter", "InputFileList", Settings) or "Default.dxf"
    InputDxf = getDrawing(InputFile, False)
    Entities = InputDxf.entities
    Entities = PyDxfTools.Overkill(Entities, DefaultFilter['Precision'])

    for FilterName in Filters:
        print "Input for filter %s\n" % FilterName
        #We iterate through filters, accept either filter values or general values or defaults
        #Then we can match the filter against the whole Drawing.entities collection
        #and map finite elements according to filter rules

        #1. Filter
        FinalizedSettings = UpdateSetting(DefaultFilter, Filters[FilterName])
        FilteredEntities[FilterName] = FilterEntities(Entities, FilterName, FinalizedSettings)

        print "Prep for filter %s\n" % FilterName
        #2. Preprocessor
        Preprocess = FinalizedSettings["PreprocessType"] if "PreprocessType" in FinalizedSettings else False
        PrepParameters = FinalizedSettings["Preprocess"] if "Preprocess" in FinalizedSettings else False
        PrepFunctionName = PrepParameters["Function"] if "Function" in PrepParameters else False
        PrepPrecision = FinalizedSettings["Precision"] if "Precision" in FinalizedSettings else 6
        PrepFunction = ProcessObjects.getFunction(Preprocess, PrepFunctionName)
        ObjectList[FilterName] = ProcessObjects.prep(FilteredEntities[FilterName], PrepFunction, PrepPrecision, PrepParameters)
        
        #3. Mapping    
        print "Mapping for filter %s\n" % FilterName
        Target = readSettingsKey(FilterName, "Target", Settings) or readSettingsKey("DefaultFilter", "Target", Settings) or False
        Mapping = readSettingsKey(FilterName, "Transformation mapping", Settings) or readSettingsKey("DefaultFilter", "Transformation mapping", Settings) or False
        if Mapping:
            FormulaX = CoordinateTransform.GetFormula(*Target['X'], Parameters = Mapping)
            FormulaY = CoordinateTransform.GetFormula(*Target['Y'], Parameters = Mapping)
            FormulaZ = CoordinateTransform.GetFormula(*Target['Z'], Parameters = Mapping)
            #X = FormulaX( {'X' : 10, 'Y' : 3, 'Z' : 1} )

        for object in ObjectList[FilterName]:
            #print "Input for object %s\n" % object
            for i, Point in enumerate(object['points']):
                if Mapping:
                    Coords = (
                            FormulaX( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]}),
                            FormulaY( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]}),
                            FormulaZ( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]})
                            )
                else:
                    Coords = (Point[0], Point[1], Point[2])
                object['points'][i] = tuple([round(x, PrepPrecision) for x in Coords])

        #4. Postprocessor
        #For the time being, we'll just compile the list of nodes
        #Placed in a separate loop for readability and structure
        print "Postp for filter %s\n" % FilterName
        for objnum, object in enumerate(ObjectList[FilterName]):
            for i, ElementName in enumerate(object['elements']):
                ElementNumber += 1
                Elements.append(None)
                ElementPoints = []
                ElementPointList = object['pointlist'][i]
                ElementData = object['data'][i] if 'data' in object else None
                for pointref in ElementPointList:
                    Point = object['points'][pointref] #Point referenced by the Element
                    if not Point in Points:
                        NodeNumber += 1
                        Points[Point] = { 'number': NodeNumber, 'elementnumbers': [], 'pointObjectReferences': [], 'additionalPoints': [] }
                        #PointsNumbered.append(None)
                        PointsNumbered['points'][NodeNumber] = {'point': Point, 'elementnumbers': []}
                        PointsNumbered['maximumNode'] = NodeNumber
                    CurrentPointNumber = Points[Point]['number']
                    ElementPoints.append(CurrentPointNumber)
                    #This one is used to reference ObjectList, possibly not needed
                    Points[Point]['pointObjectReferences'].append(ProcessObjects.REMapperPointRef(FilterName=FilterName, ObjectNumber=objnum, PointNumber=pointref))
                    Points[Point]['elementnumbers'].append(ElementNumber)
                    PointsNumbered['points'][CurrentPointNumber]['elementnumbers'].append(ElementNumber)
                Element = { 'points' : ElementPoints,
                           'elementclass' : ElementName,
                           'elementnum': ElementNumber, #???
                           'filter': FilterName,
                           'data': ElementData,
                           }
                Elements[ElementNumber] = Element

    #5. Export
    #We treat each export entry as a different one, but that has to change later
    Outputs = GetSections("Output", Settings)
    DefaultOutput = GetSections("DefaultOutput", Settings)['Default Output']
    for OutputName in Outputs:
        FinalizedSettings = UpdateSetting(DefaultOutput, Outputs[OutputName])
        OutputWriter = REDOutput.getFormatWriter(FinalizedSettings)
        OutputWriter(ObjectList, Filters, Points, PointsNumbered, Elements)
    

        #Check the list of filters against
#        Output = sdxf.Drawing()
#        for Entity in Entities:
#            print Entity.layer
#            Output.append(sdxf.Line(points=[(0, 0), (1, 1)], layer=Entity.layer))


if __name__ == '__main__':
    main()