from . import Expr
from . import Stmt
from .Token import *
from .TokenType import *
from .LoxExceptions import ParseError

__all__ = ["Parser"]

"""
    This module provides the Parser class, with some methods, 
    to build the specific Statement Syntax Tree, from a given list of tokens,
    (see the scanner's documentation), for each statement that composes the program.
"""

class Parser(object) :
   
    def __init__(self, tokens : list) :
        self._current = 0       # works as a pointer to a token in the token list
        self._tokens = tokens   # the token list to be processed
        self._hadError = False  # defines the error state of Parser
    
    def Parse(self) -> list:
        """
            matches the rule :
                program -> declaration* EOF
        """
        statements = []
        
        while not self._isAtEnd() :
            statements.append(self._declaration())
                
        return statements
    
    def _declaration(self) -> Stmt:
        """
            matches to one of the rules :
                declaration -> classDeclaration
                declaration -> funDeclaration
                declaration -> varDeclaration
                declaration -> statement
        """
        try :
            if self._match(TokenType.CLASS) :
                """
                    matches the rule:
                        classDeclaration -> "class" class
                """
                return self._class()
                
            elif self._match(TokenType.FUN) :
                """
                    matches the rule: 
                        funDeclaration -> "fun" function
                """
                return self._function("function")
            
            elif self._match(TokenType.VAR) :
                return self._varDeclaration()
            
            return self._statement()
        
        except ParseError as error:
            error.what()
            self._hadError = True
            #going into panic mode
            self._synchronize()
            return None
    
    def _class(self) -> Stmt:
        """
            matches the rule :
                class -> IDENTIFIER "{" function* "}"
        """
        name = self._consume(TokenType.IDENTIFIER, errorMessage = "Expect class name.")
        self._consume(TokenType.LEFT_BRACE, errorMessage = "Expect '{'{'}' before class body.")
        
        methods = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._isAtEnd() :
            methods.append(self._function("method"))
        
        self._consume(TokenType.RIGHT_BRACE, errorMessage = "Expect {'}'} after class body.")
        
        return Stmt.Class(name, methods)
    
    def _function(self, what : str) -> Stmt: #for functions and class methods
        """
            matches the rule :
                 function -> IDENTIFIER "(" parameters? ")" block
        """
        functionName = self._consume(TokenType.IDENTIFIER, errorMessage = f"Expected {what} name.")
        
        self._consume(TokenType.LEFT_PAREN, errorMessage = f"Expected '(' after {what} name.")
        
        parametersList = []
        
        if not self._check(TokenType.RIGHT_PAREN) : #otherwise the function has no arguments
            while True:
                #matches the rule: parameters -> IDENTIFIER ("," IDENTIFIER)*
                try :
                    if len(parametersList) >= 255:
                        raise ParseError(self._peek(), "Functions with more than 255 parameters are not allowed.")
                
                except ParseError as error:    
                    error.what()
                else :
                    try :
                        parameter = self._consume(TokenType.IDENTIFIER, errorMessage = "Expected parameter name.")
                    
                    except ParseError as error:
                        error.what()
                    else :
                        parametersList.append(parameter)
                finally :
                    if not self._match(TokenType.COMMA) : break            
        
        self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expected ')' after parameter list.")
    
        self._consume(TokenType.LEFT_BRACE, errorMessage = f"Expected '{'{'}' before {what} body.") 
        body = self._block() #enclosing brace '}' is consumed by block()
        
        return Stmt.Function(functionName, parametersList, body) 
    
    def _varDeclaration(self) -> Stmt:
        """
            matches the rule :
                varDeclaration -> "var" IDENTIFIER ("=" expression)? ";"
        """
        name = self._consume(TokenType.IDENTIFIER, errorMessage = "Expected variable name.")
        
        initializer = None if not self._match(TokenType.EQUAL) else self._expression()
        
        self._consume(TokenType.SEMICOLON, errorMessage = "Expected ';' after variable declaration.")      
        
        return Stmt.Var(name, initializer)
        
    def _statement(self) -> Stmt: 
        """
            matches to one of the rules :
                statement -> exprStmt
                statement -> ifStmt
                statement -> forStmt
                statement -> printStmt
                statement -> whileStmt
                statement -> returnStmt
                statement -> block
        """
        if self._match(TokenType.IF) :
            return self._ifStmt()
        
        elif self._match(TokenType.FOR) :
            return self._forStmt()
            
        elif self._match(TokenType.PRINT) :
            return self._printStmt()
        
        elif self._match(TokenType.WHILE) :
            return self._whileStmt()
            
        elif self._match(TokenType.RETURN) :
            return self._returnStmt()    
        
        elif self._match(TokenType.LEFT_BRACE) :
            return self._block()
            
        return self._exprStmt()
    
    def _ifStmt(self) -> Stmt:
        """
            matches the rule:
                ifStmt -> "if" "(" expression ")" statement ("else" statement)?
        """
        self._consume(TokenType.LEFT_PAREN, errorMessage = "Expected '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expected ')' after if condition.")
        
        thenBranch = self._statement()
        elseBranch = self._statement() if self._match(TokenType.ELSE) else None 
        
        return Stmt.If(condition, thenBranch, elseBranch)        
         
    def _exprStmt(self) -> Stmt:
        """
            matches the rule :
                exprStmt -> expression ";"
        """
        expr = self._expression()
        try :
            self._consume(TokenType.SEMICOLON, errorMessage = "Expected ';' after expression.")
        except ParseError :
            raise
        else :
            return Stmt.Expression(expr)
    
    def _forStmt(self) -> Stmt:
        """
            matches the rule:  
                forStmt -> "for" "(" (varDeclaration | exprStmt | ";") expression? ";" expression? ")" statement
        
            It parses the for loop:
            
                for(initializer; condition; increment) statement;
           
            as a while loop:
            
                {
                   initializer
                       while(condition){
                           statement
                           increment
                       }
                }
        """
        try:
            self._consume(TokenType.LEFT_PAREN, errorMessage = "Expected '(' after 'for'.")
            
            #initializer statement is optional
            if self._match(TokenType.SEMICOLON) : initializer = None
            elif self._match(TokenType.VAR) : initializer = self._varDeclaration()
            else : initializer = self._exprStmt()
            
            #condition expression is optional, validates true condition (infinity loop) if no condition is provided
            condition = self._expression() if not self._check(TokenType.SEMICOLON) else Expr.Literal(True)
            self._consume(TokenType.SEMICOLON, errorMessage = "Expected ';' after loop condition.")
            
            #increment expression is optional
            increment = self._expression() if not self._check(TokenType.RIGHT_PAREN) else None
            self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expected ')' after for clauses.")
            
            statements = [] #list of statements in the while statement body
            
            statements.append(self._statement()) #parses the statement in the for loop body
            if increment is not None : 
                #adds increment expression to the end of the while body
                statements.append(Stmt.Expression(increment))
            
            body = Stmt.Block(statements)
            
            if initializer is None :
                #no initializer is provided, so it parses it as a normal while statement
                return Stmt.While(condition, body)
            else :
                #an initializer is provided, so creates a block with the initializer and the while statements
                return Stmt.Block([initializer, Stmt.While(condition, body)]) 
            
        except ParseError:
            raise
    
    def _printStmt(self) -> Stmt:
        """
            matches the rule:
                printStmt -> "print" expression ";"
        """
        value = self._expression()
        
        try :
            self._consume(TokenType.SEMICOLON, errorMessage = "Expected ';' after value.")
        except ParseError:
            raise
        else :
            return Stmt.Print(value)
    
    def _whileStmt(self) -> Stmt :
        """
            matches the rule:
                whileStmt -> "while" "(" expression ")" statement
        """
        try :
            self._consume(TokenType.LEFT_PAREN, errorMessage = "Expected '(' after 'while'.")
            condition = self._expression()
            self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expected ')' after condition.")
            body = self._statement()
        
        except ParseError:
            raise
        else : 
            return Stmt.While(condition, body)
    
    def _returnStmt(self) -> Stmt:
        """
            matches the rule:
                returnStmt -> "return" expression? ";"
        """
        keyword = self._previous()
        
        value = self._expression() if not self._check(TokenType.SEMICOLON) else None
        
        self._consume(TokenType.SEMICOLON, errorMessage = "Expected ';' after return value.")
        
        return Stmt.Return(keyword, value)
        
    def _block(self) -> Stmt:
        """
            matches the rule:
                block -> "{" declaration* "}"
        """
        statements = []
        
        while not self._check(TokenType.RIGHT_BRACE) and not self._isAtEnd() :
            statements.append(self._declaration())
            
        try :
            self._consume(TokenType.RIGHT_BRACE, errorMessage = "Expected '}' after block.")
        except ParseError :
            raise
        else :
            return Stmt.Block(statements)
        
    def _expression(self) -> Expr:
        """
            matches the rule: 
                expression -> assignment
        """
        return self._assignment()
    
    def _assignment(self) -> Expr:
        """
            matches to one of the rules:
                assignment -> logic_or
                assignment -> (call ".")? IDENTIFIER "=" assignment
        """
        expr = self._logic_or()
        
        if self._match(TokenType.EQUAL) :
            equals = self._previous()
            value = self._assignment()
            
            try :
                if isinstance(expr, Expr.Variable) :
                    return Expr.Assign(expr.name, value)
                
                elif isinstance(expr, Expr.Get) :
                    return Expr.Set(expr.object, expr.name, value)
                    
                raise ParseError(equals, "Invalid assignment target.")
                 
            except ParseError as error:
                error.what()
            
        return expr
    
    def _logic_or(self) -> Expr:
        """
            matches the rule:
                logic_or -> logic_and ("or" logic_and)*
        """
        expr = self._logic_and()
        
        while self._match(TokenType.OR) :
            operator = self._previous()
            right = self._logic_and()
            
            expr = Expr.Logical(expr, operator, right)
        
        return expr
        
    def _logic_and(self) -> Expr:
        """
            matches the rule:
                logic_and -> equality ("and" equality)*
        """
        expr = self._equality()
        
        while self._match(TokenType.AND) :
            operator = self._previous()
            right = self._equality()
            
            expr = Expr.Logical(expr, operator, right)
        
        return expr
            
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
                unary -> call
        """
        if self._match(TokenType.BANG, TokenType.MINUS) :
            operator = self._previous()
            right = self._unary()
            
            return Expr.Unary(operator, right)
            
        return self._call()
        
    def _call(self) -> Expr :
        """
            matches the rule:
                call -> primary ( "(" arguments? ")" | "." IDENTIFIER)*
        """
        expr = self._primary()
        
        #parses an entire function call
        while True :
            if self._match(TokenType.LEFT_PAREN) : 
                expr = self._finishCall(expr)
            
            elif self._match(TokenType.DOT) :
                name = self._consume(TokenType.IDENTIFIER, errorMessage = "Expect property name after '.'.")
                expr = Expr.Get(expr, name)
            else : 
                break    
            
        return expr
    
    def _finishCall(self, callee : Expr) -> Expr :
        #parses an single function call
        #callee is any single expression that can be evaluated to a function
        arguments = []
        
        if not self._check(TokenType.RIGHT_PAREN) :
            while True :
            #parses the remaining arguments in this function call
                try :
                    #validates maximum number of arguments allowed
                    if len(arguments) >= 255 :
                        raise ParseError(self._peek(), "Expected less than 255 arguments to the function.")
                except ParseError as error:
                    error.what() #report it now, don't enter in panic mode 
                else :
                    arguments.append(self._expression())
                    
                    if not self._match(TokenType.COMMA) : break
        
        paren = self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expected ')' after arguments list.")
        
        return Expr.Call(callee, paren, arguments)
        
    def _primary(self) -> Expr :
        """
            matches to one of the rules: 
                primary -> NUMBER
                primary -> STRING
                primary -> "false"
                primary -> "true"
                primary -> "nil"
                primary -> IDENTIFIER
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
        
        elif self._match(TokenType.THIS) :
            return Expr.This(self._previous())
        
        elif self._match(TokenType.IDENTIFIER) :
            return Expr.Variable(self._previous())
            
        elif self._match(TokenType.LEFT_PAREN) :
            expr = self._expression()
            try :
                self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expected ')' after expression.")
            except ParseError :
                raise
            else :
                return Expr.Grouping(expr)
                
        else : 
            raise ParseError(self._peek(), "Expected expression.")    
    
    def _match(self, *args : TokenType) -> bool:
        #checks if there is any token in the args, that matches the _current token in _tokens
        
        for token in args : 
            if(self._check(token)) :
                self._advance()
                return True
        return False
        
    def _check(self, arg : TokenType) -> bool :
        #checks whether the arg token type matches the _current token in _tokens, or not
        
        if self._isAtEnd() : 
            return False
        return self._peek().tokenValue == arg
    
    
    def _advance(self) -> Token:
        #consumes the _current Token in _tokens and returns it
        
        if not self._isAtEnd() : 
            self._current += 1
        return self._previous()    
    
    
    def _consume(self, expected : TokenType, errorMessage : str) -> Token: 
        #consumes _current token if it matches the expected token, else raise ParseError 
        if self._check(expected):
            return self._advance()
        else :
            raise ParseError(self._peek(), errorMessage)       
        
    def _isAtEnd(self) -> bool :
        #checks if EOF is the _current Token in _tokens
        return self._peek().tokenValue == TokenType.EOF
        
         
    def _peek(self) -> Token :
        #returns the _current Token from _tokens
        return self._tokens[self._current]
        
        
    def _previous(self) -> Token :
        #returns the last consumed Token from _tokens
        return self._tokens[self._current - 1]
        
        
    def _synchronize(self) -> None :
        #discard tokens until it finds a statement boundary
        
        _begin_statement = [ 
            TokenType.CLASS,                   
            TokenType.FUN,   
            TokenType.VAR,   
            TokenType.FOR,   
            TokenType.IF,    
            TokenType.WHILE, 
            TokenType.PRINT, 
            TokenType.RETURN 
        ]
        
        _end_statement = [ 
            TokenType.SEMICOLON
        ]
        
        while not self._isAtEnd() :
            if self._previous().tokenValue in _end_statement :
                return
            if self._peek().tokenValue in _begin_statement :
                return
                
            self._advance()
