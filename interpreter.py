from variable import Variable
from modifier import Modifier
import re
import methods

methods = {
    "bark": methods.bark,
    "paw": methods.paw,
    "sweep": methods.sweep
}

equaws = "equaws"
untiw = "untiw"

statements = ["sniff", "fur"]

def parse(script, body):
    parsing = True

    while parsing:
        # Check for if statement
        if body.startswith("sniff"):
            index = findEndingIndex(body, 5)
            substring = body[:index]
            body = body[index:]
                        
            # Parse condition and contents
            condition = substring[substring.find('(') + 1:substring.find(')')]
            contents = substring[substring.find(')') + 1:index]

            leftSide = typeFromString(script, condition.split(equaws)[0])
            rightSide = typeFromString(script, condition.split(equaws)[1])   

            if leftSide == rightSide:
                parse(script, contents)
        elif body.startswith("fur"):
            index = findEndingIndex(body, 3)
            substring = body[:index - 3]
            body = body[index:]

            # Parse condition and contents
            condition = substring[substring.find('(') + 1:substring.find(')')]
            contents = substring[substring.find(')') + 1:index]

            leftSide = typeFromString(script, condition.split(untiw)[0])
            rightSide = typeFromString(script, condition.split(untiw)[1])

            while leftSide != rightSide:
                parse(script, contents)
                leftSide = typeFromString(script, condition.split(untiw)[0])
                rightSide = typeFromString(script, condition.split(untiw)[1])
        elif '~' in body:
            # Find the index of first '~' and substring it
            index = body.find('~')
            substring = body[:index]
            body = body[index + 1:]
            _parseInstruction(script, substring)
        else:
            parsing = False

def _resolveString(script, string):
    for var in script.variables:
        if '^' + var in string:
            string = string.replace('^' + var, str(script.variables[var].value))
    return string

def findEndingIndex(body, index):
    openBraces = 1
    endingIndex = index

    while openBraces > 0:
        nextBopIndex = body.find("bop", endingIndex)
        nextFurIndex = body.find("fur", endingIndex)
        nextSniffIndex = body.find("sniff", endingIndex)
        numbers = [nextBopIndex, nextFurIndex, nextSniffIndex]

        # smallest number in numbers
        smallest = min(i for i in numbers if i > 0)

        if smallest == nextBopIndex:
            openBraces -= 1
            endingIndex = smallest + 3
        elif smallest == nextFurIndex:
            openBraces += 1
            endingIndex = smallest + 3
        elif smallest == nextSniffIndex:
            openBraces += 1
            endingIndex = smallest + 5
    return endingIndex

def typeFromString(script, string):
    string = _resolveString(script, string)

    if string.startswith('"') and string.endswith('"'):
        return string[1:-1]
    elif string == "True" or string == "False":
        return string == "True"
    elif string.isnumeric():
        return int(string)
    elif string.endswith('f'):
        return float(string.replace('f', ''))
    elif string.startswith('^'):
        return script.variables[string[1:]].value
    else:
        return string

# Private function to parse a substring
def _parseInstruction(script, instruction):
    modifier = Modifier.NONE

    # Check for modifier
    for mod in Modifier:
        if instruction.startswith(mod.name.lower()):
            modifier = mod

    # Check for variable declaration
    if modifier is not Modifier.NONE:
        instruction = instruction[len(mod.name.lower()):]
        name = instruction[:instruction.find(equaws)]
        value = instruction[instruction.find(equaws) + len(equaws):]
        
        # Parse true type
        value = typeFromString(script, value)

        # ONO variables cannot have their value modified
        if name in script.variables and script.variables[name].modifier is Modifier.ONO:
            raise Exception("Cannot modify a variable with ONO modifier")
        
        script.variables[name] = Variable(name, value, modifier)
    else:
        # Parse name and args from instruction
        name = instruction[:instruction.find('(')]
        args = instruction[instruction.find('(') + 1:instruction.find(')')]

        # Split args by commas that aren't in a string
        #args = re.split(r'",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)"', args)

        # Check if method exists
        if name in methods:
            method = methods[name]
            method(script, args)