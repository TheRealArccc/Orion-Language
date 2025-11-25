from dataclasses import dataclass

@dataclass
class BuiltInFunctionValue:
    name: any
    func: any

    def call(self, interpreter, args):
        return self.func(interpreter, args)

    def __repr__(self):
        return (f"<builtin {self.name}>")

@dataclass
class IntValue:
    value: int

    def __repr__(self):
        return (f"{self.value}")

@dataclass
class FloatValue:
    value: float

    def __repr__(self):
        return (f"{self.value}")

@dataclass
class StringValue:
    value: float

    def __repr__(self):
        return (f"{self.value}")
    
@dataclass
class BoolValue:
    value: float

    def __repr__(self):
        return (f"{self.value}")
    
@dataclass
class VariableValue:
    value: any
    
@dataclass
class NothingValue:
    value: None

    def __repr__(self):
        return (f"{self.value}")
    
@dataclass
class FunctionValue:
    name: str
    params: any
    body: any
    env: any

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value