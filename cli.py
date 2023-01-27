from script import Script

script = Script()

while True:
    code = input(">>> ")
    if code == "exit":
        break
    else:
        value = script.run(code)
        if value is not None:
            print(str(value))