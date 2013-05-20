from configobj import ConfigObj
from validate import Validator
import collections
from sys import argv

def init():
    return argv

def readSettings(filename):
    v = Validator()
    spec = ConfigObj("Parameters.spec", encoding = "UTF8", list_values=False)
    config = ConfigObj(filename, configspec = spec, encoding = "UTF8")
    config.validate(v)
    return config

def readSettingsKey(Section, Key, settings):
    #This function is obsolete and deprecated
    if Section in settings and Key in settings[Section]:
        return (settings[Section][Key] or False)
    else:
        return False

def GetSections(Type, settings):
    SectionsSet = {}
    for Section in settings:
        if "Type" in settings[Section] and settings[Section]["Type"] == Type:
            SectionsSet[Section] = settings[Section]
    return SectionsSet

def FilterEntities(Entities, FilterName, SettingsDict):
    FilteredEntities = []

    Layer = False
    if 'Layer' in SettingsDict: Layer = SettingsDict['Layer']
    if Layer and not (type(Layer) is list): Layer = [Layer] #prevents from searching for substrings when doing in Layer
    Color = False
    if 'Color' in SettingsDict: Color = SettingsDict['Color']
    if Color and not (type(Color) is list): Color = [Color]
    FilterEntities = False
    if 'Entities' in SettingsDict: FilterEntities = SettingsDict['Entities']
    if FilterEntities and not (type(FilterEntities) is list): FilterEntities = [FilterEntities]
    FilterPoints = False
    if 'Points' in SettingsDict: FilterPoints = [int(x) for x in SettingsDict['Points']]
    if FilterPoints and not (type(FilterPoints) is list): FilterPoints = [FilterPoints]
    FilterClosed = False
    if 'Closed' in SettingsDict: FilterClosed = SettingsDict['Closed']

    for entity in Entities:
#        if entity.dxftype == 'LWPOLYLINE':
#            print
        try:
            if entity.is_closed == True: EntityClosed = 'yes'
            else: EntityClosed = 'no'
        except AttributeError:
            FilterClosed = False
        Condition = (not Layer or entity.layer in Layer) and \
                    (not Color or entity.color in Color) and \
                    (not FilterEntities or entity.dxftype in FilterEntities) and \
                    (not FilterPoints or len(entity.points) in FilterPoints) and \
                    (not FilterClosed or FilterClosed.lower() == EntityClosed)
        if Condition:
            FilteredEntities.append(entity)
    print "Applying filters: {} entities remain in dataset '{}'.".format(len(FilteredEntities), FilterName)
    return FilteredEntities

def UpdateSetting(origin, u):
    d = origin.copy()
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = UpdateSetting(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

def UpdateDict(origin, u):
    d = origin.copy()
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = UpdateSetting(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d