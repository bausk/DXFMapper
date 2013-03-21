# Created: 08.03.13
# License: MIT License
from __future__ import unicode_literals
__author__ = "Alex Bausk <bauskas@gmail.com>"

from dxfgrabber.classifiedtags import ClassifiedTags
from dxfgrabber.entities import entity_factory

def main():
    #unittest.main()
    tags = ClassifiedTags.fromtext(TEXT_DXF12)
    entity = entity_factory(tags, 'AC1009')
    print entity.layer;


if __name__ == '__main__':
    main()