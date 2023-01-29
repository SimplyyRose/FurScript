from enum import Enum

class FurClass:
    def __init__(self, body):
        self.body = body

class FurObject:
    def __init__(self):
        self.methods = {}
        self.variables = {}
        self.type = ContextType.CLASS
        self.constructor: FurConstructor | None = None

    def __str__(self):
        return f'FurObject(methods={self.methods}, variables={self.variables}, type={self.type}, constructor={self.constructor})'

class FurMethod:
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

class FurConstructor:
    def __init__(self, args, body):
        self.args = args
        self.body = body

class Modifier(Enum):
    NONE = 0
    OWO = 1
    ONO = 2

class FurVariable:
    def __init__(self, name, value, modifier):
        self.name = name
        self.value = value
        self.modifier = modifier

    def __str__(self):
        return f'FurVariable(name={self.name}, value={self.value}, modifier={self.modifier})'

class ContextType(Enum):
    CLASS = 0,
    CONSTRUCTOR = 1
    FOR = 2,
    TRY = 3,
    EXCEPTION = 4

class FurContext:
    def __init__(self, type):
        self.type = type
        self.variables = {}
    
    def __str__(self):
        # return 'MyClass(x=' + str(self.x) + ' ,y=' + self.y + ')'
        return f'FurContext(type={self.type}, variables={self.variables})'