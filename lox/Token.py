from .TokenType import *

__all__ = ["Token"]

class Token(object):
    __slots__ = ("lexeme", "line", "literal", "tokenValue")
    
    def __init__(self, token : TokenType, lexeme : str, literal : object, line : int) :
        self.tokenValue = token
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        
    def __str__(self) -> str:
        return str(self.token) + " '" + self.lexeme + "', line: " + str(self.line)

