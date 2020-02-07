from Token import *
from TokenType import *

class Lox_Exceptions(Exception) :
    
    @staticmethod
    def report(line : int, where : str, message : str) -> bool :
        print("[line {0}] Error {1}: {2}".format(line, where, message))
    
    def scanning_error(self, line : int, message : str) : pass
    
    def what(self) : pass

class ScanError(Lox_Exceptions) :
    def __init__(self, line : int, message : str) :
        self._line = line
        self._message = message
    
    def scan_error(self) -> None :
        Lox_Exceptions.report(self._line, "", self._message)
    
    def what(self) :
        return self.scan_error()
