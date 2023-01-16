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
    "fetch": methods.fetch,
    "fetchjson": methods.fetchjson,
    "stash": methods.stash,
    "wandom": methods.wandom,
}

keyWords = ["twy>", "sniff", "fur", "bop", "mew"]

def parse(script, body):
    parsing = True

    while parsing:
        # Check for if statement
        if body.startswith('sniff'):
            index = findEndingIndex(body, 5)
            substring = body[:index]
            body = body[index:]
                        
            # Parse condition and contents
            rightParenIndex = substring.find(')')
            condition = substring[substring.find('(') + 1:rightParenIndex]
            contents = substring[rightParenIndex + 1:index]

            splitCondition = condition.split('equaws')
            leftSide = typeFromString(script, splitCondition[0])
            rightSide = typeFromString(script, splitCondition[1])

            if leftSide == rightSide:
                response = parse(script, contents)
                if response is not None:
                    return response
        elif body.startswith("fur"):
            index = findEndingIndex(body, 3)
            substring = body[:index - 3]
            body = body[index:]

            # Parse condition and contents
            rightParenIndex = substring.find(')')
            condition = substring[substring.find('(') + 1:rightParenIndex]
            contents = substring[rightParenIndex + 1:index]

            # Until for loop
            if 'untiw' in condition:
                splitCondition = condition.split('untiw')
                leftSide = typeFromString(script, splitCondition[0])
                rightSide = typeFromString(script, splitCondition[1])

                while leftSide != rightSide:
                    response = parse(script, contents)
                    if response is not None:
                        return response
                    leftSide = typeFromString(script, condition.split('untiw')[0])
                    rightSide = typeFromString(script, condition.split('untiw')[1])
            if 'un' in condition:
                splitCondition = condition.split('un')
                name = splitCondition[0][1:]
                script.variables[name] = Variable(name, None, Modifier.OWO)
                items = resolveValue(script, splitCondition[1])

                if type(items) is list:
                    for item in items:
                        script.variables[name].value = item
                        response = parse(script, contents)
                        if response is not None:
                            return response
                del script.variables[name]
        elif body.startswith('mew'):
            index = findEndingIndex(body, 3)
            substring = body[:index]
            body = body[index:]

            # Parse args and contents
            rightParenIndex = substring.find(')')
            name = substring[3:rightParenIndex - 1]
            args = substring[substring.find('(') + 1:rightParenIndex]
            contents = substring[rightParenIndex + 1:index]
            methodMap[name] = contents
        elif body.startswith('twy>'):
            index = findEndingIndex(body, 4)
            substring = body[:index]
            body = body[index:]

            catchIndex = substring.find('catch')
            tryContents = substring[4:catchIndex]
            rightParenIndex = substring.find(')')
            catchContents = substring[rightParenIndex + 1:index - 3]
            exceptionVarName = substring[substring.find('(') + 1:rightParenIndex]

            try:
                response = parse(script, tryContents)
                if response is not None:
                    return response
            except Exception as e:
                script.variables[exceptionVarName] = Variable(exceptionVarName, str(e), Modifier.ONO)
                response = parse(script, catchContents)
                del script.variables[exceptionVarName]
                if response is not None:
                    return response
        elif body.startswith('nudges'):
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
        varString = '^' + var
        while varString in string:
            value = script.variables[var].value
            # If value is dict
            if type(value) is dict:
                index = string.find(varString) + len(varString)                
                if len(string) > index and string[index] == '[' and string.find(']', index) != -1:
                    key = string[index + 1:string.find(']', index)]
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
                index = string.find(varString) + len(varString)
                
                if len(string) > index and string[index] == '[' and string.find(']', index) != -1:
                    key = string[index + 1:string.find(']', index)]
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

            if keyWord == 'bop':
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
        return json.loads(string)
    if string.startswith('"{') and string.endswith('}"'):
        string = string[1:-1]
        return json.loads(string)
    elif string.startswith('[') and string.endswith(']'):
        items = string[1:-1].split(',')
        for i in range(len(items)):
            items[i] = typeFromString(script, items[i])
        return items
    elif string.startswith('"') and string.endswith('"'):
        return handleString(string[1:-1])
    elif string == 'True' or string == 'False':
        return string == "True"
    elif string.isnumeric():
        return int(string)
    elif string.endswith('f'):
        return float(string.replace('f', ''))
    elif string.startswith('^'):
        return None
    else:
        return handleString(string)

# Private function to parse a substring
def _parseInstruction(script, instruction):
    modifier = Modifier.NONE

    # Check for modifier
    for mod in Modifier:
        if instruction.startswith(mod.name.lower()):
            modifier = mod

    varReference = instruction.startswith('^')

    # Check for variable declaration
    if modifier is not Modifier.NONE or varReference:
        if varReference:
            instruction = instruction[1:]
        else:
            instruction = instruction[len(modifier.name):]
        equawsIndex = instruction.find('equaws')
        name = instruction[:equawsIndex]
        value = instruction[equawsIndex + 6:]
        
        # Parse true type
        value = resolveValue(script, value)

        # ONO variables cannot have their value modified
        if name in script.variables and script.variables[name].modifier is Modifier.ONO:
            raise Exception("Cannot modify a variable with ONO modifier")
        
        if varReference:
            script.variables[name].value = value
        else:
            script.variables[name] = Variable(name, value, modifier)
    else:
        handleMethod(script, instruction)

def handleMethod(script, instruction):
    # Parse name and args from instruction
    leftParenIndex = instruction.find('(')
    name = instruction[:leftParenIndex]
    argText = instruction[leftParenIndex + 1:instruction.rfind(')')]
    args = []

    if ',' in argText:
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

def handleString(string):
    try:
        return ne.evaluate(string)
    except:
        string = re.sub(r'(?<!\\)"', '', string)
        string = re.sub(r'\\(.)', r'\1', string)
        string = re.sub(r'(?<!\\)\+', '', string)
        return string