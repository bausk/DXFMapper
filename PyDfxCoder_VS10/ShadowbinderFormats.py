def getFormat(Name):

    def Lira(FormatDict, Semantic, Data, ExtendedData):
        if Semantic == 'Compatibility':
            if not 5 in ExtendedData: ExtendedData[5] = []
            ExtendedData[5].append("{} 2 3 5 6/".format(Data[0]))
            for i in Data[1:] :
                ExtendedData[5].append("{}/".format(i))
        elif Semantic == 'NodalAxisRotation':
            #Rotated nodes
            #FormatDict[12].append("{} 1/".format(Data[0]))
            for key in Data :
                FormatDict[12].append("{} {} {} {} 0.0/".format(key, *Data[key]))
        elif Semantic == 'Supports':
            #Rotated nodes
            #FormatDict[12].append("{} 1/".format(Data[0]))
            DataMap = {'UX' : 1, 'UY' : 2, 'UZ' : 3, 'RX' : 4, 'RY' : 5, 'RZ' : 6}
            for key in Data :
                DataProcessed = [DataMap[x] for x in Data[key]]
                DataProcessed = ' '.join(str(v) for v in DataProcessed)
                FormatDict[5].append("{} {} /".format(key, DataProcessed))
        elif Semantic == 'Nodes':
            for Key, Point in Data.iteritems() :
                FormatDict[4].append("{} {} {}/".format(Point['point'][0], Point['point'][1], Point['point'][2]))
        elif Semantic == 'Elements':
            for Element in Data :
                #if Element and Element['points'][0] == Element['points'][1]:
                #    print
                if not Element: continue
                ElementStiffness = Element['extended_model_data']['StiffnessMarker']
                if Element and Element['elementclass'] == "LINE_2NODES" :
                    FormatDict[1].append("10 {} {} {}/".format(
                                                               ExtendedData['ElementPropertyIndex'][ElementStiffness],
                                                               Element['points'][0],
                                                               Element['points'][1]
                                                               ))
                elif Element and Element['elementclass'] == "SOLID_8NODES" :
                    FormatDict[1].append("36 {} {} {} {} {}/\n0 0 {} {} {} {}/".format(
                                                                                       ExtendedData['ElementPropertyIndex'][ElementStiffness],
                                                                                       Element['points'][0],
                                                                                       Element['points'][1], 
                                                                                       Element['points'][3], 
                                                                                       Element['points'][2], 
                                                                                       Element['points'][4], 
                                                                                       Element['points'][5], 
                                                                                       Element['points'][7], 
                                                                                       Element['points'][6]
                                                                                       ))
                elif Element and Element['elementclass'] == "SOLID_6NODES" :
                    FormatDict[1].append("33 {} {} {} {} {}/\n0 0 {} {}/".format(
                                                                                 ExtendedData['ElementPropertyIndex'][ElementStiffness],
                                                                                      Element['points'][0],
                                                                                      Element['points'][1], 
                                                                                      Element['points'][2], 
                                                                                      Element['points'][3], 
                                                                                      Element['points'][4], 
                                                                                      Element['points'][5]
                                                                                      ))
        elif Semantic == 'ElementProperties':
            for Key, DataString in Data.iteritems() :
                FormatDict[3].append("{} {}/".format(Key, DataString))
        elif Semantic == 'ElementForce':
            if not 'LoadStringCount' in ExtendedData:
                ExtendedData['LoadStringCount'] = int(FormatDict[7][-1].split(' ', 1)[0]) if len(FormatDict[7]) else 0
            ExtendedData['LoadStringCount'] += 1
            FormatDict[7].append("{} {}/".format(ExtendedData['LoadStringCount'], Data['string']))
            FormatDict[6].append("{} {} {} {} {}/".format(Data['element'], Data['load_id'], Data['direction'], ExtendedData['LoadStringCount'], Data['loadcase']))
            #return False
            #for Key, Elements in Data.iteritems() :
                #FormatDict[4].append("{} {} {}/".format(Elements['point'][0], Elements['point'][1], Elements['point'][2]))

        return True

    def Default(FormatDict, Semantic, Data, ExtendedData):
        return False

    functions = {
        'Lira' : Lira,
        'Default' : Default,
        }

    if Name in functions:
        return functions[Name]
    else:
        return functions['Default']

def initFormat(Name, Semantic):

    def Lira(Semantic):
        if Semantic == "Production":
            FormatDict = {
                          0: [
                              "1; example/ 2; 5/",
                                "28; 0 0 1  0 1 0  1 0 0; /",
                             ],
                          1: [],
                          3: [],
                          4: [],
                          5: [],
                          6: ["1 0 1 1 1"],
                          7: ["1 1 0"],
                          11: [],
                          12: [],
                          }
        if Semantic == "Basic Test":
            FormatDict = {
                          0: ["1; example/ 2; 5/",
                                "28; 0 0 1  0 1 0  1 0 0; /",
                                "33; M 1 CM 100 T 1 C 1 /",
                                "39; 1: DL/"],
                          1: [],
                          3: [],
                          4: [],
                          5: [],
                          6: ["1 0 1 1 1"],
                          7: ["1 1 0"],
                          11: [],
                          12: [],
                          }
        if Semantic == "Advanced Test":
            FormatDict = {
                          0: ["1; example/ 2; 5/",
                                "28; 0 0 1  0 1 0  1 0 0; /",
                                "33; M 1 CM 100 T 1 C 1 /",
                                "39; 1: DL/"],
                          1: [],
                          3: [],
                          4: [],
                          5: [],
                          6: ["1 0 1 1 1 /"],
                          7: ["1 1 0 /"],
                          11: [],
                          12: [],
                          }
        elif Semantic == False:
            FormatDict = {
                          0: [],
                          1: [],
                          3: [],
                          4: [],
                          5: [],
                          6: [],
                          7: [],
                          11: [],
                          12: [],
                          }
        return FormatDict

    def Default():
        return True

    functions = {
        'Lira' : Lira,
        'Default' : Default,
        }

    if Name in functions:
        return functions[Name]
    else:
        return functions['Default']

def writeFormat(Name):

    def Lira(Document, Filename):
        f = open(Filename,'w')
        for DocNumber, Contents in Document.iteritems() :
            f.write('({}/\n{}\n)\n'.format(DocNumber, '\n'.join(Contents)))
        return True

    def Default():
        return True

    functions = {
        'Lira' : Lira,
        'Default' : Default,
        }

    if Name in functions:
        return functions[Name]
    else:
        return functions['Default']