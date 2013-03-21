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

def main():
    script, filename = argv
    settings = readSettings()
    InputFile = readSettingsKey("Input", "File", settings) or "Default.dxf"
    OutputFile = readSettingsKey("Output", "File", settings) or "Default.lir"

    #astring = unicode(open("../DXF Examples/" + filename + ".dxf").read())
    #tags = ClassifiedTags.fromtext(unicode(open(InputFile).read()))
    stream = StringIO(unicode(open(InputFile).read()))
    options = {
        'grab_blocks': False
    }
    dwg = Drawing(stream, options)
    #DxfDrawing = Drawing
    print tags



if __name__ == '__main__':
    main()
