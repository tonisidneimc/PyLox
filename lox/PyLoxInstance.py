from .Token import *
from .PyLoxExceptions import PyLoxRuntimeError

__all__ = ["PyLoxInstance"]

class PyLoxInstance :
    def __init__(self, klass) :
        self._klass = klass #class declaration
        self._fields = {} #define attributes here
    
    def get(self, name : Token) :
        #return some property of this instance
        if name.lexeme in self._fields :
            #returns an attribute's state
            return self._fields[name.lexeme]
        
        method = self._klass.findMethod(name.lexeme)
        if method is not None :
            #returns a method
            return method.bind(self)    
        
        raise PyLoxRuntimeError(name, "Undefined property '{}'.".format(name.lexeme))
    
    def set(self, name : Token, value : object) :
        #defines the state/value of an instance attribute
        self._fields[name.lexeme] = value; return
    
    def __str__(self) :
        #runtime representation of PyLox class instance objects
        return "<{} instance>".format(self._klass._name)
