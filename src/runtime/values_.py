from dataclasses import dataclass

class ModuleValue:
    def __init__(self, name, env):
        self.name = name
        self.env = env    
    
    def get(self, identifier):
        return self.env.get(identifier)
    
    def __repr__(self):
        return (f"<module {self.name}>")

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

class NothingValue:
    def __init__(self, value=None):
        self.value = value
        if value == None:
            self.value = 'Nothing'

    def __repr__(self):
        return (f"{self.value}")
    
@dataclass
class FunctionValue:
    name: str
    params: any
    body: any
    env: any

    def call(self, interpreter, args):
        # This is similar to visit_FunctionCallNode logic
        call_env = interpreter.env.__class__(self.env)
        call_env.enter_scope()

        old_env = interpreter.env
        interpreter.env = call_env

        # Declare parameters with pre-evaluated argument values
        for param, arg_value in zip(self.params, args):
            param_name = param.params.identifier if hasattr(param, 'params') else param.identifier
            call_env.declare(param_name, arg_value)

        try:
            for stmt in self.body:
                interpreter.visit(stmt)
        except ReturnSignal as r:
            result = r.value
            call_env.exit_scope()
            interpreter.env = old_env
            return result

        call_env.exit_scope()

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value