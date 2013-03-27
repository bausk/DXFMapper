# Created: 08.03.13
# License: MIT License
from __future__ import unicode_literals
__author__ = "Alex Bausk <bauskas@gmail.com>"

from dxfgrabber.classifiedtags import ClassifiedTags
from dxfgrabber.entities import entity_factory
import dxfgrabber
from sys import argv
from configobj import ConfigObj
from validate import Validator
from dxfgrabber.drawing import Drawing
from io import StringIO
import CoordinateTransform
import ProcessObjects
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

def main():
    script, filename = argv
    Settings = readSettings()

    Filters = GetSections("Filter", Settings)
    EntitiesRefs = {} #Map to export entities
    EntitiesList = [] #Entities list

    FilteredEntities = {}
    ObjectList = {}
    Points = {}

    for FilterName in Filters:
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
        PrepFunction = ProcessObjects.getFunction(Preprocess, PrepFunctionName)
        ObjectList[FilterName] = ProcessObjects.prep(FilteredEntities[FilterName], PrepFunction, PrepParameters)
        
        #3. Mapping    
        Target = readSettingsKey(FilterName, "Target", Settings) or readSettingsKey("DefaultFilter", "Target", Settings)
        Mapping = readSettingsKey(FilterName, "Transformation mapping", Settings) or readSettingsKey("DefaultFilter", "Transformation mapping", Settings)
        FormulaX = CoordinateTransform.GetFormula(*Target['X'], Parameters = Mapping)
        FormulaY = CoordinateTransform.GetFormula(*Target['Y'], Parameters = Mapping)
        FormulaZ = CoordinateTransform.GetFormula(*Target['Z'], Parameters = Mapping)
        #X = FormulaX( {'X' : 10, 'Y' : 3, 'Z' : 1} )
        for object in ObjectList[FilterName]:
            for i, Point in enumerate(object['points']):
                object['points'][i] = FormulaX( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]}), FormulaY( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]}), FormulaZ( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]})

        #4. Postprocessor
        #For the time being, we'll just compile the list of nodes
        #Placed in a separate loop for readability and structure
        NodeNumber = 0
        for objnum, object in enumerate(ObjectList[FilterName]):
            for i, Point in enumerate(object['points']):
                if not Point in Points:
                    NodeNumber += 1
                    Points[Point] = { 'number': NodeNumber, 'nodes': [] }
                Points[Point]['nodes'].append(ProcessObjects.REMapperPointRef(FilterName=FilterName, ObjectNumber=objnum, PointNumber=i))
        


    #5. Export
    #We treat each export entry as a different one, but that has to change later
    Outputs = GetSections("Output", Settings)
    for OutputName in Outputs:
        OutputFileName = readSettingsKey(FilterName, "OutputFile", Settings) or readSettingsKey("DefaultOutput", "OutputFile", Settings) or "Output.dxf"
        OutputFile = sdxf.Drawing()
        for FilterName in Filters:
            for compoundObject in ObjectList[FilterName]:
                for objectNum, objectType in enumerate(compoundObject['objects']):
                    if objectType == 'LINE_2NODES':
                        Point1 = compoundObject['points'][compoundObject['nodes'][objectNum][0]]
                        Point2 = compoundObject['points'][compoundObject['nodes'][objectNum][1]]
                        OutputFile.append(sdxf.Line(points=[Point1, Point2], layer="Lines"))
                    if objectType == 'SOLID_8NODES':
                        Point1 = compoundObject['points'][compoundObject['nodes'][objectNum][0]]
                        Point2 = compoundObject['points'][compoundObject['nodes'][objectNum][1]]
                        Point3 = compoundObject['points'][compoundObject['nodes'][objectNum][2]]
                        Point4 = compoundObject['points'][compoundObject['nodes'][objectNum][3]]
                        OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer="Faces"))
                        Point1 = compoundObject['points'][compoundObject['nodes'][objectNum][4]]
                        Point2 = compoundObject['points'][compoundObject['nodes'][objectNum][5]]
                        Point3 = compoundObject['points'][compoundObject['nodes'][objectNum][6]]
                        Point4 = compoundObject['points'][compoundObject['nodes'][objectNum][7]]
                        OutputFile.append(sdxf.Face(points=[Point1, Point2, Point3, Point4], layer="Faces"))


        #A variant
        #for Point in Points:
            #OutputFile.append(sdxf.Point(Point, layer="0"))
            #OutputFile.append(sdxf.Line(points=[(0,0,0), Point], layer="0"))
        OutputFile.saveas(OutputFileName)
    

        #Check the list of filters against
#        Output = sdxf.Drawing()
#        for Entity in Entities:
#            print Entity.layer
#            Output.append(sdxf.Line(points=[(0, 0), (1, 1)], layer=Entity.layer))


if __name__ == '__main__':
    main()