from .Token import *
from .TokenType import *

class Lox_Exceptions(Exception) :
    
    @staticmethod
    def report(line : int, where : str, message : str) -> bool :
        print("[line {0}] Error {1}: {2}".format(line, where, message))
    
    def scanning_error(self, line : int, message : str) : pass
    
    def parse_error(self, token : Token, message : str) : pass
    
    def what(self) : pass

class ScanError(Lox_Exceptions) :
    def __init__(self, line : int, message : str) :
        self._line = line
        self._message = message
    
    def scan_error(self) -> None :
        Lox_Exceptions.report(self._line, "", self._message)
    
    def what(self) :
        return self.scan_error()

class ParseError(Lox_Exceptions) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
    
    def parse_error(self) -> None :
        if self._token.tokenValue == TokenType.EOF :
            Lox_Exceptions.report(self._token.line, " at end", self._message)
        else :
            Lox_Exceptions.report(self._token.line, " at '" + self._token.lexeme + "'", self._message)
        
    def what(self) :
        return self.parse_error()

class CompileError(Lox_Exceptions) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
        
    def compile_error(self) -> None:
        Lox_Exceptions.report(self._token.line, " at '" + self._token.lexeme + "'", self._message)
        
    def what(self) :
        return self.compile_error()

class RunTimeError(RuntimeError, Lox_Exceptions) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
        
    def runtime_error(self) -> None:
        Lox_Exceptions.report(self._token.line, " at '" + self._token.lexeme + "'", self._message)
        
    def what(self) :
        return self.runtime_error()

class ReturnException(Exception) :
    def __init__(self, value : object) :
        self._value = value
