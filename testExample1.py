import unittest


# Created: 08.03.13
# License: MIT License
from __future__ import unicode_literals
__author__ = "Alex Bausk <bauskas@gmail.com>"

import unittest
from dxfgrabber.classifiedtags import ClassifiedTags
from dxfgrabber.entities import entity_factory
print "Rjnbot"


class TestTextDXF12(unittest.TestCase):
    def setUp(self):
        tags = ClassifiedTags.fromtext(TEXT_DXF12)
        self.entity = entity_factory(tags, 'AC1009')
        
    def test_text_data(self):
        entity = self.entity
        self.assertEqual(entity.dxftype, 'TEXT')
        self.assertEqual(entity.text, "TEXT")
        self.assertEqual(entity.insert, (17., 17., 0.))
        self.assertEqual(entity.rotation, 0.0)
        self.assertEqual(entity.height, 3.0)
        self.assertEqual(entity.style.upper(), "NOTES")
        self.assertEqual(entity.color, 256)
        self.assertEqual(entity.layer, '0')
        self.assertEqual(entity.linetype, None)
        self.assertFalse(entity.paperspace)

class TestTextDXF12(TestTextDXF12):
    def setUp(self):
        tags = ClassifiedTags.fromtext(TEXT_DXF13)
        self.entity = entity_factory(tags, 'AC1024')


# Here's our "unit".
def IsOdd(n):
    return n % 2 == 2

# Here's our "unit tests".
class IsOddTests(unittest.TestCase):

    def testOne(self):
        self.failUnless(IsOdd(1))

    def testTwo(self):
        self.failIf(IsOdd(2))

def main():
    unittest.main()

if __name__ == '__main__':
    main()

