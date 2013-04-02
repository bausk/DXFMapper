def getFormat(Name):

    def Lira(FormatDict, Semantic, Data):
        if Semantic == 'Compatible Nodes':
            #Compatible nodes
            FormatDict[5].append("{} 1/".format(Data[0]))
            for i in Data[1:] :
                FormatDict[5].append("{}/".format(i))
        if Semantic == 'Nodes':

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
                            "39; /"],
                      1: [],
                      3: [],
                      4: [],
                      5: [],
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