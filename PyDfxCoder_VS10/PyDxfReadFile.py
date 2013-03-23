# Created: 08.03.13
# License: MIT License
from __future__ import unicode_literals
__author__ = "Alex Bausk <bauskas@gmail.com>"

from dxfgrabber.classifiedtags import ClassifiedTags
from dxfgrabber.entities import entity_factory
import dxfgrabber
import CoordinateTransform
from sys import argv
from configobj import ConfigObj
from validate import Validator
from dxfgrabber.drawing import Drawing
from io import StringIO


def readSettings():
    v = Validator()
    spec = ConfigObj("Parameters.spec", encoding = "UTF8", list_values=False)
    config = ConfigObj("Parameters.model", configspec = spec)
    config.validate(v)
    return config

def readSettingsKey(Section, Key, settings):
    if Section in settings and Key in settings[Section]:
        return settings[Section][Key]
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

def main():
    script, filename = argv
    Settings = readSettings()

    Filters = GetSections("Filter", Settings)
    for FilterName in Filters:
        #We iterate through filters, accept either filter values or general values or defaults
        #Then we can match the filter against the whole Drawing.entities collection
        #and map finite elements according to filter rules
        InputFile = readSettingsKey(FilterName, "InputFileList", Settings) or readSettingsKey("General", "InputFileList", Settings) or "Default.dxf"
        OutputFile = readSettingsKey(FilterName, "OutputFileList", Settings) or readSettingsKey("General", "OutputFileList", Settings) or "Default.lir"
        AxisXMapping = readSettingsKey(FilterName, "AxisXMapping", Settings) or readSettingsKey("General", "AxisXMapping", Settings) or "Default.lir"
        InputDxf = getDrawing(InputFile, False)
        Entities = InputDxf.entities






if __name__ == '__main__':
    main()
