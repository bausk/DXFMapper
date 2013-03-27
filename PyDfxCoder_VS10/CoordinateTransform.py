from math import *

def GetFormula(TransformFormat, TransformType, Coordinate, Parameters):

    def getVar(Which, Vars):
        return Vars[Parameters[Which]['Mapping']]

    def CylToRectangularX(Vars):
        return (getVar('R', Vars) - Parameters['R']['Origin']) / Parameters['R']['Scale'] * cos((getVar('Theta', Vars) - Parameters['Theta']['Origin']) / Parameters['Theta']['Scale'])
        #return (Variables['R'] - Parameters['R']['Origin']) / Parameters['R']['Scale'] * cos((Variables['Theta'] - Parameters['Theta']['Origin']) / Parameters['Theta']['Scale'])

    def CylToRectangularY(Vars):
        return (getVar('R', Vars) - Parameters['R']['Origin']) / Parameters['R']['Scale'] * sin((getVar('Theta', Vars) - Parameters['Theta']['Origin']) / Parameters['Theta']['Scale'])

    def CylToRectangularZ(Vars):
        return (getVar('Z', Vars) - Parameters['Z']['Origin']) / Parameters['Z']['Scale']
        
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