from .Token import *
from .Lox_Exceptions import RunTimeError

__all__ = ["Environment"]

class Environment :
    __slots__ = ["_values", "_enclosing"]
    
    def __init__(self, enclosing = None) :
        self._values = {}
        self._enclosing = enclosing
    
    def define(self, name : str, value : object) -> None:
        #binds a new name to a value
        self._values[name] = value
    
    def get(self, name : Token) -> object:
        #looks up to the variable's value
        
        #searches for the definition of the variable in the local scope
        if name.lexeme in self._values :
            return self._values[name.lexeme]
        
        #searches for the definition of the variable in the outer blocks 
        if self._enclosing != None : 
            return self._enclosing.get(name)
            
        raise RunTimeError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def assign(self, name : Token, value : object) -> None:
        #assign a value to an existing variable
        
        #assign to a local variable
        if name.lexeme in self._values :
            self._values[name.lexeme] = value; return
        
        #assign to a variable defined in an outer block
        if self._enclosing != None : 
            self._enclosing.assign(name, value); return
        
        #not allowed to create a new variable
        raise RunTimeError(name, "Undefined variable '" + name.lexeme + "'.")
