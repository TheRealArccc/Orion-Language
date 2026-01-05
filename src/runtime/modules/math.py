import math
from ..values_ import *

def build_math_module():
    def math_sqrt(interpreter, args):
        if len(args) == 1:
            if type(args[0].value) not in (int, float):
                raise Exception(f"math.sqrt() only accepts integers or floats, not {type(args[0])}")
            
            return math.sqrt(args[0].value)
        else:
            raise Exception(f"math.sqrt() only accepts 1 argument ({len(args)} given)")
        
    def math_pi():
        return math.pi
    
    def math_eulers_number():
        return math.e

    return {
        "sqrt": BuiltInFunctionValue("sqrt", math_sqrt),
        "pi": VariableValue(math_pi()),
        "e": VariableValue(math_eulers_number())
    }