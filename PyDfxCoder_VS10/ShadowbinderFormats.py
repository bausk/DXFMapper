def getFormat(Name):

    def Lira(FormatDict, Semantic, Data):
        if Semantic == 'Compatible Nodes':
            #Compatible nodes
            FormatDict[5].append("{} 1/".format(Data[0]))
            for i in Data[1:] :
                FormatDict[5].append("{}/".format(i))
        if Semantic == 'Rotated Nodes':
            #Rotated nodes
            FormatDict[12].append("{} 1/".format(Data[0]))
            for i in Data[1:] :
                FormatDict[5].append("{}/".format(i))
        if Semantic == 'Nodes':
            for Key, Point in Data.iteritems() :
                FormatDict[4].append("{} {} {}/".format(Point['point'][0], Point['point'][1], Point['point'][2]))
        if Semantic == 'Elements':
            for Element in Data :
                if Element and Element['points'][0] == Element['points'][1]:
                    print
                if Element and Element['elementclass'] == "LINE_2NODES" :
                    FormatDict[1].append("10 3 {} {}/".format(Element['points'][0], Element['points'][1]))
                if Element and Element['elementclass'] == "SOLID_8NODES" :
                    FormatDict[1].append("36 1 {} {} {} {}/\n0 0 {} {} {} {}/".format(
                                                                                      Element['points'][0],
                                                                                      Element['points'][1], 
                                                                                      Element['points'][3], 
                                                                                      Element['points'][2], 
                                                                                      Element['points'][4], 
                                                                                      Element['points'][5], 
                                                                                      Element['points'][7], 
                                                                                      Element['points'][6]
                                                                                      ))
        if Semantic == 'Properties':
            return False
            #for Key, Elements in Data.iteritems() :
                #FormatDict[4].append("{} {} {}/".format(Elements['point'][0], Elements['point'][1], Elements['point'][2]))
        if Semantic == 'Loads':
            return False
            #for Key, Elements in Data.iteritems() :
                #FormatDict[4].append("{} {} {}/".format(Elements['point'][0], Elements['point'][1], Elements['point'][2]))

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

def initFormat(Name, Semantic):

    def Lira(Semantic):
        FormatDict = {
                      0: ["1; example/ 2; 5/",
                            "28; 0 0 1  0 1 0  1 0 0; /",
                            "33; M 1 CM 100 T 1 C 1 /",
                            "39; 1: DL/"],
                      1: [],
                      3: ["1 OBI 2.000E+001   0.02 RO      1/",
                          "2 GEI 1.000E+002   0.01    0.2 RO     50/",
                          "3 S0 1.000E+000      2      3/"],
                      4: [],
                      5: [],
                      6: ["1 0 1 1 1"],
                      7: ["1 1 0"],
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