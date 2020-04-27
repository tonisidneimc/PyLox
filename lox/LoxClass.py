from .Callable import *
from .LoxInstance import *
from .LoxFunction import *

__all__ = ["LoxClass"]

class LoxClass(Callable) :
    def __init__(self, name : str, superclass, methods : dict) :
        self._supercls = superclass
        self._name = name 
        self._methods = methods
    
    def call(self, interpreter, arguments : list) -> LoxInstance:
        #calling a class returns an instance of it
        #if a class constructor method - init - is defined, call it with the specified arguments
        instance = LoxInstance(self)
        
        initializer = self.findMethod("init") #returns a LoxFunction object 
        if initializer is not None :
            #define 'this' in the surrounding scope first, so calls the init method
            initializer.bind(instance).call(interpreter, arguments)
        
        return instance
    
    def findMethod(self, methodName : str) -> LoxFunction:
        #tries to find a method defined inside the current class or in superclass
        if methodName in self._methods : 
            return self._methods[methodName]
        elif self._supercls is not None :
            return self._supercls.findMethod(methodName)
        
        else : return None
        
    def arity(self) -> int:
        #returns the arity of the constructor
        initializer = self.findMethod("init")
        return initializer.arity() if initializer is not None else 0
    
    def __str__(self) :
        #runtime representation of a class in Lox
        return "<class " + self._name + ">"
    
