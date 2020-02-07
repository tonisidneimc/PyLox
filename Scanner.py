from Token import *
from TokenType import *
from Lox_Exceptions import ScanError

__all__ = ["Scanner"]

class Scanner(object) :
    
    #Lox reserved keywords
    _keywords = {
        "and"    : TokenType.AND,
        "class"  : TokenType.CLASS,
        "else"   : TokenType.ELSE,
        "false"  : TokenType.FALSE,
        "for"    : TokenType.FOR,
        "fun"    : TokenType.FUN,
        "if"     : TokenType.IF,
        "nil"    : TokenType.NIL,
        "or"     : TokenType.OR,
        "print"  : TokenType.PRINT,
        "return" : TokenType.RETURN,
        "super"  : TokenType.SUPER,
        "this"   : TokenType.THIS,
        "true"   : TokenType.TRUE,
        "var"    : TokenType.VAR,
        "while"  : TokenType.WHILE
    }
    
    def __init__(self, source : str) :
        self._hadError = False
        self._line = 1
        self._start = 0
        self._current = 0
        self._source = source
        self._tokens = []
    
    def Tokenize(self) -> list:
        while not self._isAtEnd() :
            try :
                self._start = self._current
                self._scanToken()
            except ScanError as e :
                self._hadError = True
                e.what()
                
        self._start = self._current        
        self._addToken(TokenType.EOF)
        
        return self._tokens
        
    def _scanToken(self) -> None:
        c = self._advance()
        D = {
            " "  : (lambda : None),
            "\r" : (lambda : None),
            "\t" : (lambda : None),
            "\n" : (lambda : self._increment_line()),
            "("  : (lambda : self._addToken(TokenType.LEFT_PAREN)),
            ")"  : (lambda : self._addToken(TokenType.RIGHT_PAREN)),
            "{"  : (lambda : self._addToken(TokenType.LEFT_BRACE)),
            "}"  : (lambda : self._addToken(TokenType.RIGHT_BRACE)),
            ","  : (lambda : self._addToken(TokenType.COMMA)),
            "."  : (lambda : self._addToken(TokenType.DOT)),
            ";"  : (lambda : self._addToken(TokenType.SEMICOLON)),
            "-"  : (lambda : self._addToken(TokenType.MINUS)),
            "+"  : (lambda : self._addToken(TokenType.PLUS)),
            "*"  : (lambda : self._addToken(TokenType.STAR)),
            "/"  : (lambda : self._skipSpaces() if self._match("/", "*") else self._addToken(TokenType.SLASH)),
            "!"  : (lambda : self._addToken(TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG)),
            "="  : (lambda : self._addToken(TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL)),
            "<"  : (lambda : self._addToken(TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS)),
            ">"  : (lambda : self._addToken(TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER)),
            '"'  : (lambda : self._string())
        }
        
        if c in D : 
            D[c]()
        elif str.isdigit(c) : 
            self._number()
        elif self._isalphanum(c) : 
            self._identifier()
        else : 
            raise ScanError(self._line, "Unexpected character '{}'".format(c))
    
    def _addToken(self, token : TokenType, literal : object = None) -> None :
        text = self._source[self._start : self._current]
        self._tokens.append(Token(token, text, literal, self._line))
    
    def _string(self) -> None: 
        while self._peek() != '"' and not self._isAtEnd() :
            if self._peek() == "\n" : self._increment_line()
            self._advance()
            
        if self._isAtEnd() :
            raise ScanError(self._line, "Unterminated String.")
        else :
            self._advance()
            value = self._source[self._start + 1 : self._current - 1]
            self._addToken(TokenType.STRING, value)
            
    def _number(self) -> None :
        while str.isdigit(self._peek()) :
            self._advance()
        if self._peek() == "." and str.isdigit(self._peekNext()) :
            self._advance()
            while str.isdigit(self._peek()) :
                self._advance()
        self._addToken(TokenType.NUMBER, float(self._source[self._start : self._current]))
    
    def _isalphanum(self, char : str) -> bool:
        return str.isalnum(char) or char == "_"
    
    def _identifier(self) -> None: 
        while self._isalphanum(self._peek()) :
            self._advance()
        
        text = self._source[self._start : self._current]
        if text not in Scanner._keywords :
            self._addToken(TokenType.IDENTIFIER, text)
        else : self._addToken(Scanner._keywords[text])
     
    def _isAtEnd(self) -> bool:
        return self._current >= len(self._source)
    
    def _increment_line(self) -> None:
        self._line += 1
    
    def _advance(self, offset : int = 1) -> str:
        self._current += offset
        return self._source[self._current - offset]
    
    def _peek(self) -> str:
        if self._isAtEnd() : return "\0"
        else : return self._source[self._current]
        
    def _peekNext(self) -> str:
        if self._current + 1 >= len(self._source) : return "\0"
        else : return self._source[self._current + 1]
    
    def _previous(self) -> str:
        if (self._current - 1) < 0 : return ""
        return self._source[self._current - 1]     
    
    def _match(self, *expected : tuple) -> bool :
        if self._isAtEnd() : return False
        for char in expected :
            if self._source[self._current] == char :
                self._current += 1
                return True 
        return False
        
    def _skipSpaces(self) -> None :
        if(self._previous() == "/") : #single-line comments
            while self._peek() != "\n" and not self._isAtEnd() :
                self._advance()            
        
        elif(self._previous() == "*") : #multi-line comments
            while not self._isAtEnd() :
                if (self._peek() == "*" and self._peekNext() == "/") :
                    self._advance(2)
                    break;
                else : self._advance()
            else :
                raise ScanError(self._line, "Unterminated Comment.")
