from . import Stmt
from .Environment import Environment
from .Callable import *
from .Lox_Exceptions import ReturnException
from tool import printSst

__all__ = ["LoxFunction"]

class LoxFunction(Callable) : 
    def __init__(self, declaration : Stmt.Function):
        self.declaration = declaration
    
    def call(self, interpreter, args : list) -> object:
        environment = Environment(interpreter.globals)
        for i in range(len(self.declaration.params)) :
            environment.define((self.declaration.params)[i].lexeme, args[i])
        try :
            interpreter.executeBlock(self.declaration.body, environment);
        except ReturnException as returnValue:
            return returnValue._value
        else :
            return None #"nil" is the default return value
    
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        return f"<function {self.declaration.name.lexeme}>"
