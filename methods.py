from time import sleep
import json
import interpreter
import requests
import os

def bark(script, message):
    # TODO: Add support for multiple arguments and special operations
    # Replace all variables with their values
    message = interpreter.resolveString(script, message)

    # Extract string from first and last quote
    message = removeQuotes(message)

    # Print
    print(message)

def paw(script, message):
    args = message.split(',')
    variable = args[0]
    amount = args[1]

    if amount.startswith('^'):
        amount = script.variables[amount[1:]].value

    script.variables[variable[1:]].value += int(amount)

def sweep(script, message):
    value = int(message)
    sleep(value)

def bite(script, message):
    if message.startswith('^'):
        del script.variables[message[1:]]

def pwompt(script, message):
    return input(message)

def pawsejson(script, message):
    message = interpreter.resolveString(script, message)
    message = removeQuotes(message)
    return json.loads(message)

def fetch(script, message):
    message = interpreter.resolveString(script, message)
    if ',' in message:
        args = message.split(',')
        url = removeQuotes(args[0])
        user_agent = removeQuotes(args[1])
        return requests.get(url, headers={'User-Agent': user_agent}).text
    else:
        url = removeQuotes(message)
        return requests.get(url).text

def fetchjson(script, message):
    message = interpreter.resolveString(script, message)
    if ',' in message:
        args = message.split(',')
        url = removeQuotes(args[0])
        user_agent = removeQuotes(args[1])
        return requests.get(url, headers={'User-Agent': user_agent}).json()
    else:
        url = removeQuotes(message)
        return requests.get(url).json()

def stash(script, message):
    message = interpreter.resolveString(script, message)
    args = message.split(',')

    url = removeQuotes(args[0])
    path = removeQuotes(args[1])
    user_agent = None

    if len(args) > 2:
        user_agent = removeQuotes(args[2])

    dir = path[:path.rfind('/')]
    if not os.path.exists(dir):
        os.makedirs(dir)

    # download file from url at path
    with open(path, 'wb') as f:
        if user_agent:
            f.write(requests.get(url, headers={'User-Agent': user_agent}).content)
        else:
            f.write(requests.get(url).content)

def removeQuotes(string):
    if string.startswith('"') and string.endswith('"'):
        return string[1:-1]
    return string