from . import Expr
from . import Stmt
from .Token import *
from .TokenType import *
from .LoxExceptions import LoxParseError

__all__ = ["Parser"]

"""
    The Parser performs the Syntax Analysis of a given token list, 
    where it arranges these tokens in a Syntax Tree structure, 
    that reflects the structure of the program.
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
            stmt = self._declaration()
            if stmt is not None : 
                statements.append(stmt)
                
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
            if self._matchAny(TokenType.CLASS) :
                """
                    matches the rule:
                        classDeclaration -> "class" class
                """
                return self._class()
                
            elif self._matchAny(TokenType.FUN) :
                """
                    matches the rule: 
                        funDeclaration -> "fun" function
                """
                return self._function("function")
            
            elif self._matchAny(TokenType.VAR) :
                return self._varDeclaration()
            
            return self._statement()
        
        except LoxParseError as error:
            error.what()
            self._hadError = True
            self._synchronize() #going into panic mode
            return None
    
    def _class(self) -> Stmt:
        """
            matches the rule :
                class -> IDENTIFIER ("<" IDENTIFIER)? "{" function* "}"
        """
        name = self._consume(TokenType.IDENTIFIER, errorMessage = "Expect class name.")
        
        supercls = None
        if self._matchAny(TokenType.LESS) :
            self._consume(TokenType.IDENTIFIER, errorMessage = "Expect superclass name.")
            supercls = Expr.Variable(self._previous())
        
        self._consume(TokenType.LEFT_BRACE, errorMessage = "Expect '{}' before class body.".format('{'))
        
        methods = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._isAtEnd() :
            methods.append(self._function("method"))
        
        self._consume(TokenType.RIGHT_BRACE, errorMessage = "Expect '{}' after class body.".format('}'))
        
        return Stmt.Class(name, supercls, methods)
    
    def _function(self, what : str) -> Stmt: #for functions and class methods
        """
            matches the rule :
                 function -> IDENTIFIER "(" parameters? ")" block
        """
        functionName = self._consume(TokenType.IDENTIFIER, errorMessage = "Expect {} name.".format(what))
        
        self._consume(TokenType.LEFT_PAREN, errorMessage = "Expect '(' after {} name.".format(what))
        
        parametersList = []
        
        if not self._check(TokenType.RIGHT_PAREN) : #otherwise the function has no arguments
            while True:
                #matches the rule: parameters -> IDENTIFIER ("," IDENTIFIER)*
                if len(parametersList) >= 255:
                    LoxParseError(self._peek(), "Functions with more than 255 parameters are not allowed.").what()
                    self._hadError = True
                
                parameter = self._consume(TokenType.IDENTIFIER, errorMessage = "Expect parameter name.")
                parametersList.append(parameter)
                
                if not self._matchAny(TokenType.COMMA) : break            
        
        self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expect ')' after parameter list.")
    
        self._consume(TokenType.LEFT_BRACE, errorMessage = "Expect '{}' before {} body.".format('{', what)) 
        body = self._block() #enclosing brace '}' is consumed by block()
        
        return Stmt.Function(functionName, parametersList, body) 
    
    def _varDeclaration(self) -> Stmt:
        """
            matches the rule :
                varDeclaration -> "var" IDENTIFIER ("=" expression)? ";"
        """
        name = self._consume(TokenType.IDENTIFIER, errorMessage = "Expect variable name.")
        
        initializer = None if not self._matchAny(TokenType.EQUAL) else self._expression()
        
        self._consume(TokenType.SEMICOLON, errorMessage = "Expect ';' after variable declaration.")      
        
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
                statement -> breakStmt
                statement -> continueStmt
                statement -> block
        """
        if self._matchAny(TokenType.IF) :
            return self._ifStmt()
        
        elif self._matchAny(TokenType.FOR) :
            return self._forStmt()
            
        elif self._matchAny(TokenType.PRINT) :
            return self._printStmt()
        
        elif self._matchAny(TokenType.WHILE) :
            return self._whileStmt()
            
        elif self._matchAny(TokenType.RETURN) :
            return self._returnStmt()    
        
        elif self._matchAny(TokenType.BREAK) :
            return self._breakStmt()    
        
        elif self._matchAny(TokenType.CONTINUE) :
            return self._continueStmt()    
        
        elif self._matchAny(TokenType.LEFT_BRACE) :
            return self._block()
            
        return self._exprStmt()
    
    def _ifStmt(self) -> Stmt:
        """
            matches the rule:
                ifStmt -> "if" "(" expression ")" statement ("else" statement)?
        """
        self._consume(TokenType.LEFT_PAREN, errorMessage = "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expect ')' after if condition.")
        
        thenBranch = self._statement()
        elseBranch = self._statement() if self._matchAny(TokenType.ELSE) else None 
        
        return Stmt.If(condition, thenBranch, elseBranch)        
         
    def _exprStmt(self) -> Stmt:
        """
            matches the rule :
                exprStmt -> expression ";"
        """
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, errorMessage = "Expect ';' after expression.")
        
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
        self._consume(TokenType.LEFT_PAREN, errorMessage = "Expect '(' after 'for'.")
            
        #initializer statement is optional
        if self._matchAny(TokenType.SEMICOLON) : initializer = None
        elif self._matchAny(TokenType.VAR) : initializer = self._varDeclaration()
        else : initializer = self._exprStmt()
            
        #condition expression is optional, validates true condition (infinity loop) if no condition is provided
        condition = self._expression() if not self._check(TokenType.SEMICOLON) else Expr.Literal(True)
        self._consume(TokenType.SEMICOLON, errorMessage = "Expect ';' after loop condition.")
            
        #increment expression is optional
        increment = self._expression() if not self._check(TokenType.RIGHT_PAREN) else None
        self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expect ')' after for clauses.")
            
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
    
    def _printStmt(self) -> Stmt:
        """
            matches the rule:
                printStmt -> "print" expression ";"
        """
        value = self._expression()
        self._consume(TokenType.SEMICOLON, errorMessage = "Expect ';' after value.")
        
        return Stmt.Print(value)
    
    def _whileStmt(self) -> Stmt :
        """
            matches the rule:
                whileStmt -> "while" "(" expression ")" statement
        """
        self._consume(TokenType.LEFT_PAREN, errorMessage = "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expect ')' after condition.")
        
        body = self._statement()
        
        return Stmt.While(condition, body)
    
    def _returnStmt(self) -> Stmt:
        """
            matches the rule:
                returnStmt -> "return" expression? ";"
        """
        keyword = self._previous()
        
        value = self._expression() if not self._check(TokenType.SEMICOLON) else None
        
        self._consume(TokenType.SEMICOLON, errorMessage = "Expect ';' after return value.")
        
        return Stmt.Return(keyword, value)
    
    def _breakStmt(self) -> Stmt:
        """
            matches the rule:
                breakStmt -> "break" ";"
        """
        keyword = self._previous()
        
        self._consume(TokenType.SEMICOLON, errorMessage = "Expect ';' after break.")
        
        return Stmt.Break(keyword)
    
    def _continueStmt(self) -> Stmt:
        """
            matches the rule:
                continueStmt -> "continue" ";"
        """
        keyword = self._previous()
        
        self._consume(TokenType.SEMICOLON, errorMessage = "Expect ';' after continue.")
        
        return Stmt.Continue(keyword)
        
    def _block(self) -> Stmt:
        """
            matches the rule:
                block -> "{" declaration* "}"
        """
        statements = []
        
        while not self._check(TokenType.RIGHT_BRACE) and not self._isAtEnd() :
            statements.append(self._declaration())
            
        self._consume(TokenType.RIGHT_BRACE, errorMessage = "Expect '}' after block.")
        
        return Stmt.Block(statements)
        
    def _expression(self) -> Expr:
        """
            matches the rule: 
                expression -> assignment ("," assignment)*
        """
        expr = self._assignment()
        
        while self._matchAny(TokenType.COMMA) :
            operator = self._previous()
            right = self._assignment()
            
            expr = Expr.Chain(expr, operator, right)
        
        return expr
    
    def _assignment(self) -> Expr:
        """
            matches to one of the rules:
                assignment -> ternary
                assignment -> (call ".")? IDENTIFIER "=" assignment
        """
        expr = self._ternary()
        
        if self._matchAny(TokenType.EQUAL) :
            equals = self._previous()
            value = self._assignment()
            
            if isinstance(expr, Expr.Variable) :
                return Expr.Assign(expr.name, value)
                
            elif isinstance(expr, Expr.Get) :
                return Expr.Set(expr.object, expr.name, value)
                    
            else : 
                LoxParseError(equals, "Invalid assignment target.").what()
                self._hadError = True
                 
        return expr
    
    def _ternary(self) -> Expr :
        """
            matches the rule: 
                ternary -> logic_or ("?" expression ":" expression)?
        """
        expr = self._logic_or()
        
        if self._matchAny(TokenType.QUESTION_MARK) :
            operator = self._previous()
            ifTrueValue = self._expression()
            
            self._consume(TokenType.COLON, errorMessage = "Expect ':' in the ternary expression.")
            ifFalseValue = self._expression()
            
            expr = Expr.Ternary(expr, operator, ifTrueValue, ifFalseValue)
                    
        return expr
    
    def _logic_or(self) -> Expr:
        """
            matches the rule:
                logic_or -> logic_and ("or" logic_and)*
        """
        expr = self._logic_and()
        
        while self._matchAny(TokenType.OR) :
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
        
        while self._matchAny(TokenType.AND) :
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
        
        while self._matchAny(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL) :
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
        
        while self._matchAny(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL) :
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
        
        while self._matchAny(TokenType.MINUS, TokenType.PLUS) :
            operator = self._previous()
            right = self._multiplication()
            
            expr = Expr.Binary(expr, operator, right)
            
        return expr
            
    def _multiplication(self) -> Expr :
        """
            matches to one of the rules: 
                multiplication -> unary ("*" unary)*
                multiplication -> unary ("/" unary)*
                multiplication -> unary ("%" unary)*
        """
        expr = self._unary()
        
        while self._matchAny(TokenType.STAR, TokenType.SLASH, TokenType.MOD) :
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
        if self._matchAny(TokenType.BANG, TokenType.MINUS) :
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
            if self._matchAny(TokenType.LEFT_PAREN) : 
                expr = self._finishCall(expr)
            
            elif self._matchAny(TokenType.DOT) :
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
                #validates maximum number of arguments allowed
                if len(arguments) >= 255 : #report it now, don't enter in panic mode
                    LoxParseError(self._peek(), "Expect less than 255 arguments to the function.").what()
                    self._hadError = True
                    
                arguments.append(self._assignment())
                    
                if not self._matchAny(TokenType.COMMA) : break
        
        paren = self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expect ')' after arguments list.")
        
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
                primary -> "super" "." IDENTIFIER
        """
        if self._matchAny(TokenType.FALSE) :
            return Expr.Literal(False)
            
        elif self._matchAny(TokenType.TRUE) :
            return Expr.Literal(True)
            
        elif self._matchAny(TokenType.NIL) :
            return Expr.Literal(None)
            
        elif self._matchAny(TokenType.NUMBER, TokenType.STRING) :
            return Expr.Literal(self._previous().literal)
        
        elif self._matchAny(TokenType.THIS) :
            return Expr.This(self._previous())
        
        elif self._matchAny(TokenType.IDENTIFIER) :
            return Expr.Variable(self._previous())
            
        elif self._matchAny(TokenType.LEFT_PAREN) :
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, errorMessage = "Expect ')' after expression.")
            
            return Expr.Grouping(expr)
        
        elif self._matchAny(TokenType.SUPER) :
            keyword = self._previous()
            self._consume(TokenType.DOT, errorMessage = "Expect '.' after 'super'.")
            
            method = self._consume(TokenType.IDENTIFIER, errorMessage = "Expect superclass method name.")
            
            return Expr.Super(keyword, method)
                        
        else :
            raise LoxParseError(self._peek(), "Expect expression.")    
    
    def _matchAny(self, *args : TokenType) -> bool:
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
        #consumes _current token if it matches the expected token, else raise LoxParseError 
        if self._check(expected):
            return self._advance()
        else :
            raise LoxParseError(self._peek(), errorMessage)       
        
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
        
        beginStatement = {
            TokenType.CLASS,                   
            TokenType.FUN,   
            TokenType.VAR,   
            TokenType.FOR,   
            TokenType.IF,    
            TokenType.WHILE, 
            TokenType.PRINT, 
            TokenType.RETURN 
        }
        
        endStatement = {TokenType.SEMICOLON}
        
        #tries to find a beginning or end of an instruction 
        while not self._isAtEnd() :
            if self._previous().tokenValue in endStatement :
                return
            elif self._peek().tokenValue in beginStatement :
                return
            else : self._advance()

