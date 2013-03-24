from math import *

def GetFormula(TransformFormat, TransformType, Coordinate, Parameters):

    def CylToRectangularX(Variables):
        return (Variables['R'] - Parameters['R']['Origin']) / Parameters['R']['Scale'] * cos((Variables['Theta'] - Parameters['Theta']['Origin']) / Parameters['Theta']['Scale'])

    def CylToRectangularY(Variables):
        return (Variables['R'] - Parameters['R']['Origin']) / Parameters['R']['Scale'] * sin((Variables['Theta'] - Parameters['Theta']['Origin']) / Parameters['Theta']['Scale'])

    def CylToRectangularZ(Variables):
        return (Variables['Z'] - Parameters['Z']['Origin']) / Parameters['Z']['Scale']
        
    functions = {
        'X': {
            'CylindricToRectangular' : CylToRectangularX,
            },
        'Y': {
            'CylindricToRectangular' : CylToRectangularY,
            },
        'Z': {
            'CylindricToRectangular' : CylToRectangularZ,
            },
        }

    return functions[Coordinate][TransformType]