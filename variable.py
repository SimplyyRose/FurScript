from enum import Enum

class Modifier(Enum):
    NONE = 0
    OWO = 1
    ONO = 2

class Variable:
    def __init__(self, name, value, modifier):
        self.name = name
        self.value = value
        self.modifier = modifier