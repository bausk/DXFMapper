#Boilerplate code

#Function generator boilerplate
def getFunction(Name):

    def f1():
        return True

    def f2():
        return True

    def Default():
        return True

    functions = {
        'f1' : f1,
        'f2' : f2,
        'Default' : Default,
        }

    if Name in functions:
        return functions[Name]
    else:
        return functions['Default']