from time import sleep
import json
import interpreter
import requests

def bark(script, message):
    # TODO: Add support for multiple arguments and special operations
    # Replace all variables with their values
    message = interpreter.resolveString(script, message)

    # Extract string from first and last quote
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1]

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
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1]
    return json.loads(message)

def fetch(script, message):
    message = interpreter.resolveString(script, message)
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1]
    return requests.get(message).text