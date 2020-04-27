from .Token import *
from .LoxExceptions import RunTimeError

__all__ = ["Environment"]

class Environment :
    __slots__ = ["_values", "enclosing"]
    
    #the 'enclosing' field is an enclosing environment,
    #that is None (not defined) if it is the global scope
    def __init__(self, enclosing = None) :
        self._values = {}
        self.enclosing = enclosing
    
    def define(self, name : str, value : object) -> None:
        #binds a new name to a value
        self._values[name] = value
    
    def get(self, name : Token) -> object:
        #looks up the value of the variable 'name'
        #searches for the definition of the variable in the local scope
        if name.lexeme in self._values :
            return self._values[name.lexeme]
        
        #searches for the definition of the variable in the outer blocks 
        if self.enclosing != None : 
            return self.enclosing.get(name)
            
        raise RunTimeError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def getAt(self, distance : int, name : str) :
        environment = self._ancestor(distance)
        return environment._values[name]
    
    def _ancestor(self, dist : int) :
        #gets an outer scope at a 'dist' distance from the current scope
        environment = self
        for i in range(dist) :
            environment = environment.enclosing
            
        return environment
    
    def assign(self, name : Token, value : object) -> None:
        #assign a value to an existing variable,
        #defined in the current or some enclosing scope 
        
        #assign to a local variable
        if name.lexeme in self._values :
            self._values[name.lexeme] = value; return
        
        #assign to a variable defined in an outer block
        try : 
            if self.enclosing != None : 
                self.enclosing.assign(name, value); return
        
        except LoxExceptions : 
            raise
        
        #variable undeclared, not allowed to create a new variable
        raise RunTimeError(name, "Undefined variable '" + name.lexeme + "'.")
   
    def assignAt(self, distance : int, name : Token, value : object) -> None:
        environment = self._ancestor(distance)
        environment._values[name.lexeme] = value; return
         
