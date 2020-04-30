from abc import ABC as AbstractClass
from abc import abstractmethod

__all__ = ["Callable"]

class Callable(AbstractClass):
    @abstractmethod
    def arity(self) -> int: 
        pass    
    
    @abstractmethod
    def call(self, interpreter, arguments : list) -> object: 
        pass
    
    @abstractmethod
    def __str__(self) : 
        pass
        
