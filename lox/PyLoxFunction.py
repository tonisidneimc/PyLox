from . import Stmt
from .Environment import Environment
from .Callable import *
from .PyLoxInstance import *
from .PyLoxExceptions import ReturnException

__all__ = ["PyLoxFunction"]

class PyLoxFunction(Callable) : 
    def __init__(self, declaration : Stmt.Function, closure : Environment, isInitializer : bool):
        self.declaration = declaration
        self.closure = closure
        self._isInitializer = isInitializer
        
    def call(self, interpreter, args : list) -> object:
        #creates a new environment for this function,
        #binding all the callee args to the expected function parameter,
        #then, perform all statements in the function body.
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)) :
            environment.define((self.declaration.params)[i].lexeme, args[i])
        
        try :
            interpreter.executeBlock(self.declaration.body, Environment(environment));
        
        except ReturnException as returnValue:
            if self._isInitializer :
                #allows to return 'this' inside an init method, used with an empty return statement
                return self.closure.getAt(0, "this")
            else : 
                return returnValue._value
        else :
            if self._isInitializer : return self.closure.getAt(0, "this") #an init method can only return 'this' by default
            
            return None #"nil" is the default return value
    
    def bind(self, instance : PyLoxInstance) :
        #bind is used in methods, to allow the "this" references to the instance in which it is bound, 
        #"this" is defined in a nested environment within the original method closure  
        environment = Environment(self.closure)
        environment.define("this", instance)
        return PyLoxFunction(self.declaration, environment, self._isInitializer)
        
    def arity(self) -> int:
        #returns the expected length of the function's parameter list
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        #runtime representation of PyLox function objects
        return "<function {}>".format(self.declaration.name.lexeme)
