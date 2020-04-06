from .Token import *
from .TokenType import *

class LoxExceptions(Exception) :
    
    @staticmethod
    def report(line : int, where : str, message : str) -> bool :
        print("[line {0}] Error {1}: {2}".format(line, where, message))
    
    def scanning_error(self, line : int, message : str) : pass
    
    def parse_error(self, token : Token, message : str) : pass
    
    def what(self) : pass

class ScanError(LoxExceptions) :
    def __init__(self, line : int, message : str) :
        self._line = line
        self._message = message
    
    def scan_error(self) -> None :
        LoxExceptions.report(self._line, "", self._message)
    
    def what(self) :
        return self.scan_error()

class ParseError(LoxExceptions) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
    
    def parse_error(self) -> None :
        if self._token.tokenValue == TokenType.EOF :
            LoxExceptions.report(self._token.line, " at end", self._message)
        else :
            LoxExceptions.report(self._token.line, " at '" + self._token.lexeme + "'", self._message)
        
    def what(self) :
        return self.parse_error()

class CompileError(LoxExceptions) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
        
    def compile_error(self) -> None:
        LoxExceptions.report(self._token.line, " at '" + self._token.lexeme + "'", self._message)
        
    def what(self) :
        return self.compile_error()

class RunTimeError(RuntimeError, LoxExceptions) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
        
    def runtime_error(self) -> None:
        LoxExceptions.report(self._token.line, " at '" + self._token.lexeme + "'", self._message)
        
    def what(self) :
        return self.runtime_error()

class ReturnException(Exception) :
    def __init__(self, value : object) :
        self._value = value
