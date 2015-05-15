# Created: 08.03.13
# License: MIT License
from __future__ import unicode_literals
__author__ = "Alex Bausk <bauskas@gmail.com>"

#from dxfgrabber.classifiedtags import ClassifiedTags
from dxfgrabber.entities import entity_factory
import dxfgrabber
import collections


from configobj import ConfigObj
from validate import Validator

import CoordinateTransform
import ProcessObjects
import REDOutput
import sdxf
import PyDxfTools
from PyDxfTools import getDrawing, getEntities
from Settings import *
from ShadowbinderDataTools import Neighborhood


def main():
    script, filename = init()
    Settings = readSettings(filename)

    UnorderedFilters = GetSections("Filter", Settings)
    EntitiesRefs = {} #Map to export entities
    EntitiesList = [] #Entities list
    FilteredEntities = {}
    ObjectList = {}
    Points = {}
    NodeNumber = 0
    ElementNumber = 0
    Nodes = [False]
    PointsNumbered = {'points' : {}, 'maximumNode' : None}
    DefaultFilter = GetSections("DefaultFilter", Settings)['DefaultFilter'] if 'DefaultFilter' in Settings else {'Type':'DefaultFilter','Precision':8,'Entities':'NONE'}
    Elements = [False]
    GlobalPointIndex = [(0,0,0)]
    FilterOrder = DefaultFilter['FilterOrder'] if 'FilterOrder' in DefaultFilter else False
    Filters = collections.OrderedDict()
    if FilterOrder and type(FilterOrder) is list:
        for FilterName in FilterOrder:
            Filters[FilterName] = UnorderedFilters.pop(FilterName)
    Filters.update(UnorderedFilters)

    for FilterName in Filters:
        print "\nReading entities for filter '%s'." % FilterName
        #We iterate through filters, accept either filter values or general values or defaults
        #Then we can match the filter against the whole Drawing.entities collection
        #and map finite elements according to filter rules

        #1. Filter
        FinalizedSettings = UpdateSetting(DefaultFilter, Filters[FilterName])
        InputFileList = FinalizedSettings["InputFileList"] if "InputFileList" in FinalizedSettings else "Drawing1.dxf"
        Precision = FinalizedSettings["Precision"] if "Precision" in FinalizedSettings else 8
        Tolerance = FinalizedSettings["Tolerance"] if "Tolerance" in FinalizedSettings else 0.00000001
        CheckNeighbors = FinalizedSettings["CheckNeighbors"] if "CheckNeighbors" in FinalizedSettings else False
        IncludeInIndex = FinalizedSettings["IncludeInIndex"] if "IncludeInIndex" in FinalizedSettings else False
        #InputFile = readSettingsKey("DefaultFilter", "InputFileList", Settings) or "Default.dxf"
        #InputDxf = getDrawing(InputFile, False)
        Entities = getEntities(InputFileList, False)

        if "Overkill" in FinalizedSettings and FinalizedSettings["Overkill"].lower() == 'yes':
            Entities = PyDxfTools.Overkill(Entities, Precision)
        FilteredEntities[FilterName] = FilterEntities(Entities, FilterName, FinalizedSettings)

        print "\nPreprocessing for filter '%s'..." % FilterName
        #2. Preprocessor
        Preprocess = FinalizedSettings["PreprocessType"] if "PreprocessType" in FinalizedSettings else False
        PrepParameters = FinalizedSettings["Preprocess"] if "Preprocess" in FinalizedSettings else False
        PrepFunctionName = PrepParameters["Function"] if "Function" in PrepParameters else False
        PrepPrecision = FinalizedSettings["Precision"] if "Precision" in FinalizedSettings else 6
        PrepFunction = ProcessObjects.getFunction(Preprocess, PrepFunctionName)
        ObjectList[FilterName] = ProcessObjects.prep(FilteredEntities[FilterName], PrepFunction, PrepPrecision, PrepParameters)
        
        #3. Mapping    
        print "Mapping for filter '%s'..." % FilterName
        Target = FinalizedSettings["Target"] if "Target" in FinalizedSettings else False
        Mapping = FinalizedSettings["Transformation mapping"] if "Transformation mapping" in FinalizedSettings else False
        Postmapping = FinalizedSettings["Postmapping"] if "Postmapping" in FinalizedSettings else False
        if not Postmapping: Postmapping = {'X': 0, 'Y': 0, 'Z': 0}
        if Mapping:
            FormulaX = CoordinateTransform.GetFormula(*Target['X'], Parameters = Mapping)
            FormulaY = CoordinateTransform.GetFormula(*Target['Y'], Parameters = Mapping)
            FormulaZ = CoordinateTransform.GetFormula(*Target['Z'], Parameters = Mapping)
            #X = FormulaX( {'X' : 10, 'Y' : 3, 'Z' : 1} )

        for object in ObjectList[FilterName]:
            #print "Input for object %s\n" % object
            #print "Processing object %s in dataset%s\n" % (object, FilterName)
            for i, Point in enumerate(object['points']):
                Coords = (Point[0], Point[1], Point[2])
                if Mapping:
                    Coords = (
                            FormulaX( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]}),
                            FormulaY( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]}),
                            FormulaZ( {'X': Point[0], 'Y': Point[1], 'Z': Point[2]})
                            )
                Coords = (Coords[0] + Postmapping['X'], Coords[1] + Postmapping['Y'], Coords[2] + Postmapping['Z'])
                #Check tolerances
                if CheckNeighbors == 'Yes':
                    object['points'][i] = Neighborhood(tuple([round(x, PrepPrecision) for x in Coords]), PrepPrecision, GlobalPointIndex) if CheckNeighbors == "Yes" else tuple([round(x, PrepPrecision) for x in Coords])
                elif IncludeInIndex == 'Yes':
                    object['points'][i] = tuple([round(x, PrepPrecision) for x in Coords])
                    if not object['points'][i] in GlobalPointIndex:
                        GlobalPointIndex.append(object['points'][i])
                else:
                    object['points'][i] = tuple([round(x, PrepPrecision) for x in Coords])
        #4. Postprocessor
        #For the time being, we'll just compile the list of nodes
        #Placed in a separate loop for readability and structure
        print "Postprocessing for filter '%s'..." % FilterName
        for objnum, object in enumerate(ObjectList[FilterName]):
            EntityModelData = object['entity_model_data'] if 'entity_model_data' in object else None
            for i, ElementName in enumerate(object['elements']):
                ElementNumber += 1
                Elements.append(None)
                ElementPoints = []
                ElementPointList = object['pointlist'][i]
                ExtendedModelData = object['extended_model_data'][i] if 'extended_model_data' in object and len(object['extended_model_data']) else None
                GenerationOrder = object['generation_order'][i] if 'generation_order' in object else None
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
                           'entity_model_data': EntityModelData,
                           'extended_model_data': ExtendedModelData,
                           'generation_order': GenerationOrder,
                           }
                Elements[ElementNumber] = Element

    #5. Export
    #We treat each export entry as a different one, but that has to change later
    Outputs = GetSections("Output", Settings)
    DefaultOutput = GetSections("DefaultOutput", Settings)["DefaultOutput"] if "DefaultOutput" in Settings else {'Type':'DefaultOutput', 'Name':None, 'OutputType':'None'}
    for OutputName in Outputs:
        print "\nWriting output rule '{}'.\n".format(OutputName)
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