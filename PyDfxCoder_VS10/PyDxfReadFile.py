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


def readSettings():
    v = Validator()
    spec = ConfigObj("Parameters.spec", encoding = "UTF8", list_values=False)
    config = ConfigObj("Parameters.model", configspec = spec, encoding = "UTF8")
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

def FilterEntities(Entities, FilterName, Settings):
    FilteredEntities = []
    Layer = readSettingsKey(FilterName, "Layer", Settings) or readSettingsKey("DefaultFilter", "Layer", Settings) or False
    if Layer and not (type(Layer) is list): Layer = [Layer] #prevents from searching for substrings when doing in Layer
    Color = readSettingsKey(FilterName, "Color", Settings) or readSettingsKey("DefaultFilter", "Color", Settings) or False
    if Color and not (type(Color) is list): Color = [Color]
    for entity in Entities:
        if not Layer or entity.layer in Layer:
            FilteredEntities.append(entity)
    return FilteredEntities

def UpdateSetting(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = UpdateSetting(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

def main():
    script, filename = argv
    Settings = readSettings()

    Filters = GetSections("Filter", Settings)
    EntitiesRefs = {} #Map to export entities
    EntitiesList = [] #Entities list

    FilteredEntities = {}
    ObjectList = {}
    Points = {}
    NodeNumber = 0
    ElementNumber = 0
    Nodes = [False]
    PointsNumbered = [False]
    Elements = [False]
    for FilterName in Filters:
        print "Input for filter %s\n" % FilterName
        #We iterate through filters, accept either filter values or general values or defaults
        #Then we can match the filter against the whole Drawing.entities collection
        #and map finite elements according to filter rules

        #1. Filter
        InputFile = readSettingsKey(FilterName, "InputFileList", Settings) or readSettingsKey("DefaultFilter", "InputFileList", Settings) or "Default.dxf"
        InputDxf = getDrawing(InputFile, False)
        Entities = InputDxf.entities
        FilteredEntities[FilterName] = FilterEntities(Entities, FilterName, Settings)

        #2. Preprocessor
        Preprocess = readSettingsKey(FilterName, "Preprocess", Settings) or readSettingsKey("DefaultFilter", "Preprocess", Settings) or False
        PrepFunctionName = readSettingsKey(FilterName, "PreprocessFunction", Settings) or readSettingsKey("DefaultFilter", "PreprocessFunction", Settings) or False
        PrepParameters = readSettingsKey(FilterName, "PreprocessParameter", Settings) or readSettingsKey("DefaultFilter", "PreprocessParameter", Settings) or False
        PrepPrecision = readSettingsKey(FilterName, "Precision", Settings) or readSettingsKey("DefaultFilter", "Precision", Settings) or 6
        PrepFunction = ProcessObjects.getFunction(Preprocess, PrepFunctionName)
        ObjectList[FilterName] = ProcessObjects.prep(FilteredEntities[FilterName], PrepFunction, PrepPrecision, PrepParameters)
        
        #3. Mapping    
        Target = readSettingsKey(FilterName, "Target", Settings) or readSettingsKey("DefaultFilter", "Target", Settings)
        Mapping = readSettingsKey(FilterName, "Transformation mapping", Settings) or readSettingsKey("DefaultFilter", "Transformation mapping", Settings)
        FormulaX = CoordinateTransform.GetFormula(*Target['X'], Parameters = Mapping)
        FormulaY = CoordinateTransform.GetFormula(*Target['Y'], Parameters = Mapping)
        FormulaZ = CoordinateTransform.GetFormula(*Target['Z'], Parameters = Mapping)
        #X = FormulaX( {'X' : 10, 'Y' : 3, 'Z' : 1} )
        for object in ObjectList[FilterName]:
            #print "Input for object %s\n" % object
            for i, Point in enumerate(object['points']):
                Coords = (
                        FormulaX( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]}),
                        FormulaY( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]}),
                        FormulaZ( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]})
                        )
                object['points'][i] = tuple([round(x, PrepPrecision) for x in Coords])

        #4. Postprocessor
        #For the time being, we'll just compile the list of nodes
        #Placed in a separate loop for readability and structure
        for objnum, object in enumerate(ObjectList[FilterName]):
            for i, ElementName in enumerate(object['elements']):
                ElementNumber += 1
                Elements.append(None)
                ElementPoints = ()
                ElementPointList = object['pointlist'][i]
                for pointref in ElementPointList:
                    Point = object['points'][pointref]
                    ElementPoints = ElementPoints + (Point, )
                    if not Point in Points:
                        NodeNumber += 1
                        Points[Point] = { 'number': NodeNumber, 'elements': [], 'pointrefs': [] }
                        PointsNumbered.append(None)
                        PointsNumbered[NodeNumber] = Point
                    #This one is used to reference ObjectList, possibly not needed
                    if len(Points[Point]['pointrefs']) > 1:
                        if Points[Point]['pointrefs'][-1][0] != FilterName:
                            print Point, NodeNumber
                    Points[Point]['pointrefs'].append(ProcessObjects.REMapperPointRef(FilterName=FilterName, ObjectNumber=objnum, PointNumber=NodeNumber))

                    Points[Point]['elements'].append(ElementNumber)
                Element = { 'points' : ElementPoints,
                           'elementclass' : ElementName,
                           'elementnum': ElementNumber
                           }
                Elements[ElementNumber] = Element

    #5. Export
    #We treat each export entry as a different one, but that has to change later
    Outputs = GetSections("Output", Settings)
    DefaultOutput = GetSections("DefaultOutput", Settings)['Default Output']
    for OutputName in Outputs:
        FinalizedSettings = UpdateSetting(DefaultOutput, Outputs[OutputName])
        OutputWriter = REDOutput.getFormatWriter(FinalizedSettings)
        OutputWriter(ObjectList, Filters, Points, Nodes, Elements)
    

        #Check the list of filters against
#        Output = sdxf.Drawing()
#        for Entity in Entities:
#            print Entity.layer
#            Output.append(sdxf.Line(points=[(0, 0), (1, 1)], layer=Entity.layer))


if __name__ == '__main__':
    main()