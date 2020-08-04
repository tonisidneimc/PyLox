from .Token import *
from .TokenType import *
from .PyLoxExceptions import PyLoxScanError

__all__ = ["Scanner"]

"""
    The Scanner performs the Lexical Analysis of a text. 
    The character buffer is read and divided into tokens, 
    each corresponding to a symbol in the PyLox language.
"""

class Scanner(object) :
    
    #PyLox reserved keywords
    _keywords = {
        "and"      : TokenType.AND,
        "class"    : TokenType.CLASS,
        "else"     : TokenType.ELSE,
        "false"    : TokenType.FALSE,
        "for"      : TokenType.FOR,
        "fun"      : TokenType.FUN,
        "if"       : TokenType.IF,
        "nil"      : TokenType.NIL,
        "or"       : TokenType.OR,
        "print"    : TokenType.PRINT,
        "return"   : TokenType.RETURN,
        "break"    : TokenType.BREAK,
        "continue" : TokenType.CONTINUE,
        "super"    : TokenType.SUPER,
        "this"     : TokenType.THIS,
        "true"     : TokenType.TRUE,
        "var"      : TokenType.VAR,
        "while"    : TokenType.WHILE
    }
    
    def __init__(self, source : str) :
        self._hadError = False  # defines the error state of Scanner
        self._line = 1          # works as a pointer to the current line in the buffer
        self._start = 0         # works as a pointer to the beginning of a token 
        self._current = 0       # works as a pointer to the end of a token
        self._source = source   # character buffer to be tokenized
        self._tokens = []       # final list of tokens
    
    def Tokenize(self) -> list:
        #breaks the character buffer into a list of tokens
        
        try :
            while not self._isAtEnd() :
                self._scanToken()
        
        except PyLoxScanError as error :
            self._hadError = True
            error.what()        
        else :
            self._start = self._current        
            self._addToken(TokenType.EOF)
        
            return self._tokens
        
    def _scanToken(self) -> None:
        self._skipWhiteSpaces() #ignore white space characters
        
        if self._isAtEnd() : return
        self._start = self._current
        
        #increments _current and returns last consumed token
        character = self._advance()
        
        LexemeToToken = {
            '"'  : (lambda : self._string()),
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
            "%"  : (lambda : self._addToken(TokenType.MOD)),
            "/"  : (lambda : self._addToken(TokenType.SLASH) if not self._matchAny("/", "*") else self._finishComment()),
            "?"  : (lambda : self._addToken(TokenType.QUESTION_MARK)),
            ":"  : (lambda : self._addToken(TokenType.COLON)),
            "!"  : (lambda : self._addToken(TokenType.BANG_EQUAL if self._matchAny("=") else TokenType.BANG)),
            "="  : (lambda : self._addToken(TokenType.EQUAL_EQUAL if self._matchAny("=") else TokenType.EQUAL)),
            "<"  : (lambda : self._addToken(TokenType.LESS_EQUAL if self._matchAny("=") else TokenType.LESS)),
            ">"  : (lambda : self._addToken(TokenType.GREATER_EQUAL if self._matchAny("=") else TokenType.GREATER))
        }
        
        if character in LexemeToToken : 
            return LexemeToToken[character]()
        
        elif str.isdigit(character) : 
            return self._number()
        
        elif self._isalphanum(character) : 
            return self._identifier()
        
        else : 
            raise PyLoxScanError(self._line, "Unexpected character '{}'".format(character))
            
    def _addToken(self, token : TokenType, literal : object = None) -> None :
        #creates a token, with lexeme at _source from _start until _current - 1

        lexeme = self._source[self._start : self._current]
        self._tokens.append(Token(token, lexeme, literal, self._line))
    
    def _string(self) -> None: 
        while self._peek() != '"' and not self._isAtEnd() :
            if self._peek() == "\n" : self._increment_line()
            self._advance()
            
        if self._isAtEnd() :
            raise PyLoxScanError(self._line, "Unterminated String.")
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
        #checks if char is a valid alphanumeric character
        return str.isalnum(char) or char == "_"
     
    def _identifier(self) -> None: 
        while self._isalphanum(self._peek()) :
            self._advance()
        
        text = self._source[self._start : self._current]
        
        if text not in Scanner._keywords :
            self._addToken(TokenType.IDENTIFIER, text)
            
        else : self._addToken(Scanner._keywords[text])
     
    def _isAtEnd(self) -> bool:
        #checks if there is any character still to be processed from the buffer
        return self._current >= len(self._source)
    
    def _incrementLine(self) -> None:
        self._line += 1
    
    def _advance(self, offset : int = 1) -> str:
        #advances the _current pointer in the character buffer
        if self._isAtEnd() : return ""
        
        self._current += offset
        return self._source[self._current - offset]
    
    def _peek(self) -> str:
        #get _current character in the buffer
        
        if self._isAtEnd() : return "\0"
        else : 
            return self._source[self._current]
        
    def _peekNext(self) -> str:
        #get next character after _current in the buffer
        
        if self._current + 1 >= len(self._source) : return "\0"
        else : 
            return self._source[self._current + 1]
    
    def _previous(self) -> str:
        #get the first character before _current, in the buffer
        
        if (self._current - 1) < 0 : return ""
        else : 
            return self._source[self._current - 1]     
    
    def _matchAny(self, *expected : tuple) -> bool :
        #checks and consumes the _current character, 
        #if it matches any of the expected characters
        
        if self._isAtEnd() : return False
        
        for char in expected :
            if self._source[self._current] == char :
                self._current += 1
                return True 
        
        return False
        
    def _finishComment(self) -> None :
        #consumes characters from the buffer until the comment ends
        c = self._previous()
        
        if c == "/" : #single-line comments
            while self._peek() != "\n" and not self._isAtEnd() :
                self._advance()            
        
        elif c == "*" : #multi-line comments
            while not self._isAtEnd() :
                if self._peek() == "*" and self._peekNext() == "/" :
                    self._advance(2)
                    break;
                else :
                    if self._peek() == "\n" : 
                        self._incrementLine()
                    self._advance()
            else :
                raise PyLoxScanError(self._line, "Unterminated Comment.")
        
        else : return
            
    def _skipWhiteSpaces(self) -> None :
    
        while not self._isAtEnd() :
            c = self._peek()
            
            if c not in {" ", "\n", "\r", "\t"} : 
                break 
            elif c == "\n" : 
                self._incrementLine() 
            
            self._advance()
            
