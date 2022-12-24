from time import sleep

def bark(script, message):
    # TODO: Add support for multiple arguments and special operations
    # Replace all variables with their values
    if '^' in message:
        for var in script.variables:
            if var in message:
                message = message.replace('^' + var, str(script.variables[var].value))
        for word in message.split(' '):
            word = word[1:-1]
            if word.startswith('^'):
                message = message.replace(word, "None")

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