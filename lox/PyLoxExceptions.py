from .Token import *
from .TokenType import *

class ReturnException(Exception) :
    def __init__(self, value : object) :
        self._value = value

class LoopControlException(Exception) : pass
class BreakException(LoopControlException) : pass
class ContinueException(LoopControlException) : pass

class PyLoxException(Exception) :

    @staticmethod
    def report(line : int, where : str, message : str) -> None :
        print("[line {}] Error {}: {}".format(line, where, message))
    
    def what(self) : pass

class PyLoxScanError(PyLoxException) :
    def __init__(self, line : int, message : str) :
        self._line = line
        self._message = message
    
    def what(self) -> None:
        return self.report(self._line, "", self._message)

class PyLoxParseError(PyLoxException) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
        
    def what(self) -> None:
        if self._token.tokenValue == TokenType.EOF :
            self.report(self._token.line, "at end", self._message)
        else :
            self.report(self._token.line, "at '{}'".format(self._token.lexeme), self._message)

class PyLoxStaticError(PyLoxException) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
        
    def what(self) :
        return self.report(self._token.line, "at '{}'".format(self._token.lexeme), self._message)

class PyLoxRuntimeError(PyLoxException) :
    def __init__(self, token : Token, message : str) :
        self._token = token
        self._message = message
            
    def what(self) -> None:
        return self.report(self._token.line, "at '{}'".format(self._token.lexeme), self._message)
        
