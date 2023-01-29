from language import *
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

keyWords = ["twy>", "sniff", "fur", "bop", "mew", "cwass", "constwucter"]

def parse(script, body, contexts=[]):
    parsing = True

    while parsing:
        # Check for if statement
        if body.startswith("cwass"):
            index = findEndingIndex(body, 5)
            substring = body[:index]
            body = body[index:]

            nameEndIndex = substring.find('>')
            name = substring[5:nameEndIndex]
            classBody = substring[nameEndIndex + 1:]

            furClass = FurClass(classBody)
            script.classes[name] = furClass
        elif body.startswith("constwucter"):
            index = findEndingIndex(body, 11)
            substring = body[:index]
            body = body[index:]

            # Parse args and contents
            rightParenIndex = substring.find(')')
            args = splitComma(substring[substring.find('(') + 1:rightParenIndex])
            contents = substring[rightParenIndex + 1:index-3]

            furConstructor = FurConstructor(args, contents)
            context = getContextOfType(contexts, ContextType.CLASS)

            if not context is None:
                context.constructor = furConstructor
        elif body.startswith('sniff'):
            index = findEndingIndex(body, 5)
            substring = body[:index]
            body = body[index:]
                        
            # Parse condition and contents
            rightParenIndex = substring.find(')')
            condition = substring[substring.find('(') + 1:rightParenIndex]
            contents = substring[rightParenIndex + 1:index]

            splitCondition = condition.split('equaws')
            leftSide = typeFromString(script, splitCondition[0], contexts)
            rightSide = typeFromString(script, splitCondition[1], contexts)

            if leftSide == rightSide:
                response = parse(script, contents, contexts)
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
                leftSide = typeFromString(script, splitCondition[0], contexts)
                rightSide = typeFromString(script, splitCondition[1], contexts)

                while leftSide != rightSide:
                    response = parse(script, contents, contexts)
                    if response is not None:
                        return response
                    leftSide = typeFromString(script, condition.split('untiw')[0], contexts)
                    rightSide = typeFromString(script, condition.split('untiw')[1], contexts)
            if 'un' in condition:
                splitCondition = condition.split('un')
                name = splitCondition[0][1:]

                forContext = FurContext(ContextType.FOR)
                forContext.variables[name] = FurVariable(name, None, Modifier.OWO)
                contexts.insert(0, forContext)
                
                items = resolveValue(script, splitCondition[1])

                if type(items) is list:
                    for item in items:
                        forContext.variables[name].value = item
                        response = parse(script, contents, contexts)
                        if response is not None:
                            contexts.pop(0)
                            return response

                # There was no return in the for loop, so pop context here.
                contexts.pop(0)
        elif body.startswith('mew'):
            index = findEndingIndex(body, 3)
            substring = body[:index]
            body = body[index:]

            # Parse args and contents
            rightParenIndex = substring.find(')')
            name = substring[3:rightParenIndex - 1]
            args = substring[substring.find('(') + 1:rightParenIndex]
            contents = substring[rightParenIndex + 1:index-3]

            furMethod = FurMethod(name, args, contents)
            context = getContextOfType(contexts, ContextType.CLASS)

            if context is not None:
                context.methods[name] = furMethod
            else:
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
                response = parse(script, tryContents, contexts)
                if response is not None:
                    return response
            except Exception as e:
                exceptionContext = FurContext(ContextType.EXCEPTION)
                exceptionContext.variables[exceptionVarName] = FurVariable(exceptionVarName, str(e), Modifier.ONO)
                contexts.insert(0, exceptionContext)

                response = parse(script, catchContents, contexts)
                contexts.pop(0)

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
            _parseInstruction(script, substring, contexts)
        else:
            parsing = False
    return None

def resolveValue(script, string, contexts=[]):
    if string.startswith('cweate'):
        leftParenIndex = string.find('(')
        name = string[6:leftParenIndex]
        args = splitComma(string[leftParenIndex + 1:string.find(')')])

        furClass = script.classes[name]
        if type(furClass) is FurClass:
            furObject = FurObject()
            contexts.insert(0, furObject)

            parse(script, furClass.body, contexts)
            print(f'Creating object of class {name} with args {args}')

            # Executes constructor
            constructor = FurContext(ContextType.CONSTRUCTOR)
            if furObject.constructor is not None:
                # TODO: Check for correct number of args
                for index in range(len(args)):
                    varName = furObject.constructor.args[index]
                    varValue = typeFromString(script, args[index], contexts)
                    constructor.variables[varName] = FurVariable(varName, varValue, Modifier.ONO)

                # Insert constructor context, execute constructor, then removes from stack.
                contexts.insert(0, constructor)
                parse(script, furObject.constructor.body, contexts)
                contexts.pop(0)

            return furObject
    elif string[0] != '^':
        return typeFromString(script, string)
    
    variable = getVariable(string, script, contexts)
    if variable is not None:
        return variable
    
    return typeFromString(script, string)

# TODO: Add support for other contexts
def resolveString(script, string, contexts=[]):
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

def typeFromString(script, string, contexts=[]):
    if string == 'None':
        return None

    variable = getVariable(string, script, contexts)
    if variable is not None:
        return variable

    if string.endswith(')'):
        return handleMethod(script, string)
    else:
        string = resolveString(script, string, contexts)

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
def _parseInstruction(script, instruction, contexts=[]):
    modifier = Modifier.NONE

    # Check for modifier
    for mod in Modifier:
        if instruction.startswith(mod.name.lower()):
            modifier = mod

    varReference = instruction.startswith('^') or instruction.startswith('$')

    # Check for variable declaration
    if modifier is not Modifier.NONE or varReference:
        if varReference:
            instruction = instruction[1:]
        else:
            instruction = instruction[len(modifier.name):]
        
        if not 'equaws' in instruction:
            if not varReference:
                createVariable(FurVariable(instruction, None, modifier), script, contexts)
            return

        equawsIndex = instruction.find('equaws')
        name = instruction[:equawsIndex]
        value = instruction[equawsIndex + 6:]
        
        # Parse true type
        value = resolveValue(script, value, contexts)

        # ONO variables cannot have their value modified
        if name in script.variables and script.variables[name].modifier is Modifier.ONO:
            raise Exception("Cannot modify a variable with ONO modifier")

        if varReference:
            variable = getVariable(name, script, contexts, True)
            if variable is not None:
                variable.value = value
        else:
            createVariable(FurVariable(name, value, modifier), script, contexts)
    else:
        handleMethod(script, instruction, contexts)

def handleMethod(script, instruction, contexts=[]):
    # Parse name and args from instruction
    leftParenIndex = instruction.find('(')
    name = instruction[:leftParenIndex]
    argText = instruction[leftParenIndex + 1:instruction.rfind(')')]
    args = []

    if ',' in argText:
        for arg in splitComma(argText):
            args.append(typeFromString(script, arg, contexts))
    else:
        args.append(typeFromString(script, argText, contexts))

    # Check if method exists
    if name in methodMap:
        method = methodMap[name]
        if type(method) is str:
            returnValue = parse(script, method, contexts)
            if returnValue is not None:
                return returnValue
        else:
            return method(script, args)

def splitComma(string):
    result = []
    index = 0
    insideString = False
    insideMethodArgs = False
    insideBrackets = False

    for i in range(len(string)):
        if string[i] == '"':
            insideString = not insideString
        elif string[i] == '(': 
            insideMethodArgs = True
        elif string[i] == ')':
            insideMethodArgs = False
        elif string[i] == '[':
            insideBrackets = True
        elif string[i] == ']':
            insideBrackets = False
        elif string[i] == ',' and not insideString and not insideMethodArgs and not insideBrackets:
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

def getVariable(var, script, contexts=[], forceNonValue=False):
    name = var
    if name[0] == '^' or name[0] == '$':
        name = name[1:]

    # If its a this then check directly against class context
    if name.startswith('dis'):
        name = name[4:]

        for context in contexts:
            if context.type is ContextType.CLASS and name in context.variables:
                if forceNonValue or var.startswith('$'):
                    return context.variables[name]
                elif var.startswith('^'):
                    return context.variables[name].value
        return None

    # Contexts
    for context in contexts:
        if name in context.variables:
            if var.startswith('$'):
                return context.variables[name]
            elif var.startswith('^'):
                    return context.variables[name].value

    # Globals
    if name in script.variables:
        if var.startswith('$'):
            return script.variables[name]
        elif var.startswith('^'):
            return script.variables[name].value

def createVariable(var, script, contexts=[]):
    if len(contexts) > 0:
        context = contexts[0]
        context.variables[var.name] = var
    else:
        script.variables[var.name] = var

def getContextOfType(contexts, type):
    for context in contexts:
        if context.type is type:
            return context
    return None