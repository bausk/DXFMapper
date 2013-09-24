from math import *
import collections
import sdxf
import ShadowbinderDataTools
from ShadowbinderDataTools import NeighborhoodRaw
from ShadowbinderFormats import *
from meshpy.tet import MeshInfo, build, Options
from pyautocad import Autocad, APoint

import simplejson as json
#import numpy as np
#import scipy.spatial
from Settings import UpdateDict
import csv
import pickle


def main():
    #Test1: mesh testing


    MeshPoints = []
    MeshFacets = []
    with open('MeshFacets', 'rb') as input:
        MeshFacets = pickle.load(input)
    with open('MeshPoints', 'rb') as input:
        MeshPoints = pickle.load(input)

    mesh_info = MeshInfo()

    mesh_info.regions.resize(1)
    mesh_info.regions[0] = [
                            MeshPoints[0][0], MeshPoints[0][1], MeshPoints[0][2], # point in volume -> first box
                            0, # region tag (user-defined number)
                            1, # max tet volume in region
                            ]
    print "Building mesh from {} facets and {} points".format(len(MeshFacets), len(MeshPoints))
    try:
        mesh = build(mesh_info, options=Options(switches="pqT", epsilon=0.01), volume_constraints=True)
    except:
        pass
    try:
        mesh = build(mesh_info, options=Options(switches="pqT", epsilon=0.0001), volume_constraints=True)
    except:
        pass
    print "Created mesh with {} points, {} faces and {} elements.".format(len(mesh.points), len(mesh.faces), len(mesh.elements))

def test1():
    #Test1: mesh testing

    acad = Autocad()
    acad.prompt("Hello, Autocad from Python\n")
    print acad.doc.Name

    p1 = APoint(0, 0)
    p2 = APoint(50, 25)
    for i in range(5):
        text = acad.model.AddText('Hi %s!' % i, p1, 2.5)
        acad.model.AddLine(p1, p2)
        acad.model.AddCircle(p1, 10)
        p1.y += 10

    dp = APoint(10, 0)
    for text in acad.iter_objects('Text'):
        print('text: %s at: %s' % (text.TextString, text.InsertionPoint))
        text.InsertionPoint = APoint(text.InsertionPoint) + dp

    for obj in acad.iter_objects(['Circle', 'Line']):
        print(obj.ObjectName)



if __name__ == '__main__':
    #main()
    test1()