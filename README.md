Fun project to experiment with learning language design. <br>

[VSCode Extension](https://github.com/SimplyyRose/FurScriptVSC) for syntax highlighting (WIP).<br>


# Methods
## Bark
**Description:** Prints out a message to the console. <br>
**Args:** Message String
```
bark("Hello World!")~
```

## Paw
**Description:** Plus equals an amount to a int variable. <br>
**Args:** Int variable, Amount Int
```
owo currency equaws 10~
paw(^currency, 5)~

// Prints out 15
bark(^currency)
```

## Sweep
**Description:** Sleeps the main thread. <br>
**Args:** Seconds Int
```
// Sleeps for 5 seconds
sweep(5)~
```

## Bite
**Description:** Unregisters a variable. <br>
**Args:** Variable name
```
// Unregisters the value for 'testValue'
ono testValue equaws 5~
bite(^testValue)~
```

## Pwompt
**Description:** Prompts the user with a question for a response <br>
**Args:** Question String
```
owo name equaws pwompt("Enter your name:")~
bark("Your name is ^name.")~
```

## Pawsejson
**Description:** Parses a JSON string into a object <br>
**Args:** JSON String
```
owo json equaws pawsejson("{"userId": 1, "name": "John"}")~
bark(^json)~
```

## Fetch
**Description:** Issues a web request and returns back a String <br>
**Args:** URL String
```
ono webText equaws fetch("https://jsonplaceholder.typicode.com/todos/1")~
bark(^webText)~
```

## Stash
**Description:** Downloads a file to a path <br>
**Args:** URL String and Path String
```
stash("https://i.imgur.com/NuUoA9Z.jpeg", "./output/forest.jpeg")~
bark("Downloaded forest.jpeg to output dir!")~
```

# Code Examples
## Interpret FurScript code
You can create an empty script and run FurScript code against it.
Run can return a value if a return is hit in the FurScript code. This example would return 10.
```python
from script import Script

code = '''ono newNumber equaws 5+5~\n
nudges ^newNumber~'''

script = Script()
print(str(script.run(code)))
```