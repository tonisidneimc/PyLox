from .Token import *
from .Lox_Exceptions import RunTimeError

__all__ = ["Environment"]

class Environment :
    __slots__ = ["_values"]
    
    def __init__(self) :
        self._values = {}
    
    def define(self, name : str, value : object) -> None:
        #binds a new name to a value
        self._values[name] = value
    
    def get(self, name : Token) -> object:
        #looks up to the variable's value
        if name.lexeme in self._values :
            return self._values[name.lexeme]
            
        raise RunTimeError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def assign(self, name : Token, value : object) -> None:
        #assign a value to an existing variable
        if name.lexeme in self._values :
            self._values[name.lexeme] = value; return
        
        #not allowed to create a new variable
        raise RunTimeError(name, "Undefined variable '" + name.lexeme + "'.")
