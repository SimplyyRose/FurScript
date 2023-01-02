from time import sleep
import json
import interpreter
import requests
import os
import random

def bark(script, args):
    message = args[0]
    
    if type(message) is str:
        message = interpreter.resolveString(script, message)
    else:
        message = str(message)

    print(message)

def paw(script, args):
    args[0].value += args[1]

def sweep(script, args):
    sleep(args[0])

def bite(script, args):
    del script.variables[args[0].name]

def pwompt(script, args):
    return input(args[0])

def pawsejson(script, args):
    contents = removeQuotes(args[0])
    return json.loads(contents)

def fetch(script, args):
    if len(args) > 1:
        return requests.get(args[0], headers={'User-Agent': args[1]}).text
    else:
        return requests.get(args[0]).text

def fetchjson(script, args):
    if len(args) > 1:
        return requests.get(args[0], headers={'User-Agent': args[1]}).json()
    else:
        return requests.get(args[0]).json()

def stash(script, args):
    url = args[0]
    path = args[1]
    user_agent = None

    if len(args) > 2:
        user_agent = args[2]

    dir = path[:path.rfind('/')]
    if not os.path.exists(dir):
        os.makedirs(dir)

    # download file from url at path
    with open(path, 'wb') as f:
        if user_agent:
            f.write(requests.get(url, headers={'User-Agent': user_agent}).content)
        else:
            f.write(requests.get(url).content)

def wandom(script, args):
    if len(args) == 1:
        return random.randint(1, args[0])
    else:
        return random.randint(args[0], args[1])

def removeQuotes(string):
    if string.startswith('"') and string.endswith('"'):
        return string[1:-1]
    return string