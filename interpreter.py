from variable import Variable, Modifier
import re
import methods
import json
import numexpr as ne

methodMap = {
    "bark": methods.bark,
    "paw": methods.paw,
    "sweep": methods.sweep,
    "bite": methods.bite,
    "pwompt": methods.pwompt,
    "pawsejson": methods.pawsejson,
    "fetch": methods.fetch,
    "fetchjson": methods.fetchjson,
    "stash": methods.stash,
    "wandom": methods.wandom,
}

equaws = "equaws"
untiw = "untiw"
un = "un"

keyWords = ["sniff", "fur", "bop", "mew"]

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
                return parse(script, contents)
        elif body.startswith("fur"):
            index = findEndingIndex(body, 3)
            substring = body[:index - 3]
            body = body[index:]

            # Parse condition and contents
            condition = substring[substring.find('(') + 1:substring.find(')')]
            contents = substring[substring.find(')') + 1:index]

            # Until for loop
            if untiw in condition:
                leftSide = typeFromString(script, condition.split(untiw)[0])
                rightSide = typeFromString(script, condition.split(untiw)[1])

                while leftSide != rightSide:
                    response = parse(script, contents)
                    if response is not None:
                        return response
                    leftSide = typeFromString(script, condition.split(untiw)[0])
                    rightSide = typeFromString(script, condition.split(untiw)[1])
            if un in condition:
                name = condition.split(un)[0][1:]
                script.variables[name] = Variable(name, None, Modifier.OWO)
                items = resolveValue(script, condition.split(un)[1])

                if type(items) is list:
                    for item in items:
                        script.variables[name].value = item
                        return parse(script, contents)
                del script.variables[name]
        elif body.startswith("mew"):
            index = findEndingIndex(body, 3)
            substring = body[:index]
            body = body[index:]

            # Parse args and contents
            name = substring[3:substring.find(')') - 1]
            args = substring[substring.find('(') + 1:substring.find(')')]
            contents = substring[substring.find(')') + 1:index]
            methodMap[name] = contents
        elif body.startswith("nudges"):
            index = body.find('~')
            substring = body[:index]
            body = body[index + 1:]
            return resolveValue(script, substring[6:])
        elif '~' in body:
            # Find the index of first '~' and substring it
            index = body.find('~')
            substring = body[:index]
            body = body[index + 1:]
            _parseInstruction(script, substring)
        else:
            parsing = False
    return None

def resolveValue(script, string):
    if string[0] != '^':
        return typeFromString(script, string)
    for var in script.variables:
        varString = "^" + var
        while varString in string:
            value = script.variables[var].value
            # If value is dict
            if type(value) is dict:
                index = string.find(varString)
                startingPoint = index + len(varString)
                
                if len(string) > startingPoint and string[startingPoint] == '[' and string.find(']', startingPoint) != -1:
                    key = string[startingPoint + 1:string.find(']', startingPoint)]
                    return value[key[1:-1]]
                else:
                    return value
            else:
                return value
    return typeFromString(script, string)

def resolveString(script, string):
    for var in script.variables:
        varString = "^" + var
        while varString in string:
            value = script.variables[var].value
            # If value is dict
            if type(value) is dict:
                index = string.find(varString)
                startingPoint = index + len(varString)
                
                if len(string) > startingPoint and string[startingPoint] == '[' and string.find(']', startingPoint) != -1:
                    key = string[startingPoint + 1:string.find(']', startingPoint)]
                    string = string.replace(varString + '[' + key + ']', str(value[key[1:-1]]))
                else:
                    string = string.replace('^' + var, str(value))
            else:
                string = string.replace('^' + var, str(value))
    return string

def findEndingIndex(body, index):
    openBraces = 1
    endingIndex = index

    while openBraces > 0:
        numbers = [0] * len(keyWords)

        for i in range(len(keyWords)):
            numbers[i] = body.find(keyWords[i], endingIndex)

        smallest = min(i for i in numbers if i > 0)
        for i in range(len(numbers)):
            if numbers[i] != smallest:
                continue

            keyWord = keyWords[i]
            endingIndex = smallest + len(keyWord)

            if keyWord == "bop":
                openBraces -= 1
            else:
                openBraces += 1
    return endingIndex

def typeFromString(script, string):
    if string == 'None':
        return None

    name = string[1:]
    if name in script.variables:
        if string.startswith('$'):
            return script.variables[name]
        elif string.startswith('^'):
            return script.variables[name].value

    if string.endswith(')'):
        return handleMethod(script, string)
    else:
        string = resolveString(script, string)

    if string.startswith('{') and string.endswith('}'):
        print(string)
        return json.loads(string)
    elif string.startswith('[') and string.endswith(']'):
        items = string[1:-1].split(',')
        for i in range(len(items)):
            items[i] = typeFromString(script, items[i])
        return items
    elif string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
        try:
            return ne.evaluate(string)
        except:
            string = re.sub(r'(?<!\\)"', '', string)
            string = re.sub(r'\\(.)', r'\1', string)
            string = re.sub(r'(?<!\\)\+', '', string)
            return string
    elif string == "True" or string == "False":
        return string == "True"
    elif string.isnumeric():
        return int(string)
    elif string.endswith('f'):
        return float(string.replace('f', ''))
    elif string.startswith('^'):
        return None
    else:
        try:
            return ne.evaluate(string)
        except:
            string = re.sub(r'(?<!\\)"', '', string)
            string = re.sub(r'\\(.)', r'\1', string)
            string = re.sub(r'(?<!\\)\+', '', string)
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
        instruction = instruction[len(modifier.name.lower()):]
        name = instruction[:instruction.find(equaws)]
        value = instruction[instruction.find(equaws) + len(equaws):]
        
        # Parse true type
        value = resolveValue(script, value)

        # ONO variables cannot have their value modified
        if name in script.variables and script.variables[name].modifier is Modifier.ONO:
            raise Exception("Cannot modify a variable with ONO modifier")
        
        script.variables[name] = Variable(name, value, modifier)
    elif instruction.startswith("^"):
        instruction = instruction[1:]
        name = instruction[:instruction.find(equaws)]
        value = instruction[instruction.find(equaws) + len(equaws):]
        
        # Parse true type
        value = resolveValue(script, value)

        # ONO variables cannot have their value modified
        if name in script.variables and script.variables[name].modifier is not Modifier.ONO:
            script.variables[name].value = value
    else:
        handleMethod(script, instruction)

def handleMethod(script, instruction):
    # Parse name and args from instruction
    name = instruction[:instruction.find('(')]
    argText = instruction[instruction.find('(') + 1:instruction.rfind(')')]
    args = []

    if argText.count(',') > 0:
        for arg in splitComma(argText):
            args.append(typeFromString(script, arg))
    else:
        args.append(typeFromString(script, argText))

    # Check if method exists
    if name in methodMap:
        method = methodMap[name]
        if type(method) is str:
            returnValue = parse(script, method)
            if returnValue is not None:
                return returnValue
        else:
            return method(script, args)

def splitComma(string):
    result = []
    index = 0
    insideString = False
    insideMethodArgs = False

    for i in range(len(string)):
        if string[i] == '"':
            insideString = not insideString
        elif string[i] == '(': 
            insideMethodArgs = True
        elif string[i] == ')':
            insideMethodArgs = False
        elif string[i] == ',' and not insideString and not insideMethodArgs:
            result.append(string[index:i])
            index = i + 1
    
    result.append(string[index:])
    return result