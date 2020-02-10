from Token import *
from TokenType import *
from Lox_Exceptions import ParseError
import Expr

__all__ = ["Parser"]

"""
    This module provides the Parser class, with some methods, 
    to build the Specific Arithmetic Syntax Tree, from a given list of tokens 
    (see the scanner's documentation), to be interpreted by the Interpreter later.
"""

class Parser(object) :
   
    def __init__(self, tokens : list) :
        self._current = 0       # works as a pointer to a token in the token list
        self._tokens = tokens   # the token list to be processed
        self._hadError = False  # defines the error state of Parser
    
    def Parse(self) -> Expr :
        """
            creates and returns a Arithmetic Syntax Tree for the current expression in token list
        """
        try :
            return self._expression()

        except ParseError as error :
            self._hadError = True
            error.what()
            return None 
    
    def _expression(self) -> Expr:
        """
            matches the rule: 
                expression -> equality
        """
        return self._equality()
    
    def _equality(self) -> Expr:
        """
            matches to one of the rules: 
                equality -> comparison ("==" comparison)*
                equality -> comparison ("!=" comparison)*
        """
        expr = self._comparison()
        
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL) :
            operator = self._previous()
            right = self._comparison()
            
            expr = Expr.Binary(expr, operator, right)
            
        return expr
    
    def _comparison(self) -> Expr :
        """
            matches to one of the rules: 
                comparison -> addition ( "<" addition)*
                comparison -> addition ("<=" addition)*
                comparison -> addition ( ">" addition)*
                comparison -> addition (">=" addition)*
        """
        expr = self._addition()
        
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL) :
            operator = self._previous()
            right = self._addition()
            
            expr = Expr.Binary(expr, operator, right)
         
        return expr
    
    def _addition(self) -> Expr :
        """
            matches to one of the rules: 
                addition -> multiplication ("+" multiplication)*
                addition -> multiplication ("-" multiplication)*
        """
        expr = self._multiplication()
        
        while self._match(TokenType.MINUS, TokenType.PLUS) :
            operator = self._previous()
            right = self._multiplication()
            
            expr = Expr.Binary(expr, operator, right)
            
        return expr
            
    def _multiplication(self) -> Expr :
        """
            matches to one of the rules: 
                multiplication -> unary ("*" unary)*
                multiplication -> unary ("/" unary)*
        """
        expr = self._unary()
        
        while self._match(TokenType.STAR, TokenType.SLASH) :
            operator = self._previous()
            right = self._unary()
            
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def _unary(self) -> Expr :
        """
            matches to one of the rules:
                unary -> ("!" unary)*
                unary -> ("-" unary)*  
                unary -> primary
        """
        if self._match(TokenType.BANG, TokenType.MINUS) :
            operator = self._previous()
            right = self._unary()
            
            return Expr.Unary(operator, right)
            
        return self._primary()
     
    def _primary(self) -> Expr :
        """
            matches to one of the rules: 
                primary -> NUMBER
                primary -> STRING
                primary -> "false"
                primary -> "true"
                primary -> "nil"
                primary -> "(" expression ")"
        """
        if self._match(TokenType.FALSE) :
            return Expr.Literal(False)
            
        elif self._match(TokenType.TRUE) :
            return Expr.Literal(True)
            
        elif self._match(TokenType.NIL) :
            return Expr.Literal(None)
            
        elif self._match(TokenType.NUMBER, TokenType.STRING) :
            return Expr.Literal(self._previous().literal)
            
        elif self._match(TokenType.LEFT_PAREN) :
            expr = self._expression()
            try :
                self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expected ')' after expression")
            except ParseError :
                raise
            else :
                return Expr.Grouping(expr)
                
        else : 
            raise ParseError(self._peek(), "Expected expression.")    
    
    def _match(self, *args : TokenType) -> bool:
        """
           checks if there is any token in the args, 
           that matches the _current token in _tokens
        """
        for token in args : 
            if(self._check(token)) :
                self._advance()
                return True
        return False
        
    def _check(self, arg : TokenType) -> bool :
        """
            checks whether the arg token type matches
            the _current token in _tokens, or not
        """
        if self._isAtEnd() : return False
        return self._peek().tokenValue == arg
    
    def _advance(self) -> Token:
        """
            consumes the _current Token in _tokens and returns it
        """
        if not self._isAtEnd() : 
            self._current += 1
        return self._previous()    
    
    def _consume(self, expected : TokenType, errorMessage : str) -> Token: 
        """
            consumes _current token if it matches the expected token, else raise ParseError 
        """
        if self._check(expected):
            return self._advance()
        else :
            raise ParseError(self._peek(), errorMessage)       
        
    def _isAtEnd(self) -> bool :
        """
            checks if EOF is the _current Token in _tokens
        """
        return self._peek().tokenValue == TokenType.EOF
         
    def _peek(self) -> Token :
        """
            returns the _current Token from _tokens
        """
        return self._tokens[self._current]
        
    def _previous(self) -> Token :
        """
            returns the last consumed Token from _tokens
        """
        return self._tokens[self._current - 1]
