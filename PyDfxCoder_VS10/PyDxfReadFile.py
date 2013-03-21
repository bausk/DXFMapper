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


def dxfString():
    return """  0
    TEXT
      5
    470
    102
    {ACAD_XDICTIONARY
    360
    471
    102
    }
    330
    1F
    100
    AcDbEntity
      8
    0
    100
    AcDbText
     10
    17.0
     20
    17.0
     30
    0.0
     40
    3.0
      1
    TEXT
      7
    Notes
    100
    AcDbText
    1001
    AcadAnnotative
    1000
    AnnotativeData
    1002
    {
    1070
         1
    1070
         1
    1002
    }
    1001
    AcadAnnoPO
    1070
         1
    """
def readSettings():
    v = Validator()
    spec = ConfigObj("Parameters.spec", encoding = "UTF8", list_values=False)
    config = ConfigObj("Parameters.model", configspec = spec)
    config.validate(v)
    return config

def main():
    script, filename = argv
    settings = readSettings()
    for setting in settings:
        print settings[setting][]
        
    astring = unicode(open("../DXF Examples/" + filename + ".dxf").read())
    tags = ClassifiedTags.fromtext(unicode(open("../DXF Examples/" + filename + ".dxf").read()))
    #dxf = dxfgrabber.readfile()
    print tags



if __name__ == '__main__':
    main()
