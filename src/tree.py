from dataclasses import dataclass

@dataclass
class ProgramNode:
    body: list

    def __repr__(self):
        return (f"PROGRAM({self.body})")

@dataclass
class BinaryOpNode:
    left: any
    op: any
    right: any
    

    def __repr__(self):
        return (f"({self.left} {self.op.value} {self.right})")

@dataclass
class NothingLiteralNode:
    literal: None

    def __repr__(self):
        return (f"Nothing") if self.literal == None else ("(ERROR_VALUE)")

@dataclass
class LiteralNode:
    literal: any

    def __repr__(self):
        return str(self.literal.value)
    
@dataclass
class UnaryOpNode:
    op: any
    operand: any

    def __repr__(self):
        return (f"{self.op.value}{self.operand}")

@dataclass
class PostfixOpNode: ###
    identifier: str
    op: any

    def __repr__(self):
        return (f"({self.identifier}{self.op.value})")
    
@dataclass
class ArrayNode:
    elements: list

    def __repr__(self):
        return f"ARRAY({self.elements})"
    
@dataclass
class IndexAccessNode:
    array: any
    index: any

    def __repr__(self):
        return f"({self.array}[{self.index}])"
    
@dataclass
class IndexAssignNode:
    array: any
    index: any
    value: any

    def __repr__(self):
        return f"({self.array}[{self.index}] = {self.value})"
    
@dataclass
class VariableNode:
    identifier: str

    def __repr__(self):
        return (f"({self.identifier})")
    
@dataclass
class VarDeclNode:
    identifier: any
    value: any = None

    def __repr__(self):
        return (f"(var {self.identifier} = {self.value})")
    
@dataclass
class AssignNode:
    identifier: any
    value: any

    def __repr__(self):
        return (f"({self.identifier} = {self.value})")
    
@dataclass
class IfNode:
    condition: any
    body: list
    else_body: list = None

    def __repr__(self):
        return (f"(IF {self.condition} THEN \n\t{self.body} \n\tELSE {self.else_body})")

@dataclass
class WhileNode:
    condition: any
    body: list

    def __repr__(self):
        return (f"(WHILE {self.condition} DO {self.body})")

@dataclass
class ForNode:
    init: any
    condition: any
    increment: any
    body: list

    def __repr__(self):
        return (f"(FOR {self.init}; {self.condition}; {self.increment} DO {self.body})")
    
@dataclass
class ParameterNode:
    params: any

    def __repr__(self):
        return f"({self.params})"
    
@dataclass
class ArgumentNode:
    args: any

    def __repr__(self):
        return f"({self.args})"
        
@dataclass
class FunctionDefNode:
    name: str
    params: ParameterNode
    body: any

    def __repr__(self):
        return (f"(FUNCTION {self.name}({self.params}) DO {self.body})")
    
@dataclass
class FunctionCallNode:
    name: str
    args: list

    def __repr__(self):
        return (f"(CALL {self.name.value}({self.args}))")
    
@dataclass
class MethodCallNode:
    object_expr: any
    method_name: any
    args: any

    def __repr__(self):
        return (f"({self.object_expr}.{self.method_name}({self.args}))")
    
@dataclass
class ReturnNode:
    value: any

    def __repr__(self):
        return (f"RETURN {self.value}")