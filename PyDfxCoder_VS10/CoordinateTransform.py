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

#--------------------------    
    def OrthosphericX(Vars):
        x = getVar('X', Vars) - Parameters['X']['Origin']
        y = getVar('Y', Vars) - Parameters['Y']['Origin']
        z = getVar('Z', Vars) - Parameters['Z']['Origin']
        d = asin(x/sqrt(x**2 + z**2)) * Parameters['D']['Scale']
        g = asin(y/sqrt(y**2 + z**2)) * Parameters['G']['Scale']
        r = sqrt(x**2 + y**2 + z**2) * Parameters['R']['Scale']
        z1 = cos(d) * r / sqrt((cos(d)*tan(g))**2 + 1)
        x1 = z1 * tan(d)
        return x1

    def OrthosphericY(Vars):
        x = getVar('X', Vars) - Parameters['X']['Origin']
        y = getVar('Y', Vars) - Parameters['Y']['Origin']
        z = getVar('Z', Vars) - Parameters['Z']['Origin']
        d = asin(x/sqrt(x**2 + z**2)) * Parameters['D']['Scale']
        g = asin(y/sqrt(y**2 + z**2)) * Parameters['G']['Scale']
        r = sqrt(x**2 + y**2 + z**2) * Parameters['R']['Scale']
        z1 = cos(d) * r / sqrt((cos(d)*tan(g))**2 + 1)
        y1 = z1 * tan(g)
        return y1

    def OrthosphericZ(Vars):
        x = getVar('X', Vars) - Parameters['X']['Origin']
        y = getVar('Y', Vars) - Parameters['Y']['Origin']
        z = getVar('Z', Vars) - Parameters['Z']['Origin']
        d = asin(x/sqrt(x**2 + z**2)) * Parameters['D']['Scale']
        g = asin(y/sqrt(y**2 + z**2)) * Parameters['G']['Scale']
        r = sqrt(x**2 + y**2 + z**2) * Parameters['R']['Scale']
        z1 = cos(d) * r / sqrt((cos(d)*tan(g))**2 + 1)
        return z1
    
        
    functions = {
        'X': {
            'CylindricToRectangular' : CylToRectangularX,
            'Orthospheric' : OrthosphericX,
            },
        'Y': {
            'CylindricToRectangular' : CylToRectangularY,
            'Orthospheric' : OrthosphericY,
            },
        'Z': {
            'CylindricToRectangular' : CylToRectangularZ,
            'Orthospheric' : OrthosphericZ,
            },
        }




    return functions[Coordinate][TransformType]