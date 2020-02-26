from abc import ABC as Abstract_Class
from abc import abstractmethod

__all__ = ["Callable"]

class Callable(Abstract_Class):
    @abstractmethod
    def arity(self) -> int: 
        pass    
    
    @abstractmethod
    def call(self, interpreter, arguments : list) -> object: 
        pass
    
    @abstractmethod
    def __str__(self) : 
        pass
        
