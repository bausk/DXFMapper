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

    #1. Filter
    for FilterName in Filters:
        #We iterate through filters, accept either filter values or general values or defaults
        #Then we can match the filter against the whole Drawing.entities collection
        #and map finite elements according to filter rules

        Target = readSettingsKey(FilterName, "Target", Settings) or readSettingsKey("DefaultFilter", "Target", Settings)
        Mapping = readSettingsKey(FilterName, "Transformation mapping", Settings) or readSettingsKey("DefaultFilter", "Transformation mapping", Settings)
        #Origin = readSettingsKey(FilterName, "Origin", Settings) or readSettingsKey("DefaultFilter", "Origin", Settings)

        #Sweet sweet higher-order function
        #Parameters['R']['Origin']
        #ParameterSet = {}
        #for Variable in TransMapping:
        #    ReferenceOriginVariable = TransMapping[Variable][0] #Reference
        #    VariableOrigin = Origin[ReferenceOriginVariable]
        #    Scale = TransMapping[Variable][1] #Scale
        #    ParameterSet[Variable] = {
        #        'Origin' : VariableOrigin,
        #        'Scale' : Scale,
        #        }
        
        #To be removed to transformation
        FormulaX = CoordinateTransform.GetFormula(*Target['X'], Parameters = Mapping)
        X = FormulaX( {'R' : 10, 'Theta' : 3} )
        #


        #Now we can filter out the entities we want to transform.
        InputFile = readSettingsKey(FilterName, "InputFileList", Settings) or readSettingsKey("DefaultFilter", "InputFileList", Settings) or "Default.dxf"
        InputDxf = getDrawing(InputFile, False)
        Entities = InputDxf.entities
        #Iterate through entities and select ones that conform to the filter
        #Settings: Layer, Color etc.
        FilteredEntities[FilterName] = FilterEntities(Entities, FilterName, Settings)
        #End of 1.

    #Pre-mapping procedure
    #Settings:


        #Check the list of filters against
#        Output = sdxf.Drawing()
#        for Entity in Entities:
#            print Entity.layer
#            Output.append(sdxf.Line(points=[(0, 0), (1, 1)], layer=Entity.layer))


if __name__ == '__main__':
    main()